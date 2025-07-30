# SPDX-FileCopyrightText: Christian Heinze
#
# SPDX-License-Identifier: Apache-2.0
"""Execute synchronization requests."""

from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import logging
import os
from typing import TYPE_CHECKING, Final, Literal, Protocol, Self, TypedDict, Unpack

_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import AsyncGenerator, Callable, Iterable, Sequence
    from types import TracebackType

    type Parser[T] = Callable[[str], T | None]

    class TrackingContext[T](Protocol):
        async def __aenter__(self) -> Self: ...
        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> bool: ...
        def create_subcontext(
            self, binary: str, *args: str
        ) -> TrackingSubContext[T]: ...

    class TrackingSubContext[T](Protocol):
        async def __aenter__(self) -> Self: ...
        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> bool: ...
        async def log(self, item: T, /) -> None: ...


async def _read_lines(stream: asyncio.StreamReader, /) -> AsyncGenerator[bytes]:
    while not stream.at_eof():
        try:
            line = await stream.readline()
            if not line:
                # Happends only at EOF as linebreaks are included.
                break
            yield line
        except asyncio.CancelledError:
            _LOGGER.info("cancelling line reading generator")
            raise
        except Exception as err:  # noqa: BLE001 # pragma: no cover
            _LOGGER.error(f"error when reading line from '{stream}': {err}")
            break


_DEFAULT_PARSER_QUEUING_TIMEOUT: Final[float] = 5.0


async def _consume_stream[T](
    stream: asyncio.StreamReader,
    parser: Parser[T],
    *,
    queue: asyncio.Queue[T | None],
    encoding: Literal["utf-8"],
    error_handling: Literal["strict", "ignore", "replace"],
) -> None:
    if (
        queueing_timeout := float(
            os.getenv("SYNCD_PARSER_QUEUING_TIMEOUT", _DEFAULT_PARSER_QUEUING_TIMEOUT)
        )
    ) <= 0:  # pragma: no cover
        raise ValueError("non-positive timeout")

    try:
        async for line_bytes in _read_lines(stream):
            try:
                line = line_bytes.decode(encoding, errors=error_handling)
            except UnicodeDecodeError as err:  # pragma: no cover
                _LOGGER.error(
                    f"error when decoding '{line_bytes}' to {encoding}: {err}"
                )
                continue
            try:
                parsed_value = parser(line)
            except Exception as err:  # noqa: BLE001 # pragma: no cover
                _LOGGER.error(f"parsing error when processing line '{line}': {err}")
                continue
            if parsed_value is not None:
                try:
                    await asyncio.wait_for(
                        queue.put(parsed_value), timeout=queueing_timeout
                    )
                except TimeoutError:  # pragma:no cover
                    _LOGGER.error(f"failed to queue '{parsed_value}'")
    except asyncio.CancelledError:
        _LOGGER.info("cancelling stream consumption")
        raise
    except Exception as err:  # noqa: BLE001 # pragma: no cover
        _LOGGER.error(f"error when consuming '{stream}': {err}")
    finally:
        await queue.put(None)


_DEFAULT_PARSER_QUEUE_SIZE: Final[int] = 100
_DEFAULT_PARSER_CLEANUP_TIMEOUT: Final[float] = 5.0


async def _zip_streams[T](
    *streams_and_parsers: tuple[asyncio.StreamReader | None, Parser[T]],
    lookup_timeout: float,
    encoding: Literal["utf-8"] = "utf-8",
    error_handling: Literal["strict", "ignore", "replace"] = "replace",
) -> AsyncGenerator[T]:
    if (
        lookup_timeout <= 0
        or (
            cleanup_timeout := float(
                os.getenv(
                    "SYNCD_PARSER_CLEANUP_TIMEOUT", _DEFAULT_PARSER_CLEANUP_TIMEOUT
                )
            )
        )
        <= 0
    ):  # pragma: no cover
        raise ValueError("non-positive timeout")
    if (
        parser_queue_size := int(
            os.getenv("SYNCD_PARSER_QUEUE_SIZE", _DEFAULT_PARSER_QUEUE_SIZE)
        )
    ) <= 0:  # pragma: no cover
        raise ValueError("non-positive parser queue size")

    active_streams = [
        (stream, parser)
        for (stream, parser) in streams_and_parsers
        if stream is not None
    ]
    if not active_streams:  # pragma: no cover
        return

    # None signals end of stream.
    queue: asyncio.Queue[T | None] = asyncio.Queue(maxsize=parser_queue_size)
    async with asyncio.TaskGroup() as tg:
        for stream, parser in active_streams:
            tg.create_task(
                _consume_stream(
                    stream,
                    parser,
                    queue=queue,
                    encoding=encoding,
                    error_handling=error_handling,
                ),
                name=f"consuming-{stream}",
            )

        active_readers = len(active_streams)
        try:
            while active_readers > 0:
                try:
                    result = await asyncio.wait_for(queue.get(), timeout=lookup_timeout)
                    queue.task_done()
                    if result is None:
                        active_readers -= 1
                        continue

                    yield result
                except asyncio.CancelledError:
                    _LOGGER.info("cancelling multi-stream consumption")
                    raise
                except TimeoutError:
                    if all(stream.at_eof() for stream, _ in active_streams):
                        break
                    continue
        finally:
            while not queue.empty():
                try:
                    queue.get_nowait()
                    queue.task_done()
                except asyncio.QueueEmpty:  # pragma: no cover
                    break
            try:
                await asyncio.wait_for(queue.join(), timeout=cleanup_timeout)
            except TimeoutError:  # pragma: no cover
                _LOGGER.error("parser queue join timed out during cleanup")


