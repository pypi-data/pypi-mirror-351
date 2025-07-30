# SPDX-FileCopyrightText: Christian Heinze
#
# SPDX-License-Identifier: Apache-2.0
"""CLI entrypoint."""

from __future__ import annotations

import sys

from syncd import _cli

if __name__ == "__main__":
    sys.exit(_cli.run())
