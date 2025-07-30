# SPDX-FileCopyrightText: Christian Heinze
#
# SPDX-License-Identifier: Apache-2.0
"""CLI.

Also showcases how to use syncd as a library.
"""

from __future__ import annotations

import argparse
import asyncio
import dataclasses
import errno
import functools
import multiprocessing
import os
import subprocess
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, Final, Self, TypedDict

import pydantic
import rich.console
import rich.highlighter
import rich.theme

import syncd

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable, Iterable


class _RsyncActionHighlighter(rich.highlighter.RegexHighlighter):
    base_style = "rsync_action."
    highlights = [  # noqa: RUF012
        rf"(?P<{action.name}>{action.name.lower()})" for action in syncd.RsyncAction
    ]


def _rsync_action_style(action: syncd.RsyncAction) -> str:
    match action:
        case syncd.RsyncAction.CREATE:
            return "bold white on #0050aa"
        case syncd.RsyncAction.COPY:
            return "bold white on #006020"
        case syncd.RsyncAction.DELETE:
            return "bold white on #aa0000"


_HIGHLIGHTER: Final[_RsyncActionHighlighter] = _RsyncActionHighlighter()
_CONSOLE: Final[rich.console.Console] = rich.console.Console(
    highlighter=_HIGHLIGHTER,
    theme=rich.theme.Theme(
        {"rsync_action." + t.name: _rsync_action_style(t) for t in syncd.RsyncAction}
        | {"progress.elapsed": "bold #606060"}
    ),
)


def _determine_dir(
    *, create_if_missing: bool = False, find: Callable[[], Path]
) -> Path:
    if not (dir_ := find()).is_absolute():
        dir_ = Path.home().joinpath(dir_).resolve()
    if not dir_.exists():
        if create_if_missing:
            dir_.mkdir(parents=True)
        else:  # pragma: no cover
            raise FileNotFoundError(f"directory '{dir_}' does not exist")
    elif not dir_.is_dir():  # pragma: no cover
        raise NotADirectoryError(f"'{dir_}' exists but is not a directory")
    return dir_


def _find_config_dir() -> Path:
    return Path(
        os.getenv(
            "SYNCD_CONFIG_DIR",
            Path(os.getenv("XDG_CONFIG_HOME", ".config"), "syncd"),
        )
    )


def _find_state_dir() -> Path:
    return Path(
        os.getenv(
            "SYNCD_STATE_DIR", os.getenv("XDG_STATE_HOME", Path(".local", "state"))
        )
    )


_determine_conf_dir = functools.partial(_determine_dir, find=_find_config_dir)
_determine_state_dir = functools.partial(_determine_dir, find=_find_state_dir)


def _find_existing_confs() -> Iterable[str]:
    try:
        config_dir = _determine_conf_dir()
    except (FileNotFoundError, NotADirectoryError):
        return ()
    return (f.stem for f in config_dir.glob("*.toml"))


