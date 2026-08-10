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

from dataclasses import dataclass
from pathlib import Path

from imarina.core.a3_mapper import A3Field
from imarina.core.excel import Excel
from imarina.core.log_utils import get_logger

logger = get_logger(__name__)


@dataclass
class TranslationDictionaryPaths:
    countries_path: Path
    jobs_path: Path
    personal_web_path: Path
    unit_group_path: Path
    entity_type_path: Path
    job_description_entity_path: Path
    sex_path: Path

    def to_a3_field_map(self) -> dict[A3Field, Path]:
        return {
            A3Field.COUNTRY: self.countries_path,
            A3Field.JOB_DESCRIPTION: self.jobs_path,
            A3Field.PERSONAL_WEB: self.personal_web_path,
            A3Field.UNIT_GROUP: self.unit_group_path,
            A3Field.ENTITY_TYPE: self.entity_type_path,
            A3Field.JOB_DESCRIPTION_ENTITY: self.job_description_entity_path,
            A3Field.SEX: self.sex_path,
        }


def build_translations(
    paths: TranslationDictionaryPaths,
) -> dict[A3Field, dict[str, str]]:
    return {
        field: dict(build_translator(path, 1))
        for field, path in paths.to_a3_field_map().items()
    }


# function to build the translator
def build_translator(path: Path, skiprows: int = 0) -> dict[str, str]:
    excel = Excel(path, skiprows, None)
    return excel.parse_two_columns(0, 1)
