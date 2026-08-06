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
from typing import Any

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
) -> Any:
    r: dict[Any, dict[str, str]] = {}
    r[A3_Field.SEX] = {}
    r[A3_Field.SEX]["Mujer"] = "Female"
    r[A3_Field.SEX]["Hombre"] = "Male"

    r[A3_Field.COUNTRY] = {}
    countries = build_translator(countries_path)
    logger.debug(" -LOADED COUNTRIES FROM EXCEL- ")
    logger.debug(f"Path: {countries_path}")
    logger.debug(f"Countries dict: {countries}")
    logger.debug(f"Number of entries: {len(countries)}")

    for key in countries:
        r[A3_Field.COUNTRY][key] = countries[key]

    r[A3_Field.JOB_DESCRIPTION] = {}
    jobs = build_translator(jobs_path)
    for key in jobs:
        r[A3_Field.JOB_DESCRIPTION][key] = jobs[key]

    r[A3_Field.PERSONAL_WEB] = {}
    personal_webs = build_translator(personal_web_path, 1)
    for key in personal_webs:
        r[A3_Field.PERSONAL_WEB][key] = personal_webs[key]

    r[A3_Field.UNIT_GROUP] = {}
    unit_groups = build_translator(unit_group_path, 1)
    for key in unit_groups:
        r[A3_Field.UNIT_GROUP][key] = unit_groups[key]

    r[A3_Field.ENTITY_TYPE] = {}
    entity_types = build_translator(entity_type_path, 1)
    for key in entity_types:
        r[A3_Field.ENTITY_TYPE][key] = entity_types[key]

    r[A3_Field.JOB_DESCRIPTION_ENTITY] = {}
    job_description_entities = build_translator(job_description_entity_path, 1)
    for key in job_description_entities:
        r[A3_Field.JOB_DESCRIPTION_ENTITY][key] = job_description_entities[key]
    return r


# function to build the translator
def build_translator(path: str, skiprows: int = 0) -> dict[str, str]:
    excel = Excel(Path(path), skiprows, None)

    excel.dataframe.iloc[:, 0] = excel.dataframe.iloc[:, 0]
    excel.dataframe.iloc[:, 1] = excel.dataframe.iloc[:, 1]

    return excel.parse_two_columns(0, 1)