CONFIGURATION_TEMPLATE: Final[str] = """\
# To sync a directory on the local disk..
src = "(absolute or relative to ~) path to source directory"

# When using a table to specify `src` or `dest`, then toplevel specifications
# like `item`, `backup`, etc., must com first.

# To sync directories on the toplevel of a phone.
# [src]
# phone_ids = ["sub", strings", "from", "lsusb", "output"]
# serial = "serial number obtained via lsusb -v -s BUS:DEVICE"

# To sync sync directories inside a lower level directory of a phone.
# [[src]]
# phone_ids = ["sub", strings", "from", "lsusb", "output"]
# serial = "serial number obtained via lsusb -v -s BUS:DEVICE"
# [[src]]
# path = "(relative to phone mountpoint) path to source directory"

# To sync directories on the toplevel of a LUKS encrypted disk.
# [src]
# crypttab_id = "Volume name used in /etc/crypttab"
# mountpoint = "Mount point in /etc/fstag"

# To sync directories inside a lower level directory of a LUKS encrypted disk.
# [[src]]
# crypttab_id = "Volume name used in /etc/crypttab"
# mountpoint = "Mount point in /etc/fstag"
# [[src]]
# path = "(relative to disk mountpoint) path to source directory"

dest = "(absolute or relative to ~) path to destination directory"
# Other options in analogy with `src`.

# Optional subdirectories. If not supplied, then the entire `src` is copied into `dest`.
# Destination folder names may include `strptime` datetime specs which are automatically
# replaced. Subdirectory specifications are allowed in the source and destination.
items = [
    "1st subdirectory",
    { src = "2nd subdirectory", dest = "name of 2nd subdirectory in dest" },
    { src = "3rd subdirectory", ignore = ["*.txt"] },
    { src = "4nd subdirectory", dest = "pics_%Y_%m", ignore = {"*.py", "x/**/*.txt" },
    { src = "5nd/sub/directory", dest = "pics/%Y/%m/%d" },
]

# Optional ignore list. Ignored in all subdirectories.
# If a pattern does not contains a non-trailing `/` or `**`, then it is matched against
# the final path component and against the full path otherwise (anchored at the end,
# e.g. foo/bar requires the final two components to be foo and bar). Moreover,
# * trailing `/` = only diectories;
# * `?` = any single character except `/`;
# * `*` = zero or more non-`/` characters;
# * `**` = zero or more characters, including slashes;
# * `[...]` one charcter from ...
ignore = [""]

# Optional backup directory.
backup = "Path to backup directory relative to `dest`"
"""


@dataclasses.dataclass(slots=True, kw_only=True)
class _CliConfArgs:
    conf: str

    copy: str | None

    @classmethod
    def from_cli(cls, *args: str) -> Self:
        if available_confs := tuple(_find_existing_confs()):
            listing = ", ".join(f"'{n}'" for n in available_confs)
            available_confs_suffix = f" Already available: {listing}."
        else:
            available_confs_suffix = ""

        parser = argparse.ArgumentParser(description="Create or modify configurations.")
        parser.add_argument(
            "conf",
            help="Name of configuration to be created or modified."
            + available_confs_suffix,
        )
        parser.add_argument(
            "--copy",
            default=None,
            help="Name of configuration to be copied."
            " May only be used if conf does not yet exist.",
            choices=available_confs,
        )

        ns = parser.parse_args(args if args else None)
        return cls(**ns.__dict__)


def conf(*args: str) -> int:
    cli_args = _CliConfArgs.from_cli(*args)
    try:
        conf_dir = _determine_conf_dir(create_if_missing=True)
    except NotADirectoryError as err:  # pragma: no cover
        _CONSOLE.print(err)
        return errno.ENOTDIR

    if not (
        path := conf_dir.joinpath(name := cli_args.conf).with_suffix(".toml")
    ).exists():
        _CONSOLE.print(f"Configuration '{name}' not found. Will", end="")
        if cli_args.copy is not None:
            _CONSOLE.print(f" copy configuration '{cli_args.copy}' to '{path}'.")
            path.write_text(
                conf_dir.joinpath(cli_args.copy).with_suffix(".toml").read_text()
            )
        else:
            _CONSOLE.print(f" write a template to '{path}'.")
            path.write_text(CONFIGURATION_TEMPLATE)
    elif cli_args.copy is not None:
        _CONSOLE.print(f"Cannot copy '{cli_args.copy}' as '{conf}' already exists.")
        return errno.EEXIST
    elif not path.is_file():  # pragma: no cover
        _CONSOLE.print(f"'{path}' exists but is not a file.")
        return errno.EISDIR

    if (editor := os.getenv("EDITOR")) is None:  # pragma: no cover
        _CONSOLE.print("No editor found. Set environment variable 'EDITOR'.")
        return 0
    try:
        subprocess.run((editor, path.as_posix()), check=True)
    except subprocess.CalledProcessError as err:  # pragma: no cover
        _CONSOLE.print(err)
        return err.returncode
    return 0


