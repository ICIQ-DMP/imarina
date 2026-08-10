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

from pathlib import Path

from imarina.core.a3_mapper import A3_Field
from imarina.core.excel import Excel
from imarina.core.log_utils import get_logger

logger = get_logger(__name__)


def build_translations(
    countries_path: str,
    jobs_path: str,
    personal_web_path: str,
    unit_group_path: str,
    entity_type_path: str,
    job_description_entity_path: str,
) -> dict[A3_Field, dict[str, str]]:
    countries = build_translator(countries_path)
    logger.debug(" -LOADED COUNTRIES FROM EXCEL- ")
    logger.debug(f"Path: {countries_path}")
    logger.debug(f"Countries dict: {countries}")
    logger.debug(f"Number of entries: {len(countries)}")

    return {
        A3_Field.SEX: {"Mujer": "Female", "Hombre": "Male"},
        A3_Field.COUNTRY: dict(countries),
        A3_Field.JOB_DESCRIPTION: dict(build_translator(jobs_path)),
        A3_Field.PERSONAL_WEB: dict(build_translator(personal_web_path, 1)),
        A3_Field.UNIT_GROUP: dict(build_translator(unit_group_path, 1)),
        A3_Field.ENTITY_TYPE: dict(build_translator(entity_type_path, 1)),
        A3_Field.JOB_DESCRIPTION_ENTITY: dict(
            build_translator(job_description_entity_path, 1)
        ),
    }


# function to build the translator
def build_translator(path: str, skiprows: int = 0) -> dict[str, str]:
    excel = Excel(Path(path), skiprows, None)
    return excel.parse_two_columns(0, 1)
