import re
from datetime import date, datetime

import pandas as pd

from imarina.core.Researcher import is_same_person, has_changed_jobs, is_visitor
from imarina.core.a3_mapper import A3_Field, parse_a3_row_data
from imarina.core.defines import PERMANENT_CONTRACT_DATE
from imarina.core.excel import Excel
from imarina.core.imarina_mapper import parse_imarina_row_data, unparse_researcher_to_imarina_row
from imarina.core.log_utils import get_logger
from imarina.core.str_utils import normalize_name_str
from imarina.core.translations import build_translator

logger = get_logger(__name__)



#normalized dni
def normalized_dni(dni):
    if not dni:
        return ""
    dni = re.sub(r"[^0-9A-Za-z]", "", str(dni)).upper()
    dni = dni.lstrip("0")   # remove leading zeros
    return dni


# search coincidencies
def search_data(query, data_input, parser, translator):

    # strict_matches = []  # los matches se guardan aqui (strict matches)
    # fuzzy_matches = [] # matches que pueden ser difusos  (fuzzy matches)
    matches = []

    for index, row in data_input.iterrows():
        # parser row
        row_data = parser(row, translator)

        # normalize name
        if normalize_name_str(query.name) == normalize_name_str(row_data.name):
            matches.append(row_data)
            continue

            # comprova la funció is_same_person
        if is_same_person(query, row_data):
            matches.append(row_data)

    if matches:
        same_ini = [r for r in matches if r.ini_date == query.ini_date]
        return same_ini if len(same_ini) == 1 else matches

    return []


#LOGIC AND PHASES TO BUILD AND UPLOAD EXCEL
def build_upload_excel(output_path, countries_path, jobs_path, imarina_path, a3_path, personal_web_path):
    today = date.today()

    # Get A3 data
    a3_data = Excel(a3_path, skiprows=2, header=0)

    # Get iMarina last upload data
    im_data = Excel(imarina_path, header=0)

    # retains columns, types, and headers if any
    empty_row_output_data = im_data.__copy__()
    empty_row_output_data.empty()
    output_data = empty_row_output_data.__copy__()

    num_changed = 0
    num_left = 0
    num_new = 0
    num_visitors = 0

    # load the translators fields: country, job_description
    translator = {A3_Field.COUNTRY: build_translator(countries_path),
                  A3_Field.JOB_DESCRIPTION: build_translator(jobs_path),
                  A3_Field.PERSONAL_WEB: build_translator(personal_web_path)}



    logger.info("Phase 1: Check if the researchers in last upload to iMarina are still in A3")
    not_present = 0
    for index, row in im_data.dataframe.iterrows():
        logger.debug("\n\nCurrently processing data from iMarina excel row number {str(index)}")
        researcher_imarina = parse_imarina_row_data(row, translator)
        logger.debug(f"Parsed data from iMarina row is: {str(researcher_imarina)}")
        researchers_matched_a3 = search_data(researcher_imarina, a3_data.dataframe, parse_a3_row_data, translator)

        empty_row = empty_row_output_data.__copy__()

        if len(researchers_matched_a3) == 0:
            num_left += 1
            logger.debug("The current researcher is not present in A3 meaning the researcher is no longer in ICIQ.")
            logger.debug("Adding researcher data into output with end date of today")
            if researcher_imarina.end_date is None:
                researcher_imarina.end_date = today  # Use end time already in iMarina if present, if not, set to today
            new_row = empty_row_output_data.__copy__()

            unparse_researcher_to_imarina_row(researcher_imarina, new_row)
            logger.trace(f"Row added to iMarina upload Excel is {str(new_row)}")
            output_data.concat(new_row)

            not_present += 1
        elif len(researchers_matched_a3) == 1:
            logger.debug("The current researcher is still present in A3 meaning the researcher is still in ICIQ.")
            researcher_a3 = researchers_matched_a3[0]
            logger.debug(f"Matched A3 researcher is {str(researcher_a3)}")
            if researcher_a3.end_date is not None and researcher_a3.end_date != PERMANENT_CONTRACT_DATE:
                logger.debug("Current researcher has a temporary contract.")

                if has_changed_jobs(researcher_a3, researcher_imarina, translator):
                    num_changed += 1
                    logger.debug("Current researcher has changed its position within ICIQ since last upload.")
                    logger.debug("Adding new row from A3 with the data of the new position.")
                    new_row = empty_row_output_data.__copy__()
                    unparse_researcher_to_imarina_row(researcher_a3, new_row)
                    logger.trace(f"Row added to iMarina upload Excel is {str(new_row)}")
                    output_data.concat(new_row)

                else:
                    logger.debug("Current researcher is still working in the same position since last upload.")
                    logger.debug("Adding new row from iMarina with the same data.")

                    # No cambió entonces mantener la fila actual
                    # If it has not changed, add current iMarina row to output as is.
                    # (end date not present) it is a contract that could be still ongoing continue
                    new_row = empty_row_output_data.__copy__()
                    unparse_researcher_to_imarina_row(researcher_imarina, new_row)
                    logger.debug(f"Row added to iMarina upload Excel is {str(new_row)}")
                    output_data.concat(new_row)
                continue
            else:
                logger.debug("Current researcher has permanent contract.")
                logger.debug("Current researcher is still working in the same position since last upload.")
                logger.debug("Adding new row from iMarina with the same data.")
                unparse_researcher_to_imarina_row(researcher_imarina, empty_row)
                output_data.concat(empty_row)

    # Phase 2: Add researchers in A3 that are not present in iMarina
    for index, row in a3_data.dataframe.iterrows():
        researcher_a3 = parse_a3_row_data(row, translator)
        researchers_matched_im = search_data(researcher_a3, im_data.dataframe, parse_imarina_row_data, translator) #find researcher_a3 have exist in iMarina
        empty_row = empty_row_output_data.__copy__()  # prepare a empty row just in case i need dates

        logger.debug(
            f"{researcher_a3.name}: code_center={researcher_a3.code_center}, ini_date={researcher_a3.ini_date}, end_date={researcher_a3.end_date}")
        logger.debug(f"Visitante: {is_visitor(researcher_a3)}")

        if is_visitor(researcher_a3):
            num_visitors += 1
            continue

        if len(researchers_matched_im) == 0:     #the researcher_a3  is new and is not in iMarina
            num_new += 1
            logger.debug(f"Present in A3 but not on iMarina, is a new researcher to add to iMarina")
            unparse_researcher_to_imarina_row(researcher_a3, empty_row)
            output_data.concat(empty_row)
        else:
            logger.debug(f"Present in A3 and also on iMarina - already processed in Phase 1")
            # No hacer nada, ya fue procesado en Phase 1

    logger.info(f"Since the last upload, {num_changed} researchers have changed its position within ICIQ.")
    logger.info(f"Since the last upload, {num_visitors} researchers have visited ICIQ.")
    logger.info(f"Since the last upload, {num_left} researchers have left ICIQ.")
    logger.info(f"Since the last upload, {num_new} researchers have entered ICIQ.")


    # Si grupo  unidad = DIRECCIO, o grupo unidad = GESTIO, o grupo unidad = OUTREACH llavors eliminar del output ( no poner)

    # For each researcher in A3, check if they are not present in iMarina
    # If they are not present, it has a code 4, it begins and end date is outside a range
    # to determine from fields to determine, then the current row from A3 corresponds to ICREA researcher or predoc
    # with CSC, so its data from A3 needs to be added to the output.

    output_data.dataframe.to_excel(output_path, index=False)