@dataclasses.dataclass(slots=True, kw_only=True)
class _CliRunArgs:
    conf: str

    dry_run: bool
    delete_extraneous: bool | None
    verbose: bool
    force: bool

    @classmethod
    def from_cli(cls, *args: str) -> Self:
        if available_confs := tuple(_find_existing_confs()):
            listing = ", ".join(f"'{n}'" for n in available_confs)
            available_confs_suffix = f" Already available: {listing}."
        else:
            available_confs_suffix = ""

        parser = argparse.ArgumentParser(
            description="Synchronize according to an existing configuration."
        )
        parser.add_argument(
            "conf",
            help="Name of configuration to be executed." + available_confs_suffix,
            choices=available_confs,
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do a dry-run; no files are actually copied or deleted.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Replace more recent versions of files in destination.",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show individual file actions in addition to summary.",
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--del-extra",
            default=None,
            dest="delete_extraneous",
            action="store_true",
            help="Delete extra files in destination.",
        )
        group.add_argument(
            "--no-del-extra",
            default=None,
            dest="delete_extraneous",
            action="store_false",
            help="Do not delete files in destination.",
        )

        ns = parser.parse_args(args if args else None)
        return cls(**ns.__dict__)


def _load_conf(name: str, /) -> syncd.Configuration:
    conf_dir = _determine_conf_dir()
    if not (path := conf_dir.joinpath(name).with_suffix(".toml")).is_file():
        raise FileNotFoundError(f"configuration '{name}' not found")  # pragma: no cover

    try:
        raw_conf = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as err:  # pragma: no cover
        raise RuntimeError(f"failed to parse configuration '{name}'") from err
    except PermissionError as err:  # pragma: no cover
        raise RuntimeError(f"failed to access configuration '{name}'") from err
    except OSError as err:  # pragma: no cover
        raise RuntimeError(f"failed to read configuration '{name}'") from err
    try:
        conf = syncd.Configuration.model_validate(raw_conf)
    except pydantic.ValidationError as err:  # pragma: no cover
        raise RuntimeError(f"failed to validate configuration '{name}'") from err
    return conf


class _RunKwargs(TypedDict):
    dry_run: bool
    force: bool
    delete_extraneous: bool | None


_RUN_KWARGS_VALIDATOR: Final[pydantic.TypeAdapter] = pydantic.TypeAdapter(_RunKwargs)


async def _run_async(*args: str) -> int:
    cli_args = _CliRunArgs.from_cli(*args)
    try:
        conf = _load_conf(cli_args.conf)
    except (NotADirectoryError, FileNotFoundError) as err:  # pragma: no cover
        _CONSOLE.print(err)
        return errno.ENOENT
    except RuntimeError as err:  # pragma: no cover
        _CONSOLE.print(err)
        return errno.EACCES

    max_processes = int(
        os.getenv("SYNCD_MAX_PROCESSES", (multiprocessing.cpu_count() or 2) - 1)
    )
    parsing_kwargs = {
        "lookup_timeout": 0.05,
        "parser_stdout": syncd.parse_stdout,
        # TODO: Handle stderr seriously.
        "parser_stderr": lambda _: None,
    }
    run_kwargs = {
        "dry_run": cli_args.dry_run,
        "force": cli_args.force,
        "delete_extraneous": cli_args.delete_extraneous,
    }

    try:
        with syncd.rsync_execution_context(conf):
            cmds = syncd.rsync_commands(
                conf, **run_kwargs, logging_format=syncd.RSYNC_OUTFORMAT
            )
            await syncd.run(
                cmds,
                max_processes=max_processes,
                tracking_context=syncd.RunMultiTracking[syncd.RsyncTransaction](
                    trackers=(
                        syncd.SqliteRunTracking(
                            file=_determine_state_dir() / "syncd.log",
                            version=syncd.__version__,
                            conf_json=conf.model_dump_json(),
                            run_json=_RUN_KWARGS_VALIDATOR.dump_json(run_kwargs).decode(
                                "utf8"
                            ),
                        ),
                        syncd.ConsoleRunTracking(
                            console=_CONSOLE,
                            highlighter=_HIGHLIGHTER,
                            verbose=cli_args.verbose,
                        ),
                    ),
                ),
                **parsing_kwargs,
            )
    except Exception as err:  # noqa: BLE001 # pragma: no cover
        _CONSOLE.print(err)
        return 1
    return 0


def run(*args: str) -> int:
    return asyncio.run(_run_async())
