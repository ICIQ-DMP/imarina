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

import re
from pathlib import Path
from typing import Any, cast

from imarina.core.a3_mapper import parse_a3_row_data
from imarina.core.defines import NOW_DATA, PERMANENT_CONTRACT_DATE
from imarina.core.excel import Excel
from imarina.core.imarina_mapper import (
    append_researchers_to_output_data,
    parse_imarina_row_data,
)
from imarina.core.log_utils import get_logger
from imarina.core.researcher import Researcher
from imarina.core.translations import TranslationDictionaryPaths, build_translations

logger = get_logger(__name__)


def normalized_dni(dni: str) -> str:
    if not dni:
        return ""
    dni = re.sub(r"[^0-9A-Za-z]", "", str(dni)).upper()
    dni = dni.lstrip("0")  # remove leading zeros
    return dni


def _match_last_upload_against_a3(
    im_researchers: list[Researcher], a3_researchers: list[Researcher]
) -> tuple[list[Researcher], list[Researcher], list[Researcher]]:
    """Phase 1: Check if the researchers in last upload to iMarina are still in A3.

    Returns (researchers_left, researchers_changed, researchers_output).
    """
    researchers_left: list[Researcher] = []
    researchers_changed: list[Researcher] = []
    researchers_output: list[Researcher] = []

    for researcher_imarina in im_researchers:
        logger.debug(f"Parsed data from iMarina row is: {researcher_imarina!s}")
        researchers_matched_a3 = researcher_imarina.search_data(a3_researchers)

        if len(researchers_matched_a3) == 0:
            logger.debug(
                "The current researcher is not present in A3 meaning the researcher is no longer in ICIQ."
            )
            logger.debug("Adding researcher data into output with end date of today")
            if researcher_imarina.end_date is None:
                # Use end time already in iMarina if present, if not, set to today
                researcher_imarina.end_date = NOW_DATA
            researchers_left.append(researcher_imarina)
            researchers_output.append(researcher_imarina)
        elif len(researchers_matched_a3) == 1:

            logger.debug(
                "The current researcher is still present in A3 meaning the researcher is still in ICIQ."
            )
            researcher_a3 = researchers_matched_a3[0]
            logger.debug(f"Matched A3 researcher is {researcher_a3!s}")
            if (
                researcher_a3.end_date is not None
                and researcher_a3.end_date != PERMANENT_CONTRACT_DATE
            ):
                logger.debug("Current researcher has a temporary contract.")
            else:
                logger.debug("Current researcher has a permanent contract.")
                researcher_a3.end_date = PERMANENT_CONTRACT_DATE

            if researcher_a3.has_changed_jobs(researcher_imarina):
                logger.debug(
                    "Current researcher has changed its position within ICIQ since last upload."
                )
                logger.debug(
                    "Adding new row from A3 with the data of the new position."
                )
                researchers_changed.append(researcher_a3)
                researchers_output.append(researcher_a3)

            else:
                logger.debug(
                    "Current researcher is still working in the same position since last upload."
                )
                logger.debug("Adding new row from iMarina with the same data.")

                # there was no change in maintaining the current queue
                # If it has not changed, add current iMarina row to output as is.
                # (end date not present) it is a contract that could be still ongoing continue
                researchers_output.append(researcher_imarina)
        else:
            logger.warning("More than one researcher matched in a3:")
            for res in researchers_matched_a3:
                logger.debug(res)

    return researchers_left, researchers_changed, researchers_output


def _find_new_researchers_in_a3(
    a3_researchers: list[Researcher], im_researchers: list[Researcher]
) -> tuple[list[Researcher], list[Researcher]]:
    """Phase 2: Add researchers in A3 that are not present in iMarina.

    Returns (researchers_new, researchers_output).
    """
    researchers_new: list[Researcher] = []
    researchers_output: list[Researcher] = []

    for researcher_a3 in a3_researchers:
        researchers_matched_im = researcher_a3.search_data(
            im_researchers
        )  # find researcher_a3 that exist in iMarina

        if (
            len(researchers_matched_im) == 0
        ):  # the researcher_a3  is new and is not in iMarina
            researchers_new.append(researcher_a3)
            researchers_output.append(researcher_a3)
        else:
            logger.debug(
                "Present in A3 and also on iMarina - already processed in Phase 1"
            )
            # No action, he has already been prosecuted in Phase 1

    return researchers_new, researchers_output


def build_upload_excel(
    output_path: Path,
    imarina_path: Path,
    a3_path: Path,
    translation_paths: TranslationDictionaryPaths,
) -> None:

    # Get A3 data
    a3_data = Excel(a3_path, skiprows=2, header=0)

    # Get iMarina last upload data
    im_data = Excel(imarina_path, header=0)

    # load the translators fields: country, job_description
    translator = build_translations(translation_paths)

    im_researchers = []
    for _index, row in im_data.dataframe.iterrows():
        im_researchers.append(parse_imarina_row_data(row))

    a3_researchers = []
    for _index, row in a3_data.dataframe.iterrows():
        a3_researchers.append(parse_a3_row_data(row, translator))

    logger.info(
        "Phase 1: Check if the researchers in last upload to iMarina are still in A3"
    )
    researchers_left, researchers_changed, researchers_output = (
        _match_last_upload_against_a3(im_researchers, a3_researchers)
    )

    logger.info("Phase 2: Add researchers in A3 that are not present in iMarina")
    researchers_new, researchers_output_phase2 = _find_new_researchers_in_a3(
        a3_researchers, im_researchers
    )
    researchers_output.extend(researchers_output_phase2)

    researchers_visitor = [
        researcher for researcher in researchers_output if researcher.is_visitor()
    ]

    num_changed = len(researchers_changed)
    num_left = len(researchers_left)
    num_new = len(researchers_new)
    num_visitors = len(researchers_visitor)

    logger.info(
        f"Since the last upload, {num_changed} researchers have changed its position within ICIQ."
    )
    logger.info(f"Since the last upload, {num_visitors} researchers have visited ICIQ.")
    logger.info(f"Since the last upload, {num_left} researchers have left ICIQ.")
    logger.info(f"Since the last upload, {num_new} researchers have entered ICIQ.")

    # IF GROUP UNIT = DIRECCIO OR GROUP UNIT = GESTIO OR GROUP UNIT = OUTREACH DELETE OF OUTPUT

    # For each researcher in A3, check if they are not present in iMarina
    # If they are not present, it has a code 4, it begins and end date is outside a range
    # to determine from fields to determine, then the current row from A3 corresponds to ICREA researcher or predoc
    # with CSC, so its data from A3 needs to be added to the output.
    # retains columns, types, and headers if any

    im_data_any = cast(
        Any, im_data
    )  # data cast pass variable type to any type to use copy method
    im_data_empty: Any = im_data_any.__copy__()
    im_data_empty.empty()

    excel_output = im_data_empty.__copy__()
    append_researchers_to_output_data(researchers_output, excel_output)
    excel_output.to_excel(Path(output_path))
