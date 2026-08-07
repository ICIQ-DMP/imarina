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

import datetime
import pathlib
from zoneinfo import ZoneInfo

# All dates in this program's data (A3/iMarina Excel exports, run timestamps)
# originate from ICIQ (Tarragona, Spain), so we pin them explicitly to Madrid
# rather than relying on naive datetimes or on whatever timezone the host
# machine/container happens to be configured with.
MADRID_TZ = ZoneInfo("Europe/Madrid")

DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
NOW_DATA = datetime.datetime.now(MADRID_TZ)
NOW = NOW_DATA.strftime(DATETIME_FORMAT)

PROJECT_DIR = pathlib.Path.cwd()
INPUT_DIR = PROJECT_DIR / "input"
OUTPUT_DIR = PROJECT_DIR / "output"
date_str = "31/12/2099"
DATE_FORMAT = "%d/%m/%Y"
PERMANENT_CONTRACT_DATE = datetime.datetime.strptime(date_str, "%d/%m/%Y").replace(
    tzinfo=MADRID_TZ
)
ICIQ_WEBPAGE = "https://iciq.org/"

FILENAME_PREFIX = "iMarina_upload_"
FILENAME_SUFFIX = ".xlsx"
FTP_EXCEL_FILE_DATE_FORMAT = "%y%m%d"

SHAREPOINT_INPUT_FOLDER = (
    "Institutional Strengthening/_Projects/iMarina_load_automation/input"
)

# Single source of truth for the input files `build` needs and `download` must
# provide, under these exact names, in the same flat directory (default:
# PROJECT_DIR / "input"). Keyed by role so callers can refer to files by
# meaning rather than repeating literal filenames.
REQUIRED_INPUT_FILES = {
    "a3": "A3.xlsx",
    "imarina": "iMarina.xlsx",
    "countries": "countries.xlsx",
    "jobs": "Job_Descriptions.xlsx",
    "personal_web": "Personal_web.xlsx",
    "unit_group": "unit_group.xlsx",
    "unit_type": "unit_type.xlsx",
    "job_description_entity": "job_description_entity.xlsx",
}

# --- CLI option defaults ---
# Kept alongside the constants they're derived from (INPUT_DIR, NOW,
# REQUIRED_INPUT_FILES above) rather than in core/shared_options.py, which
# holds only `*Opt` CLI metadata. Controllers reference these directly:
# `param: SomeOpt = DEFAULT_SOME` (see "Adding a new CLI option" in
# CLAUDE.md).

# --- build ---

DEFAULT_COUNTRIES_DICT = INPUT_DIR / REQUIRED_INPUT_FILES["countries"]
DEFAULT_JOBS_DICT = INPUT_DIR / REQUIRED_INPUT_FILES["jobs"]
DEFAULT_IMARINA_INPUT = INPUT_DIR / REQUIRED_INPUT_FILES["imarina"]
DEFAULT_A3_INPUT = INPUT_DIR / REQUIRED_INPUT_FILES["a3"]
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / f"iMarina_upload_{NOW}.xlsx"
DEFAULT_PERSONAL_WEB_PATH = INPUT_DIR / REQUIRED_INPUT_FILES["personal_web"]
DEFAULT_UNIT_GROUP_PATH = INPUT_DIR / REQUIRED_INPUT_FILES["unit_group"]
DEFAULT_ENTITY_TYPE_PATH = INPUT_DIR / REQUIRED_INPUT_FILES["unit_type"]
DEFAULT_JOB_DESCRIPTION_ENTITY_PATH = (
    INPUT_DIR / REQUIRED_INPUT_FILES["job_description_entity"]
)

# --- publish ---

DEFAULT_PUBLISH_FILE_PATH = None
DEFAULT_DRY_RUN = True

# --- upload ---

DEFAULT_UPLOAD_FILE_PATH = None
DEFAULT_TARGET_FOLDER = pathlib.Path(
    "Institutional Strengthening/_Projects/iMarina_load_automation/output"
)

# --- notify ---

DEFAULT_NOTIFY_SHAREPOINT_PATH = DEFAULT_TARGET_FOLDER
