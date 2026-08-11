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
NOW_DATA = datetime.datetime.now(MADRID_TZ)
NOW = NOW_DATA.strftime(DATETIME_FORMAT)

PROJECT_DIR = pathlib.Path.cwd()

INPUT_FOLDER_NAME = "input"
OUTPUT_FOLDER_NAME = "output"

INPUT_DIR = PROJECT_DIR / INPUT_FOLDER_NAME
OUTPUT_DIR = PROJECT_DIR / OUTPUT_FOLDER_NAME
date_str = "31/12/2099"
DATE_FORMAT = "%d/%m/%Y"
PERMANENT_CONTRACT_DATE = datetime.datetime.strptime(date_str, "%d/%m/%Y").replace(
    tzinfo=MADRID_TZ
)
ICIQ_WEBPAGE = "https://iciq.org/"

FILENAME_PREFIX = "iMarina_upload_"
FILENAME_SUFFIX = ".xlsx"
FTP_FILENAME = "icl_ag_personal_12539.xlsx"

FTP_UPLOAD_PATH = f"carga_icolet/{FTP_FILENAME}"

DEFAULT_LOG_PATH = PROJECT_DIR / "logs" / f"{NOW}.log"

SHAREPOINT_BASE_FOLDER = pathlib.Path("_Projects/imarina-load-researchers")

SHAREPOINT_INPUT_FOLDER = SHAREPOINT_BASE_FOLDER / INPUT_FOLDER_NAME

TRANSLATION_FILES = {
    "countries": "Pais nacimiento _ [A3] to País de Nacimiento [iMarina].xlsx",
    "jobs": "Puesto de trabajo [A3] to Categoría Investigadora Docente [iMarina].xlsx",
    "personal_web": "Puesto de trabajo [A3] to Web personal [iMarina].xlsx",
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

DEFAULT_COUNTRIES_DICT = INPUT_DIR / REQUIRED_INPUT_FILES["countries"]
DEFAULT_JOBS_DICT = INPUT_DIR / REQUIRED_INPUT_FILES["jobs"]
DEFAULT_IMARINA_INPUT = INPUT_DIR / REQUIRED_INPUT_FILES["imarina"]
DEFAULT_A3_INPUT = INPUT_DIR / REQUIRED_INPUT_FILES["a3"]
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / OUTPUT_FILENAME
DEFAULT_PERSONAL_WEB_PATH = INPUT_DIR / REQUIRED_INPUT_FILES["personal_web"]
DEFAULT_UNIT_GROUP_PATH = INPUT_DIR / REQUIRED_INPUT_FILES["unit_group"]
DEFAULT_ENTITY_TYPE_PATH = INPUT_DIR / REQUIRED_INPUT_FILES["unit_type"]
DEFAULT_JOB_DESCRIPTION_ENTITY_PATH = (
    INPUT_DIR / REQUIRED_INPUT_FILES["job_description_entity"]
)
DEFAULT_SEX_PATH = INPUT_DIR / REQUIRED_INPUT_FILES["sex"]

# --- publish ---

DEFAULT_PUBLISH_FILE_PATH = OUTPUT_DIR / FTP_FILENAME
DEFAULT_DRY_RUN = True

# --- upload ---

DEFAULT_UPLOAD_FILE_PATH = OUTPUT_DIR / FTP_FILENAME
DEFAULT_TARGET_FOLDER = SHAREPOINT_BASE_FOLDER / OUTPUT_FOLDER_NAME

# --- notify ---

DEFAULT_NOTIFY_SHAREPOINT_PATH = DEFAULT_TARGET_FOLDER
