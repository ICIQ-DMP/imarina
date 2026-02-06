"""
Reusable CLI argument definition.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Annotated

import typer

# Argument to send a directory
DirectoryOpt = Annotated[
    Optional[Path],
    typer.Option(
        "-d",
        "--directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to a directory. If omitted, the current directory is used.",
    ),
]


LogFileOpt = Annotated[
    Optional[Path], typer.Option("-l", "--log-file", help="Path to log file (optional)")
]

VerboseOpt = Annotated[
    bool,
    typer.Option(
        "-v", "--verbose", "--debug", help="Verbose output (debug)", is_flag=True
    ),
]

# Very verbose flag
VeryVerboseOpt = Annotated[
    bool,
    typer.Option("--t", "--trace", help="Very verbose output (trace)", is_flag=True),
]

# Quiet flag
QuietOpt = Annotated[
    bool,
    typer.Option("-q", "--quiet", help="Quiet mode (minimal output)", is_flag=True),
]

# Very quiet flag
VeryQuietOpt = Annotated[
    bool,
    typer.Option(
        "-Q", "--Quiet", "--no-output", help="Quiet mode (no output)", is_flag=True
    ),
]


# Add all opts to this variable so they are marked as publicly exposed
__all__ = [
    "VerboseOpt",
    "QuietOpt",
    "DirectoryOpt",
    "VeryVerboseOpt",
    "VeryQuietOpt",
    "LogFileOpt",
]
