# SPDX-FileCopyrightText: Christian Heinze
#
# SPDX-License-Identifier: Apache-2.0
"""Progress tracking."""

from __future__ import annotations

import asyncio
import collections
import contextlib
import dataclasses
import enum
import itertools
import logging
import os
import shutil
import time
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Concatenate,
    Final,
    Literal,
    Self,
    TypedDict,
)

import aiosqlite
import pydantic
import rich.highlighter
import rich.progress
import rich.table

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import (
        AsyncGenerator,
        Callable,
        Coroutine,
        Iterable,
    )
    from types import TracebackType

_LOGGER: Final[logging.Logger] = logging.getLogger()


class RsyncAction(str, enum.Enum):
    DELETE = "*"
    CREATE = "c"
    COPY = ">"

    def __str__(self) -> str:
        return self.name.lower()


def _extract_first_letter(data: Any) -> Any:
    if isinstance(data, str):
        return data[:1]
    return data


@pydantic.with_config(pydantic.ConfigDict(extra="forbid"))
class RsyncTransaction(TypedDict):
    filename: str  # Relative to the destination.
    transfer_bytes: int
    action: Annotated[RsyncAction, pydantic.BeforeValidator(_extract_first_letter)]


RSYNC_OUTFORMAT: Final[str] = '{"filename": "%n", "transfer_bytes": %b, "action": "%i"}'
_TRANSACTION_VALIDATOR: Final[pydantic.TypeAdapter] = pydantic.TypeAdapter(
    RsyncTransaction
)


def parse_stdout(text: str, /) -> RsyncTransaction | None:
    if not (stripped_text := text.strip()):
        return None
    try:
        return _TRANSACTION_VALIDATOR.validate_json(stripped_text)
    except pydantic.ValidationError:
        return None


_DBSETUP: Final[str] = """
CREATE TABLE runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TEXT NOT NULL ON CONFLICT FAIL DEFAULT CURRENT_TIMESTAMP,
    version TEXT NOT NULL ON CONFLICT FAIL,
    conf TEXT NOT NULL ON CONFLICT FAIL,
    run TEXT NOT NULL ON CONFLICT FAIL
) STRICT;
CREATE INDEX idx_runs_created ON runs(created);

CREATE TABLE tasks (
    runid INTEGER NOT NULL ON CONFLICT FAIL REFERENCES runs (id) ON DELETE CASCADE,
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dest TEXT NOT NULL ON CONFLICT FAIL
) STRICT;
CREATE INDEX idx_tasks_runid ON tasks(runid);

CREATE TABLE transactions (
    taskid INTEGER NOT NULL ON CONFLICT FAIL REFERENCES tasks (id) ON DELETE CASCADE,
    filename TEXT NOT NULL ON CONFLICT FAIL,
    action TEXT NOT NULL ON CONFLICT FAIL,
    transfer_bytes INT NOT NULL ON CONFLICT FAIL
) STRICT;
CREATE INDEX idx_transactions_taskid ON transactions(taskid);
CREATE INDEX idx_transactions_action ON transactions(action);
"""


