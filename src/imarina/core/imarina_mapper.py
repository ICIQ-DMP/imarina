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

    ID_ONE = 21  # PARSE
    ENTITY_TYPE = 22  # Submit DONE
    ENTITY_COUNTRY = 23
    ENTITY_COMMUNITY = 24
    ENTITY_NAME = 25
    ENTITY_CITY = 26
    ENTITY_CODE = 27
    ENTITY_DIRECTION = 28
    ENTITY_WEB = 29  # Submit  DONE
    ENTITY_TYPE2 = 30
    ENTITY2 = 31
    ID_TWO = 32
    ENTITY_TYPE3 = 33
    ID_THREE = 34
    ORCID = 35  # Submit
    RESEARCH_ID = 36
    AUTHOR_ID = 37
    DIALNET_ID = 38
    GOOGLE_SCHOLAR = 39
    CONTACT_COUNTRY = 40
    COMMUNITY_CONTACT = 41
    CONTACT_PROVINCE = 42
    CONTACT_CITY = 43
    CODE_CONTACT = 44
    CONTACT_DIRECTION = 45
    CONTACT_PHONE = 46
    BIO = 47


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
    empty_output_row.dataframe.iat[0, ImarinaField.ID_ONE.value] = data.id_one
    empty_output_row.dataframe.iat[0, ImarinaField.ID_TWO.value] = data.id_two
    empty_output_row.dataframe.iat[0, ImarinaField.ID_THREE.value] = data.id_three
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY2.value] = data.entity2
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_COUNTRY.value] = (
        data.entity_country
    )
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_COMMUNITY.value] = (
        data.entity_community
    )
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_NAME.value] = data.entity_name
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_CITY.value] = data.entity_city
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_CODE.value] = data.entity_code
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_DIRECTION.value] = (
        data.entity_direction
    )
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_TYPE2.value] = (
        data.entity_type2
    )
    empty_output_row.dataframe.iat[0, ImarinaField.ENTITY_TYPE3.value] = (
        data.entity_type3
    )

    empty_output_row.dataframe.iat[0, ImarinaField.RESEARCH_ID.value] = data.research_id
    empty_output_row.dataframe.iat[0, ImarinaField.AUTHOR_ID.value] = data.author_id
    empty_output_row.dataframe.iat[0, ImarinaField.DIALNET_ID.value] = data.dialnet_id

    empty_output_row.dataframe.iat[0, ImarinaField.GOOGLE_SCHOLAR.value] = (
        data.google_scholar
    )
    empty_output_row.dataframe.iat[0, ImarinaField.CONTACT_COUNTRY.value] = (
        data.contact_country
    )
    empty_output_row.dataframe.iat[0, ImarinaField.COMMUNITY_CONTACT.value] = (
        data.community_contact
    )
    empty_output_row.dataframe.iat[0, ImarinaField.CONTACT_PROVINCE.value] = (
        data.contact_province
    )
    empty_output_row.dataframe.iat[0, ImarinaField.CONTACT_CITY.value] = (
        data.contact_city
    )
    empty_output_row.dataframe.iat[0, ImarinaField.CODE_CONTACT.value] = (
        data.code_contact
    )
    empty_output_row.dataframe.iat[0, ImarinaField.CONTACT_DIRECTION.value] = (
        data.contact_direction
    )
    empty_output_row.dataframe.iat[0, ImarinaField.CONTACT_PHONE.value] = (
        data.contact_phone
    )
    empty_output_row.dataframe.iat[0, ImarinaField.BIO.value] = data.bio


# parsear los datos de imarina
def parse_imarina_row_data(row):

    entity_val = get_val(row, ImarinaField.UNIT_GROUP.value)
    entity_val = str(entity_val).strip() if pd.notna(entity_val) else ""

    entity_type_val = get_val(row, ImarinaField.ENTITY_TYPE.value)
    entity_type_val = str(entity_type_val).strip() if pd.notna(entity_type_val) else ""

    entity_web_val = get_val(row, ImarinaField.ENTITY_WEB.value)
    entity_web_val = str(entity_web_val).strip() if pd.notna(entity_web_val) else ""

    id_one_val = (
        str(val).strip()
        if (val := get_val(row, ImarinaField.ID_ONE.value)) is not None
        else ""
    )
    id_two_val = (
        str(val).strip()
        if (val := get_val(row, ImarinaField.ID_TWO.value)) is not None
        else ""
    )
    id_three_val = (
        str(val).strip()
        if (val := get_val(row, ImarinaField.ID_THREE.value)) is not None
        else ""
    )
    research_id_val = (
        str(val).strip()
        if (val := get_val(row, ImarinaField.RESEARCH_ID.value)) is not None
        else ""
    )
    author_id_val = (
        str(val).strip()
        if (val := get_val(row, ImarinaField.AUTHOR_ID.value)) is not None
        else ""
    )
    dialnet_id_val = (
        str(val).strip()
        if (val := get_val(row, ImarinaField.DIALNET_ID.value)) is not None
        else ""
    )
    google_scholar_val = (
        str(val).strip()
        if (val := get_val(row, ImarinaField.GOOGLE_SCHOLAR.value)) is not None
        else ""
    )

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
        id_one=id_one_val,
        id_two=id_two_val,
        id_three=id_three_val,
        entity2=get_val(row, ImarinaField.ENTITY2.value),
        entity_country=str(get_val(row, ImarinaField.ENTITY_COUNTRY.value)),
        entity_community=str(get_val(row, ImarinaField.ENTITY_COMMUNITY.value)),
        entity_name=str(get_val(row, ImarinaField.ENTITY_NAME.value)),
        entity_city=str(get_val(row, ImarinaField.ENTITY_CITY.value)),
        entity_code=str(get_val(row, ImarinaField.ENTITY_CODE.value)),
        entity_direction=str(get_val(row, ImarinaField.ENTITY_DIRECTION.value)),
        entity_type2=str(get_val(row, ImarinaField.ENTITY_TYPE2.value)),
        entity_type3=str(get_val(row, ImarinaField.ENTITY_TYPE3.value)),
        research_id=research_id_val,
        author_id=author_id_val,
        dialnet_id=dialnet_id_val,
        google_scholar=google_scholar_val,
        contact_country=str(get_val(row, ImarinaField.CONTACT_COUNTRY.value)),
        community_contact=str(get_val(row, ImarinaField.COMMUNITY_CONTACT.value)),
        contact_province=str(get_val(row, ImarinaField.CONTACT_PROVINCE.value)),
        contact_city=str(get_val(row, ImarinaField.CONTACT_CITY.value)),
        code_contact=str(get_val(row, ImarinaField.CODE_CONTACT.value)),
        contact_direction=str(get_val(row, ImarinaField.CONTACT_DIRECTION.value)),
        contact_phone=str(get_val(row, ImarinaField.CONTACT_PHONE.value)),
        bio=str(get_val(row, ImarinaField.BIO.value)),
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
