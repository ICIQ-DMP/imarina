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

from enum import Enum
from typing import Any

import pandas as pd

from imarina.core.date_utile import sanitize_date, unparse_date
from imarina.core.excel import Excel, get_str_val, get_val
from imarina.core.log_utils import get_logger
from imarina.core.researcher import Researcher, normalize_name

logger = get_logger(__name__)


class ImarinaField(Enum):
    # Values are the exact iMarina.xlsx column headers, so row[field.value]
    # resolves by column name instead of position - adding, removing or
    # reordering unrelated columns in the iMarina export no longer breaks
    # this mapping. Only renaming one of these headers would (and that now
    # fails loudly as a KeyError instead of silently reading/writing the
    # wrong column).
    NAME = "nombre"
    SURNAME = "primer_apellido"
    SECOND_SURNAME = "segundo_apellido"
    SIGNATURE = "signature"
    SIGNATURE_CUSTOM = "signature_custom"
    DNI = "DNI/NIE/NIF"
    BIRTH_DATE = "Fecha de Nacimiento"
    SEX = "Sexo"
    COUNTRY = "País de Nacimiento"
    EMAIL = "Correo Electrónico"
    PERSONAL_WEB = "Web Personal"
    ADSCRIPTION_TYPE = "Tipo de Adscripción"
    JOB_DESCRIPTION = "Categoría Investigadora/Docente"
    DEDICATION = "Dedicación"
    INI_DATE = "Fecha de Inicio"
    END_DATE = "Fecha de Fin"
    UNIT_GROUP = "Entidad (Nivel 1)"

    ENTITY_TYPE = "Tipo de Entidad"
    ENTITY_COUNTRY = "País de la Entidad"
    ENTITY_COMMUNITY = "Region/Comunidad de la Entidad"
    ENTITY_PROVINCE = "Provincia de la Entidad"
    ENTITY_CITY = "Ciudad de la Entidad"
    ENTITY_POSTAL_CODE = "Código Postal de la Entidad"
    ENTITY_ADDRESS = "Dirección de la Entidad"
    ENTITY_WEB = "Web de la Entidad"
    ORCID = "ORCID"
    GOOGLE_SCHOLAR_ID = "Google Scholar ID"
    SCOPUS_ID = "AuthorID (Scopus)"
    CONTACT_PHONE = "Teléfono de Contacto"


def unparse_researcher_to_imarina_row(data: Researcher, empty_output_row: Excel) -> Any:
    empty_output_row.dataframe.at[0, ImarinaField.DNI.value] = data.dni
    empty_output_row.dataframe.at[0, ImarinaField.EMAIL.value] = data.email
    empty_output_row.dataframe.at[0, ImarinaField.ORCID.value] = data.orcid
    empty_output_row.dataframe.at[0, ImarinaField.NAME.value] = data.name
    empty_output_row.dataframe.at[0, ImarinaField.SURNAME.value] = data.surname
    empty_output_row.dataframe.at[0, ImarinaField.SECOND_SURNAME.value] = (
        data.second_surname
    )
    empty_output_row.dataframe.at[0, ImarinaField.INI_DATE.value] = unparse_date(
        data.ini_date
    )
    empty_output_row.dataframe.at[0, ImarinaField.END_DATE.value] = unparse_date(
        data.end_date
    )
    empty_output_row.dataframe.at[0, ImarinaField.SEX.value] = data.sex
    empty_output_row.dataframe.at[0, ImarinaField.PERSONAL_WEB.value] = (
        data.personal_web
    )
    empty_output_row.dataframe.at[0, ImarinaField.SIGNATURE.value] = data.signature
    empty_output_row.dataframe.at[0, ImarinaField.SIGNATURE_CUSTOM.value] = (
        data.signature_custom
    )
    empty_output_row.dataframe.at[0, ImarinaField.COUNTRY.value] = data.country
    empty_output_row.dataframe.at[0, ImarinaField.JOB_DESCRIPTION.value] = (
        data.job_description
    )
    empty_output_row.dataframe.at[0, ImarinaField.ADSCRIPTION_TYPE.value] = (
        data.adscription_type
    )
    empty_output_row.dataframe.at[0, ImarinaField.UNIT_GROUP.value] = data.unit_group
    empty_output_row.dataframe.at[0, ImarinaField.ENTITY_TYPE.value] = data.entity_type

    empty_output_row.dataframe.at[0, ImarinaField.ENTITY_COUNTRY.value] = (
        data.entity_country
    )
    empty_output_row.dataframe.at[0, ImarinaField.ENTITY_COMMUNITY.value] = (
        data.entity_community
    )
    empty_output_row.dataframe.at[0, ImarinaField.ENTITY_PROVINCE.value] = (
        data.entity_province
    )
    empty_output_row.dataframe.at[0, ImarinaField.ENTITY_CITY.value] = data.entity_city
    empty_output_row.dataframe.at[0, ImarinaField.ENTITY_POSTAL_CODE.value] = (
        data.entity_postal_code
    )
    empty_output_row.dataframe.at[0, ImarinaField.ENTITY_ADDRESS.value] = (
        data.entity_address
    )
    empty_output_row.dataframe.at[0, ImarinaField.ENTITY_WEB.value] = data.entity_web
    empty_output_row.dataframe.at[0, ImarinaField.SCOPUS_ID.value] = data.scopus_id
    empty_output_row.dataframe.at[0, ImarinaField.GOOGLE_SCHOLAR_ID.value] = (
        data.google_scholar_id
    )
    empty_output_row.dataframe.at[0, ImarinaField.CONTACT_PHONE.value] = (
        data.contact_phone
    )


