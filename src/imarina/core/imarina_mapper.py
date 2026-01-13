from enum import Enum

from imarina.core.excel import Excel, get_val
from imarina.core.log_utils import get_logger
from imarina.core.Researcher import Researcher, normalize_name
from imarina.core.date_utile import unparse_date, sanitize_date


logger = get_logger(__name__)


class ImarinaField(Enum):
    NAME = 1  # Submit
    SURNAME = 2  # Submit
    SECOND_SURNAME = 3  # Submit
    SIGNATURE = 4  # No submit. Why?
    SIGNATURE_CUSTOM = 5  # No submit. Why?
    DNI = 6  # Submit
    BIRTH_DATE = 7  # Submit
    SEX = 8  # Submit
    COUNTRY = 9  # Submit
    # BORN_COUNTRY = -1
    EMAIL = 12  # Submit
    PERSONAL_WEB = 13  # Submit
    # ADSCRIPTION_TYPE = 15  # Submit
    JOB_DESCRIPTION = 16  # Submit
    INI_DATE = 18  # Submit
    END_DATE = 19  # Submit
    # ENTITY = 20  # Submit
    # ENTITY_TYPE = 22  # Submit
    # ENTITY_WEB = 29  # Submit
    ORCID = 35  # Submit


def unparse_researcher_to_imarina_row(data: Researcher, empty_output_row: Excel):
    empty_output_row.dataframe.iat[0, ImarinaField.DNI.value] = data.dni
    empty_output_row.dataframe.iat[0, ImarinaField.EMAIL.value] = data.email
    empty_output_row.dataframe.iat[0, ImarinaField.ORCID.value] = data.orcid
    empty_output_row.dataframe.iat[0, ImarinaField.NAME.value] = data.name
    empty_output_row.dataframe.iat[0, ImarinaField.SURNAME.value] = data.surname
    empty_output_row.dataframe.iat[0, ImarinaField.SECOND_SURNAME.value] = (
        data.second_surname
    )
    empty_output_row.dataframe.iat[0, ImarinaField.INI_DATE.value] = unparse_date(
        data.ini_date
    )
    empty_output_row.dataframe.iat[0, ImarinaField.END_DATE.value] = unparse_date(
        data.end_date
    )
    empty_output_row.dataframe.iat[0, ImarinaField.SEX.value] = data.sex
    empty_output_row.dataframe.iat[0, ImarinaField.PERSONAL_WEB.value] = (
        data.personal_web
    )
    empty_output_row.dataframe.iat[0, ImarinaField.SIGNATURE.value] = data.signature
    empty_output_row.dataframe.iat[0, ImarinaField.SIGNATURE_CUSTOM.value] = (
        data.signature_custom
    )
    empty_output_row.dataframe.iat[0, ImarinaField.COUNTRY.value] = data.country
    empty_output_row.dataframe.iat[0, ImarinaField.JOB_DESCRIPTION.value] = (
        data.job_description
    )


def parse_imarina_row_data(row):
    dni_val = get_val(row, ImarinaField.DNI.value)
    if dni_val:
        dni_val = str(dni_val).replace("-", "").replace(".", "").strip().lower()

    orcid_val = get_val(row, ImarinaField.ORCID.value)
    if orcid_val:
        orcid_val = str(orcid_val).replace("-", "").replace(".", "").strip().lower()

    job_description_val = get_val(row, ImarinaField.JOB_DESCRIPTION.value)
    if job_description_val:
        job_description_val = job_description_val.strip()
        # Hardcoded because they are only 2 values
        if job_description_val == "Associated researcher":
            job_description_val = "Postdoctoral researcher"
        elif job_description_val == "Group Leader / ICREA Professor":
            job_description_val = "Group Leader"

    data = Researcher(
        dni=dni_val,
        email=get_val(row, ImarinaField.EMAIL.value),
        orcid=orcid_val,
        name=normalize_name(get_val(row, ImarinaField.NAME.value)),
        surname=normalize_name(get_val(row, ImarinaField.SURNAME.value)),
        second_surname=normalize_name(get_val(row, ImarinaField.SECOND_SURNAME.value)),
        ini_date=sanitize_date(get_val(row, ImarinaField.INI_DATE.value)),
        end_date=sanitize_date(get_val(row, ImarinaField.END_DATE.value)),
        sex=get_val(row, ImarinaField.SEX.value),
        personal_web=get_val(row, ImarinaField.PERSONAL_WEB.value),
        signature=get_val(row, ImarinaField.SIGNATURE.value),
        signature_custom=get_val(row, ImarinaField.SIGNATURE_CUSTOM.value),
        country=str(get_val(row, ImarinaField.COUNTRY.value)).strip(),
        born_country=str(get_val(row, ImarinaField.COUNTRY.value)).strip(),
        job_description=job_description_val,
    )

    return data


def append_researchers_to_output_data(researchers, output_data):
    empty_row_output_data = output_data.__copy__()
    empty_row_output_data.empty()
    for researcher in researchers:
        new_row = empty_row_output_data.__copy__()
        unparse_researcher_to_imarina_row(researcher, new_row)
        output_data.concat(new_row)

