# SPDX-FileCopyrightText: Christian Heinze
#
# SPDX-License-Identifier: Apache-2.0
"""Command generation."""

from __future__ import annotations

import contextlib
import itertools
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Protocol, Self

if TYPE_CHECKING:
    from collections.abc import Generator  # pragma: no cover

import pydantic

from . import _devices, _executable


def _is_relative_path(path: Path) -> Path:
    if path.is_absolute():
        raise ValueError(f"{path} is absolute")
    return path


type RelativePath = Annotated[Path, pydantic.AfterValidator(_is_relative_path)]
type IgnorePattern = Annotated[str, pydantic.Field(pattern="[^!-+]")]


class Item(pydantic.BaseModel):
    """Directory specification.

    See `PATTERN MATCHING RULES` section of the rsync manpage for rules on how
    to specify ignore patterns. Patterns provided here are passed via the `--exclude`
    option.

    If `dest` is provided as a str, then it is passed to `datetime.now().strftime` via
    the `format` parameter, that is, placeholders for date/time components like
    `%Y`, `%m`, etc., are replaced with the actual values at validation time.
    """

    model_config = pydantic.ConfigDict(extra="forbid", frozen=True)

    # The directory names are abstract specifications until combined with an absolute
    # location. Test for existence or being a directory or symlinks cannot be done until
    # then.
    src: RelativePath
    dest: RelativePath

    # Order is immaterial as no includes are allowed.
    ignore: frozenset[IgnorePattern] = frozenset()

    @pydantic.model_validator(mode="before")
    @classmethod
    def _missing_dest_replaced_by_src(cls, data: Any) -> Any:
        if isinstance(data, str | Path):
            data = {"src": data}

        if isinstance(data, dict):
            if "dest" not in data and (src := data.get("src")) is not None:
                data["dest"] = src
            elif isinstance(dest := data.get("dest"), str):
                data["dest"] = datetime.now().strftime(format=dest)

        return data


def _complete(root: Path, sub: Path) -> Path:
    # Checks of `root` being absolute and `sub` being relative are done during object
    # validation.
    return root.joinpath(sub).resolve()


def _select_src_type(v: Any) -> str:
    if isinstance(v, list | tuple) and v:
        v = v[0]

    if isinstance(v, dict) and "phone_ids" in v:
        return "phone"
    if isinstance(v, dict) and "crypttab_id" in v:
        return "luks"
    return "directory"


def _select_dest_type(v: Any) -> str:
    if isinstance(v, list | tuple) and v:
        v = v[0]

    if isinstance(v, dict) and "crypttab_id" in v:
        return "luks"
    return "directory"


class _Device(Protocol):
    def get_mountpoint(self) -> Path: ...

    def open(self) -> Self: ...

    def close(self) -> None: ...


def _handle_subpath_spec[TDevice: _Device](
    pair: TDevice | tuple[TDevice, Path],
) -> tuple[TDevice, Path]:
    if isinstance(pair, tuple):
        device, path = pair
        return device, device.get_mountpoint() / path
    return pair, pair.get_mountpoint()


type RelativePathSpec = Annotated[
    RelativePath,
    pydantic.BeforeValidator(lambda d: d.get("path", d) if isinstance(d, dict) else d),
]


