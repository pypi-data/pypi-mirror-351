#
# Copyright (c) 2025, NVIDIA CORPORATION. All rights reserved.
#

from requests.exceptions import ChunkedEncodingError, ConnectionError, ReadTimeout
from urllib3.exceptions import ProtocolError, ReadTimeoutError
from io import BufferedIOBase, BufferedWriter
from typing import Optional
from overrides import override
from aistore.sdk.obj.content_iterator import ContentIterator
from aistore.sdk.utils import get_logger
from aistore.sdk.obj.obj_file.utils import (
    handle_broken_stream,
    compute_loop_size,
)

logger = get_logger(__name__)


class ObjectFileReader(BufferedIOBase):
    """
    A sequential read-only file-like object extending `BufferedIOBase` for reading object data, with support for both
    reading a fixed size of data and reading until the end of file (EOF).

    When a read is requested, any remaining data from a previously fetched chunk is returned first. If the remaining
    data is insufficient to satisfy the request, the `read()` method fetches additional chunks from the provided
    `content_iterator` as needed, until the requested size is fulfilled or the end of the stream is reached.

    In case of unexpected stream interruptions (e.g. `ChunkedEncodingError`, `ConnectionError`) or timeouts (e.g.
    `ReadTimeout`), the `read()` method automatically retries and resumes fetching data from the last successfully
    retrieved chunk. The `max_resume` parameter controls how many retry attempts are made before an error is raised.

    Args:
        content_iterator (ContentIterator): An iterator that can fetch object data from AIS in chunks.
        max_resume (int): Maximum number of resumes allowed for an ObjectFileReader instance.
    """

    def __init__(self, content_iterator: ContentIterator, max_resume: int):
        self._content_iterator = content_iterator
        self._max_resume = max_resume  # Maximum number of resume attempts allowed
        self._reset()

    def _reset(self, retain_resumes: bool = False) -> None:
        self._iterable = self._content_iterator.iter()
        self._remainder = None
        self._resume_position = 0
        self._closed = False
        if not retain_resumes:
            self._resume_total = 0

    @property
    def content_iterator(self) -> ContentIterator:
        """Return the content iterator."""
        return self._content_iterator

    @override
    def __enter__(self):
        self._reset()
        return self

    @override
    def readable(self) -> bool:
        """Return whether the file is readable."""
        return not self._closed

    @override
    def read(self, size: Optional[int] = -1) -> bytes:
        """
        Read up to 'size' bytes from the object. If size is -1, read until the end of the stream.

        Args:
            size (int, optional): The number of bytes to read. If -1, reads until EOF.

        Returns:
            bytes: The read data as a bytes object.

        Raises:
            ObjectFileReaderStreamError: If a connection cannot be made.
            ObjectFileReaderMaxResumeError: If the stream is interrupted more than the allowed maximum.
            ValueError: I/O operation on a closed file.
            Exception: Any other errors while streaming and reading.
        """
        if self._closed:
            raise ValueError("I/O operation on closed file.")
        if size == 0:
            return b""
        if size is None:
            size = -1

        # Cache original requested size in case of reset
        original_size = size

        size = compute_loop_size(size)
        result = []

        try:
            # Consume any remaining data from a previous chunk before fetching new data
            if self._remainder:
                if size < len(self._remainder):
                    result.append(self._remainder[:size])
                    self._remainder = self._remainder[size:]
                    size = 0
                else:
                    result.append(self._remainder)
                    size -= len(self._remainder)
                    self._remainder = None

            # Fetch new chunks from the stream as needed
            while size:
                try:
                    chunk = memoryview(next(self._iterable))
                except (
                    ConnectionError,
                    ChunkedEncodingError,
                    ProtocolError,
                    ReadTimeout,
                    ReadTimeoutError,
                ) as err:
                    # If the stream is broken (e.g. TCP reset, dropped connection, malformed or incomplete chunk)
                    # or there is a timeout, retry with a new iterator from the last known position
                    self._iterable, self._resume_total = handle_broken_stream(
                        self._content_iterator,
                        self._resume_position,
                        self._resume_total,
                        self._max_resume,
                        err,
                    )

                    # If the object is remote and not cached, reset the iterator and restart the read operation
                    # to avoid timeouts when streaming non-cached remote objects with byte ranges (must wait for
                    # entire object to be cached in-cluster).
                    if not self._iterable:
                        self._reset(retain_resumes=True)
                        size = compute_loop_size(original_size)

                    continue

                except StopIteration:
                    # End of stream, exit loop
                    break

                # Track the position of the stream by adding the length of each fetched chunk
                self._resume_position += len(chunk)

                # Add the part of the chunk that fits within the requested size and
                # store any leftover data for the next read
                if size < len(chunk):
                    result.append(chunk[:size])
                    self._remainder = chunk[size:]
                    size = 0
                else:
                    result.append(chunk)
                    self._remainder = None
                    size -= len(chunk)

        except Exception as err:
            obj_path = self.content_iterator.client.path
            # Handle any unexpected errors, log them with context, close the file, and re-raise
            logger.error(
                "Error while reading object at '%s': %s. Closing file.",
                obj_path,
                err,
                exc_info=True,
            )
            self.close()
            raise err

        # Assemble the final bytes object with a single data copy
        return b"".join(result)

    @override
    def close(self) -> None:
        """Close the file."""
        self._closed = True


class ObjectFileWriter(BufferedWriter):
    """
    A file-like writer object for AIStore, extending `BufferedWriter`.

    Args:
        obj_writer (ObjectWriter): The ObjectWriter instance for handling write operations.
        mode (str): Specifies the mode in which the file is opened.
            - `'w'`: Write mode. Opens the object for writing, truncating any existing content.
                     Writing starts from the beginning of the object.
            - `'a'`: Append mode. Opens the object for appending. Existing content is preserved,
                     and writing starts from the end of the object.
    """

    def __init__(self, obj_writer: "ObjectWriter", mode: str):
        self._obj_writer = obj_writer
        self._mode = mode
        self._handle = ""
        self._closed = False
        if self._mode == "w":
            self._obj_writer.put_content(b"")

    @override
    def __enter__(self, *args, **kwargs):
        if self._mode == "w":
            self._obj_writer.put_content(b"")
        return self

    @override
    def write(self, buffer: bytes) -> int:
        """
        Write data to the object.

        Args:
            data (bytes): The data to write.

        Returns:
            int: Number of bytes written.

        Raises:
            ValueError: I/O operation on a closed file.
        """
        if self._closed:
            raise ValueError("I/O operation on closed file.")

        self._handle = self._obj_writer.append_content(buffer, handle=self._handle)

        return len(buffer)

    @override
    def flush(self) -> None:
        """
        Flush the writer, ensuring the object is finalized.

        This does not close the writer but makes the current state accessible.

        Raises:
            ValueError: I/O operation on a closed file.
        """
        if self._closed:
            raise ValueError("I/O operation on closed file.")

        if self._handle:
            # Finalize the current state with flush
            self._obj_writer.append_content(
                content=b"", handle=self._handle, flush=True
            )
            # Reset the handle to prepare for further appends
            self._handle = ""

    @override
    def close(self) -> None:
        """
        Close the writer and finalize the object.
        """
        if not self._closed:
            # Flush the data before closing
            self.flush()
            self._closed = True
