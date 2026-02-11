from imarina.core.excel import Excel
from imarina.core.a3_mapper import A3_Field
from imarina.core.log_utils import get_logger
from pathlib import Path
from typing import Any
logger = get_logger(__name__)


def build_translations(
        countries_path: str,
        jobs_path: str,
        personal_web_path: str,
        unit_group_path: str,
        entity_type_path: str,
        job_description_entity_path: str,
) -> Any :
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

    for key in countries.keys():
        r[A3_Field.COUNTRY][key] = countries[key]

    r[A3_Field.JOB_DESCRIPTION] = {}
    jobs = build_translator(jobs_path)
    for key in jobs.keys():
        r[A3_Field.JOB_DESCRIPTION][key] = jobs[key]

    r[A3_Field.PERSONAL_WEB] = {}
    personal_webs = build_translator(personal_web_path, 1)
    for key in personal_webs.keys():
        r[A3_Field.PERSONAL_WEB][key] = personal_webs[key]

    r[A3_Field.UNIT_GROUP] = {}
    unit_groups = build_translator(unit_group_path, 1)
    for key in unit_groups.keys():
        r[A3_Field.UNIT_GROUP][key] = unit_groups[key]

    r[A3_Field.ENTITY_TYPE] = {}
    entity_types = build_translator(entity_type_path, 1)
    for key in entity_types.keys():
        r[A3_Field.ENTITY_TYPE][key] = entity_types[key]

    r[A3_Field.JOB_DESCRIPTION_ENTITY] = {}
    job_description_entities = build_translator(job_description_entity_path, 1)
    for key in job_description_entities.keys():
        r[A3_Field.JOB_DESCRIPTION_ENTITY][key] = job_description_entities[key]
    return r


# function to build the translator
def build_translator(path: str, skiprows: int = 0) -> dict[str, str]:
    excel = Excel(Path(path), skiprows, None)

    excel.dataframe.iloc[:, 0] = excel.dataframe.iloc[:, 0]
    excel.dataframe.iloc[:, 1] = excel.dataframe.iloc[:, 1]

    return excel.parse_two_columns(0, 1)
