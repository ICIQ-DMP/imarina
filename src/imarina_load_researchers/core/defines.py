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

import datetime
import pathlib
from zoneinfo import ZoneInfo

# All dates in this program's data (A3/iMarina Excel exports, run timestamps)
# originate from ICIQ (Tarragona, Spain), so we pin them explicitly to Madrid
# rather than relying on naive datetimes or on whatever timezone the host
# machine/container happens to be configured with.
MADRID_TZ = ZoneInfo("Europe/Madrid")

DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"

date_str = "31/12/2099"
DATE_FORMAT = "%d/%m/%Y"
PERMANENT_CONTRACT_DATE = datetime.datetime.strptime(date_str, "%d/%m/%Y").replace(
    tzinfo=MADRID_TZ
)

NOW_DATA = datetime.datetime.now(MADRID_TZ)
NOW = NOW_DATA.strftime(DATETIME_FORMAT)

# Paths
PROJECT_DIR = pathlib.Path.cwd()

SHAREPOINT_REMOTE_BASE_DIR = pathlib.Path("_Projects/imarina-load-researchers/runtime")

INPUT_DIR_NAME = "input"
OUTPUT_DIR_NAME = "output"
A3_DUMPS_DIR_NAME = "a3"
PUBLISHED_DIR_NAME = "published"
IMARINA_DIR_NAME = "imarina"

LOCAL_INPUT_DIR = PROJECT_DIR / INPUT_DIR_NAME
LOCAL_OUTPUT_DIR = PROJECT_DIR / OUTPUT_DIR_NAME
LOCAL_PUBLISHED_DIR = PROJECT_DIR / PUBLISHED_DIR_NAME

SHAREPOINT_REMOTE_INPUT_DIR = SHAREPOINT_REMOTE_BASE_DIR / INPUT_DIR_NAME
SHAREPOINT_REMOTE_OUTPUT_DIR = SHAREPOINT_REMOTE_BASE_DIR / OUTPUT_DIR_NAME
SHAREPOINT_REMOTE_A3_DIR = SHAREPOINT_REMOTE_BASE_DIR / A3_DUMPS_DIR_NAME
SHAREPOINT_REMOTE_PUBLISHED_DIR = SHAREPOINT_REMOTE_BASE_DIR / PUBLISHED_DIR_NAME
# Where `download` re-uploads its iMarina fallback selection (see STEPS.md's
# "Preparation (download)" section for why this is a copy, not just a link).
SHAREPOINT_REMOTE_IMARINA_DIR = SHAREPOINT_REMOTE_BASE_DIR / IMARINA_DIR_NAME

SHAREPOINT_LOCAL_BASE_DIR = PROJECT_DIR / "services/onedrive/data"

SHAREPOINT_LOCAL_INPUT_DIR = SHAREPOINT_LOCAL_BASE_DIR / SHAREPOINT_REMOTE_INPUT_DIR
SHAREPOINT_LOCAL_OUTPUT_DIR = SHAREPOINT_LOCAL_BASE_DIR / SHAREPOINT_REMOTE_OUTPUT_DIR
SHAREPOINT_LOCAL_A3_DIR = SHAREPOINT_LOCAL_BASE_DIR / SHAREPOINT_REMOTE_A3_DIR
SHAREPOINT_LOCAL_PUBLISHED_DIR = (
    SHAREPOINT_LOCAL_BASE_DIR / SHAREPOINT_REMOTE_PUBLISHED_DIR
)

ICIQ_WEBPAGE = "https://iciq.org/"

FTP_FILENAME = "icl_ag_personal_12539.xlsx"

# `build` names its output "<DATETIME>__<FTP_FILENAME>" (see OUTPUT_FILENAME
# below) - these must stay in sync with that so select_file_to_upload() can
# actually parse the datetime back out of real output filenames.
FILENAME_PREFIX = ""
FILENAME_SUFFIX = f"__{FTP_FILENAME}"

FTP_UPLOAD_PATH = f"carga_icolet/{FTP_FILENAME}"

