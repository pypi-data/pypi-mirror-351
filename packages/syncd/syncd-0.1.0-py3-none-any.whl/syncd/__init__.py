# SPDX-FileCopyrightText: Christian Heinze
#
# SPDX-License-Identifier: Apache-2.0
"""syncd synchronization utility."""

from __future__ import annotations

import importlib.metadata

from ._concurrent import RunMultiTracking, run
from ._request import Configuration, rsync_commands, rsync_execution_context
from ._tracker import (
    RSYNC_OUTFORMAT,
    ConsoleRunTracking,
    RsyncAction,
    RsyncTransaction,
    SqliteRunTracking,
    parse_stdout,
)

__version__ = importlib.metadata.version(__name__)

__all__ = [
    "RSYNC_OUTFORMAT",
    "Configuration",
    "ConsoleRunTracking",
    "RsyncAction",
    "RsyncTransaction",
    "RunMultiTracking",
    "SqliteRunTracking",
    "parse_stdout",
    "rsync_commands",
    "rsync_execution_context",
    "run",
]


def __dir__() -> list[str]:  # pragma: no cover
    return __all__
