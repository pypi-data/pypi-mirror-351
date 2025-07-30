# SPDX-FileCopyrightText: Christian Heinze
#
# SPDX-License-Identifier: Apache-2.0
"""Connect to a devices."""

from __future__ import annotations

import functools
import logging
import os
import re
import subprocess
import time
import urllib.parse
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, NotRequired, Self, TypedDict, Unpack

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable

    type Formatter = Callable[[str], str]

import pydantic

from . import _executable

_LOGGER = logging.getLogger(__name__)


class _PathToDirectory(pydantic.RootModel):
    root: Path

    def get_mountpoint(self) -> Path:
        return self.root

    def open(self) -> Self:
        return self

    def close(self) -> None:
        pass  # pragma: no cover


def _ensure_absolute_nolink(path: Path) -> Path:
    """Ensure absolute path and resolves links.

    Relativ path are considered relative to user's home directory.
    """
    if not path.is_absolute():
        path = Path.home() / path
    # Calling `resolve` directly roots relative paths in the cwd; exposes links.
    return path.resolve()


def _if_exists_is_directory(path: Path) -> Path:
    if path.exists() and not path.is_dir():
        raise ValueError(f"'{path}' is not a directory")
    return path


type AbsolutePathToDirectory = Annotated[
    Path,
    pydantic.AfterValidator(_ensure_absolute_nolink),
    pydantic.AfterValidator(_if_exists_is_directory),
]


class Directory(_PathToDirectory):
    root: AbsolutePathToDirectory


def _exists(path: Path) -> Path:
    if not path.exists():
        raise ValueError(f"'{path}' does not exist")
    return path


type _AbsolutePathToExistingDirectory = Annotated[
    Path,
    pydantic.AfterValidator(_ensure_absolute_nolink),
    pydantic.AfterValidator(_exists),
    pydantic.AfterValidator(_if_exists_is_directory),
]


class ExistingDirectory(_PathToDirectory):
    root: _AbsolutePathToExistingDirectory


