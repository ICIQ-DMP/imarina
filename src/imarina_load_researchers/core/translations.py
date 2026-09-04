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

from dataclasses import dataclass
from pathlib import Path

from imarina_load_researchers.core.a3_mapper import (
    A3Field,
    Translator,
    normalize_country_name,
)
from imarina_load_researchers.core.excel import Excel
from imarina_load_researchers.core.log_utils import get_logger

logger = get_logger(__name__)


@dataclass
class TranslationDictionaryPaths:
    """Paths to the static two-column translation-dictionary spreadsheets
    `build` needs, one per `A3Field` that requires an A3→iMarina translation."""

    countries_path: Path
    jobs_path: Path
    personal_web_path: Path
    unit_group_path: Path
    entity_type_path: Path
    job_description_entity_path: Path
    sex_path: Path

    def to_a3_field_map(self) -> dict[A3Field, Path]:
        """
        Maps each translated `A3Field` to its dictionary spreadsheet's path.

        Returns:
            dict[A3Field, Path]: The `{A3Field: dictionary path}` mapping.
        """
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
) -> Translator:
    """
    Loads every A3→iMarina translation dictionary into one `Translator`.

    Args:
        paths (TranslationDictionaryPaths): Paths to the dictionary
            spreadsheets to load.

    Returns:
        Translator: The `{A3Field: {raw_value: translated_value}}`
            dictionaries, with `A3Field.COUNTRY` pre-normalized (via
            `normalize_country_name`) so `a3_mapper`'s per-row lookups don't
            have to re-normalize it on every researcher row.
    """
    translations = {
        field: dict(build_translator(path, 1))
        for field, path in paths.to_a3_field_map().items()
    }
    # Normalized once here so a3_mapper's per-row country lookups don't have to
    # rebuild this from the raw dict on every researcher row.
    translations[A3Field.COUNTRY] = {
        normalize_country_name(k): v.strip()
        for k, v in translations[A3Field.COUNTRY].items()
    }
    return translations


# function to build the translator
def build_translator(path: Path, skiprows: int = 0) -> dict[str, str]:
    """
    Loads a two-column dictionary spreadsheet into a `{raw: translated}` dict.

    Args:
        path (Path): Path to the two-column dictionary spreadsheet.
        skiprows (int): Number of leading rows to skip (e.g. a header row).

    Returns:
        dict[str, str]: The first column mapped to the second, as a dict.
    """
    excel = Excel(path, skiprows, None)
    return excel.parse_two_columns(0, 1)
