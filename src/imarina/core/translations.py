from imarina.core.excel import Excel
from src.imarina.core.a3_mapper import A3_Field
from src.imarina.core.log_utils import get_logger

logger = get_logger(__name__)


def build_translations(countries_path, jobs_path, personal_web_path):
    r = {A3_Field.SEX: {}}
    r[A3_Field.SEX]["Mujer"] = "Woman"
    r[A3_Field.SEX]["Hombre"] = "Man"

    r[A3_Field.COUNTRY] = {}
    countries = build_translator(countries_path)
    logger.debug(" -LOADED COUNTRIES FROM EXCEL- ")
    logger.debug("Path:", countries_path)
    logger.debug("Countries dict:", countries)
    logger.debug("Number of entries:", len(countries))

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
    return r


# function to build the translator
def build_translator(path, skiprows=0):
    excel = Excel(path, skiprows, None)

    excel.dataframe.iloc[:, 0] = excel.dataframe.iloc[:, 0]
    excel.dataframe.iloc[:, 1] = excel.dataframe.iloc[:, 1]

    return excel.parse_two_columns(0, 1)