class Configuration(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid", frozen=True)

    src: Annotated[
        Annotated[
            _devices.Phone | tuple[_devices.Phone, RelativePathSpec],
            pydantic.Tag("phone"),
        ]
        | Annotated[
            _devices.LuksDisk | tuple[_devices.LuksDisk, RelativePathSpec],
            pydantic.Tag("luks"),
        ]
        | Annotated[_devices.ExistingDirectory, pydantic.Tag("directory")],
        pydantic.Field(discriminator=pydantic.Discriminator(_select_src_type)),
    ]
    dest: Annotated[
        Annotated[
            _devices.LuksDisk | tuple[_devices.LuksDisk, RelativePathSpec],
            pydantic.Tag("luks"),
        ]
        | Annotated[_devices.Directory, pydantic.Tag("directory")],
        pydantic.Field(
            alias="dest", discriminator=pydantic.Discriminator(_select_dest_type)
        ),
    ]

    items: frozenset[Item] = frozenset((Item.model_validate("."),))

    backup: RelativePath | None = None
    ignore: frozenset[IgnorePattern] = frozenset()

    @pydantic.model_validator(mode="after")
    def _src_and_dest_not_nested(self) -> Self:
        _, src = _handle_subpath_spec(self.src)
        _, dest = _handle_subpath_spec(self.dest)

        # This is incomplete as links can only be resolved once the device is opened.
        # Still it's better to catch some error before doing the time consuming mount.
        if src.is_relative_to(dest) or dest.is_relative_to(src):
            raise ValueError(f"Source '{src}' and destination'{dest}' are nested.")
        return self


@contextlib.contextmanager
def rsync_execution_context(conf: Configuration) -> Generator[None]:
    src, config_src = _handle_subpath_spec(conf.src)
    dest, config_dest = _handle_subpath_spec(conf.dest)

    with contextlib.ExitStack() as es:
        es.enter_context(contextlib.closing(src.open()))
        es.enter_context(contextlib.closing(dest.open()))

        # These checks can only be done once external devices are mounted.
        config_src, config_dest = config_src.resolve(), config_dest.resolve()
        if config_src.is_relative_to(config_dest) or config_dest.is_relative_to(
            config_src
        ):
            raise ValueError(f"Source '{src}' and destination'{dest}' are nested.")

        for a in conf.items:
            a_src_abs = _complete(config_src, a.src)
            if not a_src_abs.is_relative_to(config_src):
                raise ValueError(f"'{a.src}' is not a subdirectory of '{config_src}'")
            if not a_src_abs.is_dir():
                raise ValueError(f"'{a.src}' is not a directory")

        for a in conf.items:
            a_dest_abs = _complete(config_dest, a.dest)
            if not a_dest_abs.is_relative_to(config_dest):
                raise ValueError(f"'{a.dest}' is not a subdirectory of '{config_dest}'")
            if conf.backup is not None:
                backup_abs = _complete(config_dest, conf.backup)
                if a_dest_abs.is_relative_to(backup_abs) or backup_abs.is_relative_to(
                    a_dest_abs
                ):
                    raise ValueError(
                        f"'{a.dest}' is incompatible with backup '{conf.backup}'"
                    )
        for a, b in itertools.product(conf.items, conf.items):
            a_dest_abs = _complete(config_dest, a.dest)
            b_dest_abs = _complete(config_dest, b.dest)
            if a_dest_abs != b_dest_abs and (
                a_dest_abs.is_relative_to(b_dest_abs)
                or b_dest_abs.is_relative_to(a_dest_abs)
            ):
                raise ValueError(
                    f"'{a.dest}' and '{b.dest}' are incompatible as subdirectories"
                )
        yield


def _path_to_cli(path: Path) -> str:
    return path.as_posix() + "/"


def _create_backup_subdir(
    dt: datetime | None = None, *, format_: str | None = None
) -> Path:
    if format_ is None:
        format_ = "%Y%m%d-%H-%M-%S"
    return Path((dt or datetime.now()).strftime(format_))


# Considered adding a `reverse` option (replace role of `src` and `dest`) but decided
# againt it as this would bypass differences in validation (existence!) and (partially
# as a consequence) may have unexpected behavior in case of timestamped destinations.
def rsync_commands(
    conf: Configuration,
    logging_format: str,
    dry_run: bool,
    force: bool,
    delete_extraneous: bool | None,
) -> Generator[tuple[str, list[str]]]:
    base_args = [
        "--mkpath",  # Create target directory if it does not exist.
        "--recursive",  # Recurse into directories.
        "--outbuf=L",  # Use line buffering.
        "--debug=none",  # Silence all debugging messages.
        "--compress",  # Compress during transit.
        "--links",  # Copy symlinks as symlinks.
        "--safe-links",  # Links pointing outside of src will not be created in dest.
        "--one-file-system",  # Do not cross over into other filesystems (mounts!)
        "--perms",  # Retain permissions.
        "--times",  # Retains modification times.
        "--out-format",  # Set output format to show
        logging_format,
    ]

    if dry_run:
        base_args.append("--dry-run")  # Dry-run: no actions.
    if not force:
        base_args.append("--update")  # Skip files that are newer in dest.
    if delete_extraneous or (delete_extraneous is None and conf.backup is not None):
        # Not using --delete-before as deleted files are retained in the backup
        # folder on the target anyways.
        base_args.append("--del")

    rsync = _executable.rsync()
    _, conf_src = _handle_subpath_spec(conf.src)
    _, conf_dest = _handle_subpath_spec(conf.dest)
    for item in conf.items:
        args = base_args.copy()
        if conf.backup is not None:
            backup = (
                conf_dest
                / conf.backup
                / _create_backup_subdir(format_=os.getenv("SYNCD_BACKUP_FMT"))
                / item.dest
            )
            # The `--backup-dir` option automatically creates the backup directory.
            # A relative path will be considered relative to the destination directory.
            args.extend(("--backup", "--backup-dir", _path_to_cli(backup)))
        args.extend(
            f"--exclude={pattern}"
            for pattern in itertools.chain(item.ignore, conf.ignore)
        )
        args.extend(
            (
                _path_to_cli(conf_src.joinpath(item.src)),
                _path_to_cli(conf_dest.joinpath(item.dest)),
            )
        )

        yield rsync, args
