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

from pathlib import Path

import typer

from imarina_load_researchers.core.defines import (
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
    REQUIRED_INPUT_FILES,
)
from imarina_load_researchers.core.imarina_excel import build_upload_excel
from imarina_load_researchers.core.log_utils import get_logger
from imarina_load_researchers.core.shared_options import (
    A3InputOpt,
    CountriesDictOpt,
    EntityTypePathOpt,
    IdOpt,
    ImarinaInputOpt,
    InputDirOpt,
    JobDescriptionEntityPathOpt,
    JobsDictOpt,
    OutputPathOpt,
    PersonalWebPathOpt,
    SexPathOpt,
    UnitGroupPathOpt,
)
from imarina_load_researchers.core.sharepoint import update_list_item_fields
from imarina_load_researchers.core.sharepoint_fields import (
    FIELD_WORKFLOW_STATE,
    WorkflowState,
)
from imarina_load_researchers.core.translations import TranslationDictionaryPaths

logger = get_logger(__name__)


def _resolve_input_path(
    explicit_path: Path | None, role: str, input_dir: Path | None, default: Path
) -> Path:
    """Resolve one of build's input file paths.

    Precedence: the file's own explicit path option (highest) > --input-dir
    joined with the file's standard name (REQUIRED_INPUT_FILES) > the
    existing ./input-based default (lowest).
    """
    if explicit_path is not None:
        return explicit_path
    if input_dir is not None:
        return input_dir / REQUIRED_INPUT_FILES[role]
    return default


def build_controller(  # noqa: PLR0913, PLR0917
        ctx: typer.Context,
        countries_dict: CountriesDictOpt = None,
        jobs_dict: JobsDictOpt = None,
        imarina_input: ImarinaInputOpt = None,
        a3_input: A3InputOpt = None,
        output_path: OutputPathOpt = DEFAULT_OUTPUT_PATH,
        personal_web_path: PersonalWebPathOpt = None,
        unit_group_path: UnitGroupPathOpt = None,
        entity_type_path: EntityTypePathOpt = None,
        job_description_entity_path: JobDescriptionEntityPathOpt = None,
        sex_path: SexPathOpt = None,
        input_dir: InputDirOpt = None,
        id_element: IdOpt = None,
) -> None:
    """Build the next iMarina upload from the 9 REQUIRED_INPUT_FILES roles.

    Each file's path is resolved independently: its own explicit option
    (e.g. --countries-dict) wins if given; otherwise, if --input-dir is
    given, the file is looked up there under its standard name
    (REQUIRED_INPUT_FILES); otherwise it falls back to ./input, as before.

    `id_element`, if given, is used for nothing other than updating the
    request's Workflow State field to "Building" (see CLAUDE.md's "Microsoft
    List schema" section) — it plays no part in resolving input/output files.
    """
    if id_element is not None:
        try:
            update_list_item_fields(
                str(id_element), {FIELD_WORKFLOW_STATE: WorkflowState.BUILDING}
            )
        except Exception:
            # Best-effort bookkeeping: must not block the actual build below.
            logger.exception("Error updating Workflow State to Building")

    build_upload_excel(
        output_path,
        _resolve_input_path(imarina_input, "imarina", input_dir, DEFAULT_IMARINA_INPUT),
        _resolve_input_path(a3_input, "a3", input_dir, DEFAULT_A3_INPUT),
        TranslationDictionaryPaths(
            countries_path=_resolve_input_path(
                countries_dict, "countries", input_dir, DEFAULT_COUNTRIES_DICT
            ),
            jobs_path=_resolve_input_path(
                jobs_dict, "jobs", input_dir, DEFAULT_JOBS_DICT
            ),
            personal_web_path=_resolve_input_path(
                personal_web_path, "personal_web", input_dir, DEFAULT_PERSONAL_WEB_PATH
            ),
            unit_group_path=_resolve_input_path(
                unit_group_path, "unit_group", input_dir, DEFAULT_UNIT_GROUP_PATH
            ),
            entity_type_path=_resolve_input_path(
                entity_type_path, "unit_type", input_dir, DEFAULT_ENTITY_TYPE_PATH
            ),
            job_description_entity_path=_resolve_input_path(
                job_description_entity_path,
                "job_description_entity",
                input_dir,
                DEFAULT_JOB_DESCRIPTION_ENTITY_PATH,
            ),
            sex_path=_resolve_input_path(sex_path, "sex", input_dir, DEFAULT_SEX_PATH),
        ),
    )

