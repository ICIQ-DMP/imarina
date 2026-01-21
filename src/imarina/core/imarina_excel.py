import re
from pathlib import Path

from imarina.core.a3_mapper import A3_Field, parse_a3_row_data
from imarina.core.defines import PERMANENT_CONTRACT_DATE, NOW_DATA

from imarina.core.imarina_mapper import (
    parse_imarina_row_data, append_researchers_to_output_data,
)
from imarina.core.log_utils import get_logger
from imarina.core.translations import build_translator, build_translations

logger = get_logger(__name__)

from imarina.core.excel import Excel


def normalized_dni(dni):
    if not dni:
        return ""
    dni = re.sub(r"[^0-9A-Za-z]", "", str(dni)).upper()
    dni = dni.lstrip("0")  # remove leading zeros
    return dni


# constructor del excel
def build_upload_excel(
    output_path: Path,
    countries_path,
    jobs_path,
    imarina_path,
    a3_path,
    personal_web_path,
    unit_group_path,
    entity_type_path,
):
    # Get A3 data
    a3_data = Excel(a3_path, skiprows=2, header=0)

    # Get iMarina last upload data
    im_data = Excel(imarina_path, header=0)

    # load the translators fields: country, job_description
    translator = build_translations(
        countries_path=countries_path,
        jobs_path=jobs_path,
        personal_web_path=personal_web_path,
        unit_group_path=unit_group_path,
        entity_type_path=entity_type_path,
    )

    researchers_left = []
    researchers_visitor = []
    researchers_new = []
    researchers_changed = []
    researchers_output = []

    im_researchers = []
    for index, row in im_data.dataframe.iterrows():
        im_researchers.append(parse_imarina_row_data(row))

    a3_researchers = []
    for index, row in a3_data.dataframe.iterrows():
        a3_researchers.append(parse_a3_row_data(row, translator))

    logger.info(
        "Phase 1: Check if the researchers in last upload to iMarina are still in A3"
    )
    for researcher_imarina in im_researchers:
        logger.debug(f"Parsed data from iMarina row is: {str(researcher_imarina)}")
        researchers_matched_a3 = researcher_imarina.search_data(a3_researchers)

        if len(researchers_matched_a3) == 0:
            logger.debug(
                "The current researcher is not present in A3 meaning the researcher is no longer in ICIQ."
            )
            logger.debug("Adding researcher data into output with end date of today")
            if researcher_imarina.end_date is None:
                researcher_imarina.end_date = NOW_DATA  # Use end time already in iMarina if present, if not, set to today
            researchers_left.append(researcher_imarina)
            researchers_output.append(researcher_imarina)
        elif len(researchers_matched_a3) == 1:

            logger.debug(
                "The current researcher is still present in A3 meaning the researcher is still in ICIQ."
            )
            researcher_a3 = researchers_matched_a3[0]
            logger.debug(f"Matched A3 researcher is {str(researcher_a3)}")
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

                # No cambió entonces mantener la fila actual
                # If it has not changed, add current iMarina row to output as is.
                # (end date not present) it is a contract that could be still ongoing continue
                researchers_output.append(researcher_imarina)
        else:
            logger.warning("More than one researcher matched in a3:")
            for res in researchers_matched_a3:
                logger.debug(res)

        # input("Press Enter to continue...")

    logger.info("Phase 2: Add researchers in A3 that are not present in iMarina")
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
            # No hacer nada, ya fue procesado en Phase 1

    for researcher in researchers_output:
        if researcher.is_visitor():
            researchers_visitor.append(researcher)

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
    # TODO UNIQUE LANGUAGE PREF ENGLISH
    # For each researcher in A3, check if they are not present in iMarina
    # If they are not present, it has a code 4, it begins and end date is outside a range
    # to determine from fields to determine, then the current row from A3 corresponds to ICREA researcher or predoc
    # with CSC, so its data from A3 needs to be added to the output.
    # retains columns, types, and headers if any

    im_data_empty = im_data.__copy__()
    im_data_empty.empty()
    output_path_str = str(output_path)

    excel_output = im_data_empty.__copy__()
    append_researchers_to_output_data(researchers_output, excel_output)
    excel_output.to_excel(Path(output_path))

    '''


    excel_left = im_data_empty.__copy__()
    append_researchers_to_output_data(researchers_left, excel_left)
    excel_left.to_excel(Path(output_path_str + "left.xlsx"))

    excel_visitor = im_data_empty.__copy__()
    append_researchers_to_output_data(researchers_visitor, excel_visitor)
    excel_visitor.to_excel(Path(output_path_str + "visitor.xlsx"))

    excel_new = im_data_empty.__copy__()
    append_researchers_to_output_data(researchers_new, excel_new)
    excel_new.to_excel(Path(output_path_str + "new.xlsx"))

    excel_changed = im_data_empty.__copy__()
    append_researchers_to_output_data(researchers_changed, excel_changed)
    excel_changed.to_excel(Path(output_path_str + "changed.xlsx"))
    '''

