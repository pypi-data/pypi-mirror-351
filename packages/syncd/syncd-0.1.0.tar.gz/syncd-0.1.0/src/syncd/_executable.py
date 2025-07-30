# SPDX-FileCopyrightText: Christian Heinze
#
# SPDX-License-Identifier: Apache-2.0
"""Executables."""

from __future__ import annotations

import functools
import os
import shutil
from pathlib import Path


def _find(name: str | None, *, env: str | None = None) -> str:
    if name is not None and not Path(name).is_absolute():
        name = shutil.which(name)
    if name is None and env is not None:
        name = os.getenv(env)
    if name is None:  # pragma: no cover
        raise RuntimeError("failed to discover binary")
    return name


rsync = functools.partial(_find, "rsync", env="SYNCD_RSYNC_EXEC")
lsusb = functools.partial(_find, "lsusb", env="SYNCD_LSUSB_EXEC")
gio = functools.partial(_find, "gio", env="SYNCD_GIO_EXEC")

cryptdisks_start = functools.partial(
    _find, "cryptdisks_start", env="SYNCD_CD_START_EXEC"
)
cryptdisks_stop = functools.partial(_find, "cryptdisks_stop", env="SYNCD_CD_STOP_EXEC")
mount = functools.partial(_find, "mount", env="SYNCD_MOUNT_EXEC")
umount = functools.partial(_find, "umount", env="SYNCD_UMOUNT_EXEC")
sudo = functools.partial(_find, "sudo", env="SYNCD_SUDO_EXEC")
chown = functools.partial(_find, "chown", env="SYNCD_CHOWN_EXEC")
