# imarina-load-researchers - Automated iMarina data loads
# Copyright (C) 2026  Aleix Mariné Tena (AleixMT) and Sonia Sayalero
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Reusable CLI argument definitions, shared across commands or specific to
`build`, `publish`, `upload` and `notify`.

Each `*Opt` alias carries only the CLI metadata (help text, flags) — no
default values live here. Where a default is more than a trivial literal,
it's a `DEFAULT_*` constant in `core/defines.py`, referenced (not computed)
at the controller's function-signature default, so `typer.Option(...)` is
never called inline in a function signature (see ruff rule B008).
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from imarina_load_researchers.core.mail import WorkflowStatus

# Argument to send a directory
DirectoryOpt = Annotated[
    Path,
    typer.Option(
        "-d",
        "--directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to a directory",
    ),
]


LogFileOpt = Annotated[
    Path, typer.Option("-l", "--log-file", help="Path to log file (optional)")
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

# --- download ---

OperationIdOpt = Annotated[
    int,
    typer.Argument(help="Element ID from MS List containing the data of this request"),
]

# --- build ---

# Each of these takes precedence over InputDirOpt for its own file, if given
# — see InputDirOpt's help text and build_controller for the resolution order.
_OVERRIDES_INPUT_DIR = "Overrides --input-dir for this file, if given."

CountriesDictOpt = Annotated[
    Path | None,
    typer.Option(
        help=f"Path of the countries dictionary file(.xlsx). {_OVERRIDES_INPUT_DIR}"
    ),
]
JobsDictOpt = Annotated[
    Path | None,
    typer.Option(
        help=f"Path of the jobs dictionary file(.xlsx). {_OVERRIDES_INPUT_DIR}"
    ),
]
ImarinaInputOpt = Annotated[
    Path | None,
    typer.Option(help=f"Path of the iMarina input file(.xlsx). {_OVERRIDES_INPUT_DIR}"),
]
A3InputOpt = Annotated[
    Path | None,
    typer.Option(help=f"Path to A3 input file(.xlsx). {_OVERRIDES_INPUT_DIR}"),
]
OutputPathOpt = Annotated[Path, typer.Option()]
PersonalWebPathOpt = Annotated[Path | None, typer.Option(help=_OVERRIDES_INPUT_DIR)]
UnitGroupPathOpt = Annotated[Path | None, typer.Option(help=_OVERRIDES_INPUT_DIR)]
EntityTypePathOpt = Annotated[Path | None, typer.Option(help=_OVERRIDES_INPUT_DIR)]
JobDescriptionEntityPathOpt = Annotated[
    Path | None, typer.Option(help=_OVERRIDES_INPUT_DIR)
]
SexPathOpt = Annotated[Path | None, typer.Option(help=_OVERRIDES_INPUT_DIR)]
InputDirOpt = Annotated[
    Path | None,
    typer.Option(
        help="Directory containing all `build` input files, each named as in "
        "REQUIRED_INPUT_FILES (core/defines.py). Any explicit per-file path "
        "option (--countries-dict, --a3-input, ...) takes precedence over "
        "this for that one file; unset, each file falls back to ./input."
    ),
]

# --- publish ---

PublishFilePathOpt = Annotated[
    Path | None,
    typer.Option(help="Path to the iMarina Excel file to upload to the SFTP server"),
]
DryRunOpt = Annotated[
    bool, typer.Option(help="Dry run, connect to FTP server but do not upload files")
]

# --- upload ---

UploadFilePathOpt = Annotated[
    Path | None,
    typer.Option(
        help="Excel file path (.xlsx). If left empty, it will look for the last one in 'output'."
    ),
]
TargetFolderOpt = Annotated[
    Path, typer.Option(help="Folder to the destination Sharepoint")
]

# --- shared: build/upload/publish ---

# Optional, unlike OperationIdOpt/NotifyIdOpt: `build`, `upload` and `publish`
# can all run detached from any MS List request (e.g. local/dev use), in
# which case no MS List item is touched at all.
IdOpt = Annotated[
    int | None,
    typer.Option(
        "--id",
        help="MS List item ID for this request. Used to update its Workflow "
        "State field and, depending on the command, related link fields; if "
        "omitted, no MS List item is touched.",
    ),
]

# --- notify ---

NotifyIdOpt = Annotated[int, typer.Option("--id", help="MS List item ID")]
NotifyStatusOpt = Annotated[
    WorkflowStatus, typer.Option("--status", help="Workflow status")
]
NotifySharepointPathOpt = Annotated[
    Path,
    typer.Option("--sharepoint-path", help="SharePoint path of the generated file"),
]


# Add all opts to this variable so they are marked as publicly exposed
__all__ = [
    "A3InputOpt",
    "CountriesDictOpt",
    "DirectoryOpt",
    "DryRunOpt",
    "EntityTypePathOpt",
    "IdOpt",
    "ImarinaInputOpt",
    "InputDirOpt",
    "JobDescriptionEntityPathOpt",
    "JobsDictOpt",
    "LogFileOpt",
    "NotifyIdOpt",
    "NotifySharepointPathOpt",
    "NotifyStatusOpt",
    "OperationIdOpt",
    "OutputPathOpt",
    "PersonalWebPathOpt",
    "PublishFilePathOpt",
    "QuietOpt",
    "TargetFolderOpt",
    "UnitGroupPathOpt",
    "UploadFilePathOpt",
    "VerboseOpt",
    "VeryQuietOpt",
    "VeryVerboseOpt",
]
