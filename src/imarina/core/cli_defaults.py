# imarina-load - Automated imarina data loads
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
Typer option annotations and their default values for the `build`, `publish`
and `upload` commands, kept out of `commands/*/cli.py` so `typer.Option(...)`
is never called inline in a function signature (see ruff rule B008).

Each `*Opt` alias carries only the CLI metadata (help text, flags); the actual
default value is a plain module-level constant, referenced (not computed) at
the controller's function-signature default.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from imarina.core.defines import NOW, PROJECT_DIR, REQUIRED_INPUT_FILES

INPUT_DIR = PROJECT_DIR / "input"

# --- build ---

DEFAULT_COUNTRIES_DICT = INPUT_DIR / REQUIRED_INPUT_FILES["countries"]
DEFAULT_JOBS_DICT = INPUT_DIR / REQUIRED_INPUT_FILES["jobs"]
DEFAULT_IMARINA_INPUT = INPUT_DIR / REQUIRED_INPUT_FILES["imarina"]
DEFAULT_A3_INPUT = INPUT_DIR / REQUIRED_INPUT_FILES["a3"]
DEFAULT_OUTPUT_PATH = PROJECT_DIR / "output" / f"iMarina_upload_{NOW}.xlsx"
DEFAULT_PERSONAL_WEB_PATH = INPUT_DIR / REQUIRED_INPUT_FILES["personal_web"]
DEFAULT_UNIT_GROUP_PATH = INPUT_DIR / REQUIRED_INPUT_FILES["unit_group"]
DEFAULT_ENTITY_TYPE_PATH = INPUT_DIR / REQUIRED_INPUT_FILES["unit_type"]
DEFAULT_JOB_DESCRIPTION_ENTITY_PATH = (
    INPUT_DIR / REQUIRED_INPUT_FILES["job_description_entity"]
)

CountriesDictOpt = Annotated[
    Path, typer.Option(help="Path of the countries dictionary file(.xlsx)")
]
JobsDictOpt = Annotated[
    Path, typer.Option(help="Path of the jobs dictionary file(.xlsx)")
]
ImarinaInputOpt = Annotated[
    Path, typer.Option(help="Path of the iMarina input file(.xlsx)")
]
A3InputOpt = Annotated[Path, typer.Option(help="Path to A3 input file(.xlsx)")]
OutputPathOpt = Annotated[Path, typer.Option()]
PersonalWebPathOpt = Annotated[Path | None, typer.Option()]
UnitGroupPathOpt = Annotated[Path | None, typer.Option()]
EntityTypePathOpt = Annotated[Path | None, typer.Option()]
JobDescriptionEntityPathOpt = Annotated[Path | None, typer.Option()]

# --- publish ---

DEFAULT_PUBLISH_FILE_PATH = None
DEFAULT_DRY_RUN = True

PublishFilePathOpt = Annotated[
    Path | None,
    typer.Option(help="Path to the iMarina Excel file to upload to the SFTP server"),
]
DryRunOpt = Annotated[
    bool, typer.Option(help="Dry run, connect to FTP server but do not upload files")
]

# --- upload ---

DEFAULT_UPLOAD_FILE_PATH = None
DEFAULT_TARGET_FOLDER = Path(
    "Institutional Strengthening/_Projects/iMarina_load_automation/output"
)

UploadFilePathOpt = Annotated[
    Path | None,
    typer.Option(
        help="Excel file path (.xlsx). If left empty, it will look for the last one in 'output'."
    ),
]
TargetFolderOpt = Annotated[
    Path, typer.Option(help="Folder to the destination Sharepoint")
]

__all__ = [
    "DEFAULT_A3_INPUT",
    "DEFAULT_COUNTRIES_DICT",
    "DEFAULT_DRY_RUN",
    "DEFAULT_ENTITY_TYPE_PATH",
    "DEFAULT_IMARINA_INPUT",
    "DEFAULT_JOBS_DICT",
    "DEFAULT_JOB_DESCRIPTION_ENTITY_PATH",
    "DEFAULT_OUTPUT_PATH",
    "DEFAULT_PERSONAL_WEB_PATH",
    "DEFAULT_PUBLISH_FILE_PATH",
    "DEFAULT_TARGET_FOLDER",
    "DEFAULT_UNIT_GROUP_PATH",
    "DEFAULT_UPLOAD_FILE_PATH",
    "A3InputOpt",
    "CountriesDictOpt",
    "DryRunOpt",
    "EntityTypePathOpt",
    "ImarinaInputOpt",
    "JobDescriptionEntityPathOpt",
    "JobsDictOpt",
    "OutputPathOpt",
    "PersonalWebPathOpt",
    "PublishFilePathOpt",
    "TargetFolderOpt",
    "UnitGroupPathOpt",
    "UploadFilePathOpt",
]
