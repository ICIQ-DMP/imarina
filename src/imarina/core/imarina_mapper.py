from enum import Enum

import pandas as pd

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
    ADSCRIPTION_TYPE = 15  # Submit PARSE
    JOB_DESCRIPTION = 16  # Submit
    DEDICATION = 17  # NEW PARSE
    INI_DATE = 18  # Submit
    END_DATE = 19  # Submit
    UNIT_GROUP = 20  # Submit  PARSE

    ENTITY_TYPE = 22
    ENTITY_COUNTRY = 23
    ENTITY_COMMUNITY = 24
    ENTITY_PROVINCE = 25
    ENTITY_CITY = 26
    ENTITY_POSTAL_CODE = 27
    ENTITY_ADDRESS = 28
    ENTITY_WEB = 29
    ORCID = 35
    GOOGLE_SCHOLAR_ID = 39
    SCOPUS_ID = 37
    CONTACT_PHONE = 46


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
    empty_output_row.dataframe.iat[0, ImarinaField.ADSCRIPTION_TYPE.value] = (
        data.adscription_type
    )
    empty_output_row.dataframe.iat[0, ImarinaField.UNIT_GROUP.value] = data.unit_group
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_TYPE.value] = data.entity_type

    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_WEB.value] = data.entity_web

    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_COUNTRY.value] = (
        data.entity_country
    )
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_COMMUNITY.value] = (
        data.entity_community
    )
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_PROVINCE.value] = (
        data.entity_province
    )
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_CITY.value] = data.entity_city
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_POSTAL_CODE.value] = (
        data.entity_postal_code
    )
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_ADDRESS.value] = (
        data.entity_address
    )
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_WEB.value] = (
        data.entity_web
    )
    empty_output_row.dataframe.iat[0, ImarinaField.SCOPUS_ID.value] = (
        data.scopus_id
    )
    empty_output_row.dataframe.iat[0, ImarinaField.GOOGLE_SCHOLAR_ID.value] = (
        data.google_scholar_id
    )
    empty_output_row.dataframe.iat[0, ImarinaField.CONTACT_PHONE.value] = (
        data.contact_phone
    )


# parsear los datos de imarina
def parse_imarina_row_data(row):

    entity_val = get_val(row, ImarinaField.UNIT_GROUP.value)
    entity_val = str(entity_val).strip() if pd.notna(entity_val) else ""

    entity_type_val = get_val(row, ImarinaField.ENTITY_TYPE.value)
    entity_type_val = str(entity_type_val).strip() if pd.notna(entity_type_val) else ""

    entity_web_val = get_val(row, ImarinaField.ENTITY_WEB.value)
    entity_web_val = str(entity_web_val).strip() if pd.notna(entity_web_val) else ""

    scopus_id_val = (
        str(val).strip()
        if (val := get_val(row, ImarinaField.SCOPUS_ID.value)) is not None
        else ""
    )
    if scopus_id_val != "":
        print(scopus_id_val)
        input()

    google_scholar_val = (
        str(val).strip()
        if (val := get_val(row, ImarinaField.GOOGLE_SCHOLAR_ID.value)) is not None
        else ""
    )

    orcid_val = get_val(row, ImarinaField.ORCID.value)
    if orcid_val is None:
        orcid_val = ""

    job_description_val = get_val(row, ImarinaField.JOB_DESCRIPTION.value)
    if job_description_val:
        job_description_val = job_description_val.strip()
        # Hardcoded because they are only 2 values
        if job_description_val == "Associated researcher":
            job_description_val = "Postdoctoral researcher"
        elif job_description_val == "Group Leader / ICREA Professor":
            job_description_val = "Group Leader"

    email_val = get_val(row, ImarinaField.EMAIL.value)
    if email_val is not None:
        email_val = email_val.lower()

    data = Researcher(
        dni=get_val(row, ImarinaField.DNI.value),  # dni_val (value)
        email=email_val,
        orcid=orcid_val,  # orcid_val (value)
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
        adscription_type=get_val(row, ImarinaField.ADSCRIPTION_TYPE.value),
        unit_group=get_val(row, ImarinaField.UNIT_GROUP.value),

        entity=entity_val,  # entity_val (value)
        entity_type=entity_type_val,  # entity_type_val (value)
        entity_web=entity_web_val,  # entity_web_val (value)
        entity_country=str(get_val(row, ImarinaField.ENTITY_COUNTRY.value)),
        entity_community=str(get_val(row, ImarinaField.ENTITY_COMMUNITY.value)),
        entity_province=str(get_val(row, ImarinaField.ENTITY_PROVINCE.value)),
        entity_city=str(get_val(row, ImarinaField.ENTITY_CITY.value)),
        entity_postal_code=str(get_val(row, ImarinaField.ENTITY_POSTAL_CODE.value)),
        entity_address=str(get_val(row, ImarinaField.ENTITY_ADDRESS.value)),
        scopus_id=str(scopus_id_val),
        google_scholar=google_scholar_val,
        contact_phone=str(get_val(row, ImarinaField.CONTACT_PHONE.value)),
    )

    return data


def append_researchers_to_output_data(researchers, output_data):
    empty_row_output_data = output_data.__copy__()
    empty_row_output_data.empty()
    empty_row_output_data.dataframe.loc[0] = [None] * len(empty_row_output_data.dataframe.columns)  # TODO: implement method of Excel, get EmptyRow
    for researcher in researchers:
        new_row = empty_row_output_data.__copy__()
        unparse_researcher_to_imarina_row(researcher, new_row)
        output_data.concat(new_row)
