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

import typer

from imarina.core.defines import (
    DEFAULT_A3_INPUT,
    DEFAULT_COUNTRIES_DICT,
    DEFAULT_ENTITY_TYPE_PATH,
    DEFAULT_IMARINA_INPUT,
    DEFAULT_JOB_DESCRIPTION_ENTITY_PATH,
    DEFAULT_JOBS_DICT,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_PERSONAL_WEB_PATH,
    DEFAULT_SEX_PATH,
    DEFAULT_UNIT_GROUP_PATH,
)
from imarina.core.imarina_excel import build_upload_excel
from imarina.core.log_utils import get_logger
from imarina.core.shared_options import (
    A3InputOpt,
    CountriesDictOpt,
    EntityTypePathOpt,
    ImarinaInputOpt,
    JobDescriptionEntityPathOpt,
    JobsDictOpt,
    OutputPathOpt,
    PersonalWebPathOpt,
    SexPathOpt,
    UnitGroupPathOpt,
)
from imarina.core.translations import TranslationDictionaryPaths

logger = get_logger(__name__)


def build_controller(  # noqa: PLR0913, PLR0917
        ctx: typer.Context,
        countries_dict: CountriesDictOpt = DEFAULT_COUNTRIES_DICT,
        jobs_dict: JobsDictOpt = DEFAULT_JOBS_DICT,
        imarina_input: ImarinaInputOpt = DEFAULT_IMARINA_INPUT,
        a3_input: A3InputOpt = DEFAULT_A3_INPUT,
        output_path: OutputPathOpt = DEFAULT_OUTPUT_PATH,
        personal_web_path: PersonalWebPathOpt = DEFAULT_PERSONAL_WEB_PATH,
        unit_group_path: UnitGroupPathOpt = DEFAULT_UNIT_GROUP_PATH,
        entity_type_path: EntityTypePathOpt = DEFAULT_ENTITY_TYPE_PATH,
        job_description_entity_path: JobDescriptionEntityPathOpt = DEFAULT_JOB_DESCRIPTION_ENTITY_PATH,
        sex_path: SexPathOpt = DEFAULT_SEX_PATH
) -> None:
    build_upload_excel(
        output_path,
        imarina_input,
        a3_input,
        TranslationDictionaryPaths(
            countries_path=countries_dict,
            jobs_path=jobs_dict,
            personal_web_path=personal_web_path,
            unit_group_path=unit_group_path,
            entity_type_path=entity_type_path,
            job_description_entity_path=job_description_entity_path,
            sex_path=sex_path,
        ),
    )