@dataclasses.dataclass(slots=True)
class _GuardedConnection:
    _connection: aiosqlite.Connection
    _lock: asyncio.Lock = dataclasses.field(default_factory=asyncio.Lock, init=False)

    async def execute[**P, T](
        self,
        func: Callable[Concatenate[aiosqlite.Connection, P], Coroutine[Any, Any, T]],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        async with self._lock:
            return await func(self._connection, *args, **kwargs)


@contextlib.asynccontextmanager
async def _autocommit(
    con: aiosqlite.Connection,
) -> AsyncGenerator[aiosqlite.Connection]:
    try:
        yield con
    except BaseException as err:
        await con.rollback()
        _LOGGER.warning(f"transactions rolled back due to {err}")
        raise
    await con.commit()


async def _log_run(
    conn: aiosqlite.Connection, /, *, version: str, conf_json: str, run_json: str
) -> int:
    async with _autocommit(conn):
        last_inserted_row = await conn.execute_insert(
            "INSERT INTO runs (version, conf, run) VALUES (:version, :conf, :run);",
            {"version": version, "conf": conf_json, "run": run_json},
        )
    assert last_inserted_row, "row ID unavailable"
    return last_inserted_row[0]


async def _log_task(conn: aiosqlite.Connection, /, *, runid: int, dest: str) -> int:
    async with _autocommit(conn):
        last_inserted_row = await conn.execute_insert(
            "INSERT INTO tasks (runid, dest) VALUES (:runid, :dest);",
            {"runid": runid, "dest": dest},
        )
    assert last_inserted_row, "row ID unavailable"
    return last_inserted_row[0]


async def _log_transactions(
    conn: aiosqlite.Connection,
    /,
    *,
    taskid: int,
    transactions: Iterable[RsyncTransaction],
) -> None:
    if not transactions:  # pragma: no cover
        return

    params = [
        (taskid, tact["filename"], tact["action"], tact["transfer_bytes"])
        for tact in transactions
    ]
    async with _autocommit(conn):
        # Positional matching is supposed to be faster.
        await conn.executemany(
            "INSERT INTO transactions (taskid, filename, action, transfer_bytes)"
            " VALUES (?, ?, ?, ?);",
            params,
        )


@dataclasses.dataclass(slots=True, kw_only=True)
class _SqliteRunTrackingState:
    context: contextlib.AsyncExitStack
    connection: _GuardedConnection
    task_group: asyncio.TaskGroup
    runid: int


@dataclasses.dataclass(slots=True, kw_only=True)
class SqliteRunTracking:
    file: Path
    version: str
    conf_json: str
    run_json: str

    _state: _SqliteRunTrackingState | None = dataclasses.field(default=None, init=False)

    async def __aenter__(self) -> Self:
        # File will be created upon conection if not yet there.
        db_exists = self.file.exists()

        context_stack = await contextlib.AsyncExitStack().__aenter__()
        conn = await context_stack.enter_async_context(aiosqlite.connect(self.file))
        task_group = await context_stack.enter_async_context(asyncio.TaskGroup())

        await conn.execute("PRAGMA synchronous = NORMAL;")
        await conn.execute("PRAGMA cache_size = -64000;")
        await conn.execute("PRAGMA temp_store = MEMORY;")
        await conn.execute("PRAGMA mmap_size = 268435456;")
        await conn.execute("PRAGMA foreign_keys = 1;")

        if not db_exists:
            await conn.execute("PRAGMA journal_mode = WAL;")
            async with _autocommit(conn):
                for statement in _DBSETUP.split(";"):
                    if stripped_statement := statement.strip():
                        await conn.execute(stripped_statement)

        guarded_conn = _GuardedConnection(conn)

        runid = await guarded_conn.execute(
            _log_run,
            version=self.version,
            conf_json=self.conf_json,
            run_json=self.run_json,
        )

        self._state = _SqliteRunTrackingState(
            context=context_stack,
            connection=guarded_conn,
            task_group=task_group,
            runid=runid,
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:
        if self._state is None:  # pragma: no cover
            raise RuntimeError("context not available")

        await self._state.context.__aexit__(exc_type, exc, tb)
        self._state = None
        return False

    def create_subcontext(self, binary: str, *args: str) -> _SqliteTaskTracking:
        if self._state is None:  # pragma: no cover
            raise RuntimeError("context not available")

        return _SqliteTaskTracking(
            dest=args[-1],
            runid=self._state.runid,
            task_group=self._state.task_group,
            connection=self._state.connection,
        )


async def _consume_transaction_queue(
    con: _GuardedConnection,
    /,
    *,
    queue: asyncio.Queue[RsyncTransaction],
    task_group: asyncio.TaskGroup,
    taskid: int,
    batch_timeout: float,
    batch_size: int,
) -> None:
    if batch_timeout <= 0:  # pragma: no cover
        raise ValueError("non-positive timeout")
    if batch_size <= 0:  # pragma: no cover
        raise ValueError("non-positive batch size")

    batch: list[RsyncTransaction] = []
    last_flush = time.monotonic()
    try:
        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=batch_timeout)
                batch.append(item)
                queue.task_done()

                if (
                    current_time := time.monotonic()
                ) - last_flush >= batch_timeout or len(batch) >= batch_size:
                    task_group.create_task(
                        con.execute(
                            _log_transactions,
                            taskid=taskid,
                            transactions=list(batch),
                        )
                    )
                    batch.clear()
                    last_flush = current_time
            except TimeoutError:
                if batch:
                    task_group.create_task(
                        con.execute(
                            _log_transactions,
                            taskid=taskid,
                            transactions=list(batch),
                        )
                    )
                    batch.clear()
                    last_flush = time.monotonic()
    except asyncio.CancelledError:
        while not queue.empty():
            try:
                item = queue.get_nowait()
                batch.append(item)
                queue.task_done()
            except asyncio.QueueEmpty:
                break
        if batch:
            task_group.create_task(
                con.execute(_log_transactions, taskid=taskid, transactions=batch)
            )

        raise


@dataclasses.dataclass(slots=True, kw_only=True)
class _SqliteTaskTrackingState:
    queue: asyncio.Queue[RsyncTransaction]
    taskid: int
    consumer: asyncio.Task


_DEFAULT_SQLITE_BATCH_SIZE: Final[int] = 100
_DEFAULT_SQLITE_BATCH_TIMEOUT: Final[float] = 0.1
_DEFAULT_SQLITE_QUEUING_TIMEOUT: Final[float] = 5.0
_DEFAULT_SQLITE_CLEANUP_TIMEOUT: Final[float] = 5.0
_DEFAULT_SQLITE_QUEUE_MULTIPLIER: Final[int] = 2


@dataclasses.dataclass(slots=True, kw_only=True)
class _SqliteTaskTracking:
    dest: str
    runid: int
    task_group: asyncio.TaskGroup
    connection: _GuardedConnection

    batch_size: int = dataclasses.field(
        default_factory=lambda: int(
            os.getenv("SYNCD_SQLITE_BATCH_SIZE", _DEFAULT_SQLITE_BATCH_SIZE)
        )
    )
    batch_timeout: float = dataclasses.field(
        default_factory=lambda: float(
            os.getenv("SYNCD_SQLITE_BATCH_TIMEOUT", _DEFAULT_SQLITE_BATCH_TIMEOUT)
        )
    )
    queuing_timeout: float = dataclasses.field(
        default_factory=lambda: float(
            os.getenv("SYNCD_SQLITE_QUEUING_TIMEOUT", _DEFAULT_SQLITE_QUEUING_TIMEOUT)
        )
    )
    cleanup_timeout: float = dataclasses.field(
        default_factory=lambda: float(
            os.getenv("SYNCD_SQLITE_CLEANUP_TIMEOUT", _DEFAULT_SQLITE_CLEANUP_TIMEOUT)
        )
    )
    queue_multiplier: int = dataclasses.field(
        default_factory=lambda: int(
            os.getenv("SYNCD_SQLITE_QUEUE_MULTIPLIER", _DEFAULT_SQLITE_QUEUE_MULTIPLIER)
        )
    )

    _state: _SqliteTaskTrackingState | None = dataclasses.field(
        default=None, init=False
    )

    async def __aenter__(self) -> Self:
        taskid = await self.connection.execute(
            _log_task, runid=self.runid, dest=self.dest
        )

        # Leave extra room to avoid blocking.
        queue = asyncio.Queue(maxsize=self.batch_size * self.queue_multiplier)
        consumer = self.task_group.create_task(
            _consume_transaction_queue(
                self.connection,
                queue=queue,
                task_group=self.task_group,
                taskid=taskid,
                batch_timeout=self.batch_timeout,
                batch_size=self.batch_size,
            )
        )

        self._state = _SqliteTaskTrackingState(
            queue=queue, taskid=taskid, consumer=consumer
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:
        if self._state is None:  # pragma: no cover
            raise RuntimeError("context not available")

        # Allows to pass control to the consumer, which might not have been started
        # in case of very short sessions.
        await asyncio.sleep(0.0)
        self._state.consumer.cancel()
        try:
            await asyncio.wait_for(
                self._state.queue.join(), timeout=self.cleanup_timeout
            )
        except TimeoutError:  # pragma: no cover
            _LOGGER.error("tracker queue join timed out during cleanup")

        self._state = None
        return False

    async def log(self, item: RsyncTransaction, /) -> None:
        if self._state is None:  # pragma: no cover
            raise RuntimeError("context not available")

        try:
            await asyncio.wait_for(
                self._state.queue.put(item), timeout=self.queuing_timeout
            )
        except TimeoutError:  # pragma: no cover
            _LOGGER.error(f"failed to queue transaction for {item['filename']}")


def _derive_label(path: str, *, max_len: int, prefix: str = "...") -> str:
    if len(label := path) <= max_len:
        return label

    path_ = Path(path)
    reversed_chosen_parts = tuple(
        part
        for part, cum_len in zip(
            reversed(path_.parts),
            itertools.accumulate(len(s) for s in reversed(path_.parts)),
            strict=True,
        )
        if cum_len <= max_len
    )
    base = "/".join(reversed(reversed_chosen_parts))
    if len(base) <= max_len:
        return base
    return f"{prefix}{base[-(max_len - len(prefix)) :]}"


@dataclasses.dataclass(slots=True, kw_only=True)
class _ConsoleRunTrackingState:
    progress: rich.progress.Progress


@dataclasses.dataclass(slots=True, kw_only=True)
class ConsoleRunTracking:
    console: rich.console.Console
    highlighter: rich.highlighter.Highlighter | None
    verbose: bool

    _state: _ConsoleRunTrackingState | None = dataclasses.field(
        default=None, init=False
    )

    async def __aenter__(self) -> Self:
        progress = rich.progress.Progress(
            rich.progress.TextColumn(
                ":runner:", table_column=rich.table.Column(width=2)
            ),
            rich.progress.TextColumn(
                "{task.fields[marker]}", table_column=rich.table.Column(width=4)
            ),
            rich.progress.TextColumn(
                ":alarm_clock:", table_column=rich.table.Column(width=2)
            ),
            rich.progress.TimeElapsedColumn(table_column=rich.table.Column(width=8)),
            rich.progress.TextColumn(
                ":file_folder:", table_column=rich.table.Column(width=2)
            ),
            rich.progress.TextColumn(
                "{task.description}",
                table_column=rich.table.Column(width=_description_column_width()),
            ),
            *itertools.chain.from_iterable(
                (
                    rich.progress.TextColumn(
                        f"{key}",
                        justify="right",
                        highlighter=self.highlighter,
                        table_column=rich.table.Column(
                            width=max(len(key.name) for key in RsyncAction)
                        ),
                    ),
                    rich.progress.TextColumn(
                        f"{{task.fields[{key}]}}",
                        justify="right",
                        table_column=rich.table.Column(min_width=7),
                    ),
                )
                for key in RsyncAction
            ),
            console=self.console,
        ).__enter__()
        self._state = _ConsoleRunTrackingState(progress=progress)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:
        if self._state is None:  # pragma: no cover
            raise RuntimeError("context not available")

        self._state.progress.__exit__(exc_type, exc, tb)
        return False

    def create_subcontext(self, binary: str, *args: str) -> _ConsoleTaskTracking:
        if self._state is None:  # pragma: no cover
            raise RuntimeError("context not available")

        return _ConsoleTaskTracking(
            dest=args[-1],
            progress=self._state.progress,
            console=self.console if self.verbose else None,
        )


@dataclasses.dataclass(slots=True, kw_only=True)
class _ConsoleTaskTrackingState:
    taskid: rich.progress.TaskID
    counts: collections.Counter[str]


def _description_column_width() -> int:
    return shutil.get_terminal_size().columns - 20 * (len(RsyncAction) + 1)


@dataclasses.dataclass(slots=True, kw_only=True)
class _ConsoleTaskTracking:
    dest: str
    progress: rich.progress.Progress
    console: rich.console.Console | None

    _state: _ConsoleTaskTrackingState | None = dataclasses.field(
        default=None, init=False
    )

    async def __aenter__(self) -> Self:
        counts = collections.Counter({str(key): 0 for key in RsyncAction})
        taskid = self.progress.add_task(
            marker="-",
            description=_derive_label(self.dest, max_len=_description_column_width()),
            **counts,  # type: ignore [reportArgumentType]
            total=1,
        )
        self._state = _ConsoleTaskTrackingState(taskid=taskid, counts=counts)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:
        if self._state is None:  # pragma: no cover
            raise RuntimeError("context not available")

        self.progress.update(self._state.taskid, completed=1)
        self._state = None
        return False

    async def log(self, item: RsyncTransaction, /) -> None:
        if self._state is None:  # pragma: no cover
            raise RuntimeError("context not available")

        self._state.counts.update((str(item["action"]),))
        self.progress.update(
            self._state.taskid,
            marker=str(self._state.taskid),
            **self._state.counts,  # type: ignore [reportArgumentType]
        )
        if self.console is not None:
            template = ":runner: {taskid}  {action} {filename} ({transfer_bytes} bytes)"
            self.console.print(template.format(taskid=self._state.taskid, **item))