def _run(binary: str, *args: str, timeout: float) -> str:
    try:
        result = subprocess.run(
            (binary, *args),
            capture_output=True,
            check=False,
            encoding="utf-8",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        cmd = " ".join((binary, *args))
        raise RuntimeError(f"'{cmd}' timed out") from None
    if result is not None and result.stderr:
        _LOGGER.error(result.stderr)
    if result is None or result.returncode != 0:
        cmd = " ".join((binary, *args))
        raise RuntimeError(f"unsuccessfully called '{cmd}'")
    return result.stdout


_run_lsusb = functools.partial(_run, _executable.lsusb(), timeout=10.0)
_run_gio = functools.partial(_run, _executable.gio(), timeout=10.0)


_DEVICE_DESC_LINE: re.Pattern[str] = re.compile(
    r"^\s*(?P<key>(iManufacturer)|(iProduct)|(iSerial))"
    r"\s+[0-9]\s+(?P<value>[- \w]+?)\s*$",
    re.MULTILINE,
)


class PhoneMetadata(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True, extra="forbid")

    manufacturer: str
    product: str
    serial: str

    @pydantic.model_validator(mode="before")
    @classmethod
    def _create_from_bus_and_device(cls, data: Any) -> Any:
        if not isinstance(data, dict) or data.keys() != {"bus", "device"}:
            return data

        return {
            # Permissible key values are in _DEVICE_DESC_LINE.
            match.group("key").removeprefix("i").lower(): match.group("value")
            for match in _DEVICE_DESC_LINE.finditer(
                _run_lsusb("-vs", "{bus}:{device}".format(**data))
            )
        }


_CONNECTION_PATTERN: re.Pattern[str] = re.compile(
    r"^Bus (?P<bus>[0-9]{3}) Device (?P<device>[0-9]{3}):"
)


@pydantic.with_config(pydantic.ConfigDict(extra="forbid"))
class _PhoneDescription(TypedDict):
    phone_ids: Annotated[
        list[Annotated[str, pydantic.Field(min_length=1)]], pydantic.Field(min_length=1)
    ]
    serial: NotRequired[Annotated[str, pydantic.Field(min_length=1)]]


class _LoggingSetup(TypedDict):
    send: NotRequired[Callable[[str], None]]

    fmt_failure: NotRequired[Formatter]
    fmt_success: NotRequired[Formatter]


_PhoneDescriptionValidator = pydantic.TypeAdapter(_PhoneDescription)


def _retrieve_phone_data(
    description: _PhoneDescription, **logging: Unpack[_LoggingSetup]
) -> dict[str, Any]:
    send = logging.get("send")
    fmt_failure = logging.get("fmt_failure")
    fmt_success = logging.get("fmt_success")

    serial = description.get("serial")
    for line in (
        line
        for line in _run_lsusb().splitlines()
        if all(kw in line for kw in description["phone_ids"])
    ):
        if not (match := _CONNECTION_PATTERN.match(line)):
            if callable(send):
                failure_msg = f"Failed to parse '{line}'."
                if callable(fmt_failure):
                    failure_msg = fmt_failure(failure_msg)
                send(failure_msg)
            continue
        data = match.groupdict()
        data["metadata"] = PhoneMetadata.model_validate(data, context=logging)
        if serial is None or data["metadata"].serial == serial:
            if callable(send):
                success_msg = f"Success using '{line}'."
                if callable(fmt_success):
                    success_msg = fmt_success(success_msg)
                send(success_msg)
            return data
        if callable(send):
            failure_msg = f"Serial did not match for '{line}'."
            if callable(fmt_failure):
                failure_msg = fmt_failure(failure_msg)
            send(failure_msg)
    raise RuntimeError("could not find device") from None


class Phone(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True, extra="forbid")

    bus: Annotated[str, pydantic.Field(pattern="[0-9]{3}")]
    device: Annotated[str, pydantic.Field(pattern="[0-9]{3}")]
    metadata: PhoneMetadata

    @pydantic.model_validator(mode="before")
    @classmethod
    def _create_from_phone_description(
        cls, data: Any, info: pydantic.ValidationInfo
    ) -> Any:
        if not isinstance(data, dict):
            return data
        try:
            description = _PhoneDescriptionValidator.validate_python(data)
        except pydantic.ValidationError:
            return data

        if isinstance(info.context, dict):
            return _retrieve_phone_data(description, **info.context)
        return _retrieve_phone_data(description)

    def _is_auto_mounted(self) -> bool:
        gio_list = _run_gio("mount", "--list")
        return self._create_identifier(auto_mounted=True) in gio_list

    def _create_identifier(self, auto_mounted: bool | None = None) -> str:
        if auto_mounted is None:
            auto_mounted = self._is_auto_mounted()
        if auto_mounted:
            return "{manufacturer}_{product}_{serial}".format(
                **self.metadata.model_dump()
            )
        return f"[usb:{self.bus},{self.device}]"

    def _get_mtp(self) -> str:
        return f"mtp://{self._create_identifier()}/"

    def get_mountpoint(self) -> Path:
        return Path(
            "/run",
            "user",
            str(os.getuid()),
            "gvfs",
            "mtp:host=" + urllib.parse.quote(self._create_identifier()),
        )

    def open(self) -> Self:
        if not self._is_auto_mounted():
            _run_gio("mount", self._get_mtp())
        if not _run_gio("list", self.get_mountpoint().as_posix()):
            self.close()
            raise RuntimeError("empty phone disk. Did you activate file transfer")
        return self

    def close(self) -> None:
        if self._is_auto_mounted():
            return
        _run_gio("mount", "-u", self._get_mtp())


_run_cryptdisks_start = functools.partial(
    _run, _executable.sudo(), _executable.cryptdisks_start(), timeout=20.0
)
_run_cryptdisks_stop = functools.partial(
    _run, _executable.sudo(), _executable.cryptdisks_stop(), timeout=20.0
)
_run_mount = functools.partial(_run, _executable.mount(), timeout=20.0)
_run_umount = functools.partial(_run, _executable.umount(), timeout=20.0)


class LuksDisk(pydantic.BaseModel):
    """USB disk encrypted with LUKS.

    - Disk handling must be specified in /etc/crypttab. The user must have
      permission to call `cryptdisks_{start,stop}` via sudo without entering
      a password.
    - Mountpoint must be specified in /etc/fstab and have the user option set.
    - User must have rights to run cryptdisks_{start,stop} and mount via sudo.
    """

    model_config = pydantic.ConfigDict(extra="forbid")

    crypttab_id: Annotated[str, pydantic.Field(min_length=1)]
    mountpoint: AbsolutePathToDirectory

    @property
    def _mapper(self) -> Path:
        return Path("/dev", "mapper", self.crypttab_id)

    def _is_mapped(self) -> bool:
        return self._mapper.exists()

    def _map(self) -> None:
        if not self._is_mapped():
            _run_cryptdisks_start(self.crypttab_id)

    def _unmap(self) -> None:
        if self._is_mapped():
            _run_cryptdisks_stop(self.crypttab_id)

    def _is_mounted(self) -> bool:
        return self._is_mapped() and (
            f"{self._mapper.as_posix()} on {self.mountpoint.as_posix()}" in _run_mount()
        )

    def _mount(self) -> None:
        if not self._is_mounted():
            _run_mount(self.mountpoint.as_posix())

    def _umount(self) -> None:
        if self._is_mounted():
            _run_umount(self.mountpoint.as_posix())

    def get_mountpoint(self) -> Path:
        return self.mountpoint

    def open(self) -> Self:
        self._map()
        try:
            self._mount()
        except RuntimeError:
            self._unmap()
            raise
        return self

    def close(self) -> None:
        self._umount()
        time.sleep(2.0)
        self._unmap()