DEFAULT_LOG_PATH = PROJECT_DIR / "logs" / f"{NOW}.log"


SHAREPOINT_INPUT_DIR = SHAREPOINT_REMOTE_BASE_DIR / INPUT_DIR_NAME

TRANSLATION_FILES = {
    "countries": "Pais nacimiento _ [A3] to País de Nacimiento [iMarina].xlsx",
    "jobs": "Puesto de trabajo [A3] to Categoría Investigadora Docente [iMarina].xlsx",
    "personal_web": "Grupo Unidad [A3] to Web personal [iMarina].xlsx",
    "unit_group": "Grupo Unidad [A3] to Entidad (Nivel 1) [iMarina].xlsx",
    "unit_type": "Entidad (Nivel 1) [iMarina] to Tipo de Entidad [iMarina].xlsx",
    "job_description_entity": "Puesto de trabajo [A3] to Entidad (Nivel 1) [iMarina].xlsx",
    "sex": "Sexo [A3] to Sexo [iMarina].xlsx",
}

# Single source of truth for the input files `build` needs and `download` must
# provide, under these exact names, in the same flat directory (default:
# PROJECT_DIR / "input"). Keyed by role so callers can refer to files by
# meaning rather than repeating literal filenames.
REQUIRED_INPUT_FILES = {"a3": "A3.xlsx", "imarina": "iMarina.xlsx"}
REQUIRED_INPUT_FILES.update(TRANSLATION_FILES)


# --- CLI option defaults ---
# Kept alongside the constants they're derived from (INPUT_DIR, NOW,
# REQUIRED_INPUT_FILES above) rather than in core/shared_options.py, which
# holds only `*Opt` CLI metadata. Controllers reference these directly:
# `param: SomeOpt = DEFAULT_SOME` (see "Adding a new CLI option" in
# CLAUDE.md).

# --- build ---
OUTPUT_FILENAME = NOW + "__" + FTP_FILENAME

DEFAULT_COUNTRIES_DICT = LOCAL_INPUT_DIR / REQUIRED_INPUT_FILES["countries"]
DEFAULT_JOBS_DICT = LOCAL_INPUT_DIR / REQUIRED_INPUT_FILES["jobs"]
DEFAULT_IMARINA_INPUT = LOCAL_INPUT_DIR / REQUIRED_INPUT_FILES["imarina"]
DEFAULT_A3_INPUT = LOCAL_INPUT_DIR / REQUIRED_INPUT_FILES["a3"]
DEFAULT_OUTPUT_PATH = LOCAL_OUTPUT_DIR / OUTPUT_FILENAME
DEFAULT_PERSONAL_WEB_PATH = LOCAL_INPUT_DIR / REQUIRED_INPUT_FILES["personal_web"]
DEFAULT_UNIT_GROUP_PATH = LOCAL_INPUT_DIR / REQUIRED_INPUT_FILES["unit_group"]
DEFAULT_ENTITY_TYPE_PATH = LOCAL_INPUT_DIR / REQUIRED_INPUT_FILES["unit_type"]
DEFAULT_JOB_DESCRIPTION_ENTITY_PATH = (
    LOCAL_INPUT_DIR / REQUIRED_INPUT_FILES["job_description_entity"]
)
DEFAULT_SEX_PATH = LOCAL_INPUT_DIR / REQUIRED_INPUT_FILES["sex"]

# --- publish ---

# None => publish_controller falls back to select_file_to_upload(), which
# autodetects the latest build output in SHAREPOINT_LOCAL_OUTPUT_DIR.
DEFAULT_PUBLISH_FILE_PATH = None
DEFAULT_DRY_RUN = True

# --- upload ---

# None => upload_controller falls back to select_file_to_upload(), which
# autodetects the latest build output in SHAREPOINT_LOCAL_OUTPUT_DIR.
DEFAULT_PUBLISHED_FILE_PATH = None
DEFAULT_TARGET_DIR = LOCAL_OUTPUT_DIR

# --- notify ---

DEFAULT_NOTIFY_SHAREPOINT_PATH = DEFAULT_TARGET_DIR