# parse the data from imarina
def parse_imarina_row_data(row: pd.Series) -> Researcher:

    entity_type_val = get_str_val(row, ImarinaField.ENTITY_TYPE.value)
    entity_web_val = get_str_val(row, ImarinaField.ENTITY_WEB.value)
    entity_country_val = get_str_val(row, ImarinaField.ENTITY_COUNTRY.value)
    entity_community_val = get_str_val(row, ImarinaField.ENTITY_COMMUNITY.value)
    entity_province_val = get_str_val(row, ImarinaField.ENTITY_PROVINCE.value)
    entity_city_val = get_str_val(row, ImarinaField.ENTITY_CITY.value)
    entity_postal_code_val = get_str_val(row, ImarinaField.ENTITY_POSTAL_CODE.value)
    entity_address_val = get_str_val(row, ImarinaField.ENTITY_ADDRESS.value)
    contact_phone_val = get_str_val(row, ImarinaField.CONTACT_PHONE.value)

    scopus_id_val = get_val(row, ImarinaField.SCOPUS_ID.value)
    if scopus_id_val is not None:
        if isinstance(scopus_id_val, float) and scopus_id_val.is_integer():
            scopus_id_val = str(int(scopus_id_val))
        else:
            scopus_id_val = str(scopus_id_val).strip()
    else:
        scopus_id_val = ""

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

    email_val = get_val(row, ImarinaField.EMAIL.value)
    if email_val is not None:
        email_val = email_val.lower()

    data = Researcher(
        dni=get_val(row, ImarinaField.DNI.value),  # dni_val (value)
        email=email_val,
        orcid=orcid_val,  # orcid_val (value)
        name=normalize_name(get_val(row, ImarinaField.NAME.value) or ""),
        surname=normalize_name(get_val(row, ImarinaField.SURNAME.value) or ""),
        second_surname=normalize_name(
            get_val(row, ImarinaField.SECOND_SURNAME.value) or ""
        ),
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
        entity_type=entity_type_val,  # entity_type_val (value)
        entity_web=entity_web_val,  # entity_web_val (value)
        entity_country=entity_country_val,
        entity_community=entity_community_val,
        entity_province=entity_province_val,
        entity_city=entity_city_val,
        entity_postal_code=entity_postal_code_val,
        entity_address=entity_address_val,
        scopus_id=str(scopus_id_val),
        google_scholar_id=google_scholar_val,
        contact_phone=contact_phone_val,
    )

    return data


def append_researchers_to_output_data(researchers: list[Any], output_data: Any) -> None:
    empty_row_output_data = output_data.__copy__()
    empty_row_output_data.empty()
    empty_row_output_data.dataframe.loc[0] = [None] * len(
        empty_row_output_data.dataframe.columns
    )
    for researcher in researchers:
        new_row = empty_row_output_data.__copy__()
        unparse_researcher_to_imarina_row(researcher, new_row)
        output_data.concat(new_row)