_DEFAULT_TERMINATE_TIMEOUT: Final[float] = 5.0
_DEFAULT_KILL_TIMEOUT: Final[float] = 2.0


async def _terminate_process(
    proc: asyncio.subprocess.Process,
) -> None:
    if proc.returncode is not None:  # pragma: no cover
        return

    terminate_timeout = float(
        os.getenv("SYNCD_RSYNC_TERMINATE_TIMEOUT", _DEFAULT_TERMINATE_TIMEOUT)
    )
    kill_timeout = float(os.getenv("SYNCD_RSYNC_KILL_TIMEOUT", _DEFAULT_KILL_TIMEOUT))
    if terminate_timeout <= 0 or kill_timeout <= 0:  # pragma: no cover
        raise ValueError("non-positive timeouts")

    with contextlib.suppress(ProcessLookupError):
        proc.terminate()
        with contextlib.suppress(TimeoutError):
            _LOGGER.info(f"waiting for '{proc}' after SIGTERM")
            await asyncio.wait_for(proc.wait(), timeout=terminate_timeout)
            return

        proc.kill()
        with contextlib.suppress(TimeoutError):
            _LOGGER.warning(f"waiting for '{proc}' after SIGKILL")
            await asyncio.wait_for(proc.wait(), timeout=kill_timeout)
            return
        _LOGGER.error(f"Process {proc.pid} did not respond to SIGKILL")


class OutputParsing[T](TypedDict):
    lookup_timeout: float
    parser_stdout: Parser[T]
    parser_stderr: Parser[T]


async def _run_one[T](
    binary: str,
    *args: str,
    semaphore: asyncio.Semaphore,
    tracking_context: TrackingContext[T],
    **parsing: Unpack[OutputParsing[T]],
) -> int:
    proc: asyncio.subprocess.Process | None = None
    try:
        # Semaphore covers everything to enforce waiting
        # for the entire sync to complete.
        async with semaphore:
            proc = await asyncio.create_subprocess_exec(
                binary,
                *args,
                # Explicitly closing stdin.
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            async with tracking_context.create_subcontext(
                binary, *args
            ) as logging_subcontext:
                async for out in _zip_streams(
                    (proc.stdout, parsing["parser_stdout"]),
                    (proc.stderr, parsing["parser_stderr"]),
                    lookup_timeout=parsing["lookup_timeout"],
                ):
                    await logging_subcontext.log(out)

                await proc.communicate()

            assert proc.returncode is not None, "unterminated process detected"
            return proc.returncode
    except asyncio.CancelledError:
        if proc is not None:
            await _terminate_process(proc)
        raise
    except Exception as err:
        if proc is not None:
            await _terminate_process(proc)

        cmd = " ".join((binary, *args))
        raise RuntimeError(f"exception while awaiting '{cmd}'") from err


async def run[T](
    commands: Iterable[tuple[str, Sequence[str]]],
    *,
    max_processes: int,
    tracking_context: TrackingContext[T],
    **parsing: Unpack[OutputParsing[T]],
) -> None:
    if max_processes <= 0:  # pragma: no cover
        raise ValueError("non-positive process limit")
    semaphore = asyncio.Semaphore(max_processes)
    try:
        async with tracking_context, asyncio.TaskGroup() as task_group:
            for binary, args in commands:
                task_group.create_task(
                    _run_one(
                        binary,
                        *args,
                        semaphore=semaphore,
                        tracking_context=tracking_context,
                        **parsing,
                    )
                )
    except* Exception as group:
        for err in group.exceptions:
            if not isinstance(err, asyncio.CancelledError):
                _LOGGER.error(f"task failed: {err}")
        raise


@dataclasses.dataclass(slots=True)
class _MultiTrackingState:
    stack: contextlib.AsyncExitStack


@dataclasses.dataclass(slots=True)
class RunMultiTracking[T]:
    trackers: tuple[TrackingContext[T], ...]

    _state: _MultiTrackingState | None = dataclasses.field(default=None, init=False)

    async def __aenter__(self) -> Self:
        stack = await contextlib.AsyncExitStack().__aenter__()
        for tracker in self.trackers:
            await stack.enter_async_context(tracker)
        self._state = _MultiTrackingState(stack=stack)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:
        if self._state is None:  # pragma: no cover
            raise RuntimeError("context not available")

        await self._state.stack.__aexit__(exc_type, exc, tb)
        return False

    def create_subcontext(self, binary: str, *args: str) -> _TaskMultiTracking[T]:
        return _TaskMultiTracking(
            trackers=tuple(
                tracker.create_subcontext(binary, *args) for tracker in self.trackers
            ),
        )


@dataclasses.dataclass(slots=True)
class _TaskMultiTracking[T]:
    trackers: tuple[TrackingSubContext[T], ...]

    _state: _MultiTrackingState | None = dataclasses.field(default=None, init=False)

    async def __aenter__(self) -> Self:
        stack = await contextlib.AsyncExitStack().__aenter__()
        for tracker in self.trackers:
            await stack.enter_async_context(tracker)
        self._state = _MultiTrackingState(stack=stack)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        if self._state is None:  # pragma: no cover
            raise RuntimeError("context not available")

        await self._state.stack.__aexit__(exc_type, exc, tb)
        return False

    async def log(self, item: T, /) -> None:
        for tracker in self.trackers:
            await tracker.log(item)
