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

import re
import unicodedata
from enum import Enum
from typing import Any

from imarina_load_researchers.core.date_utile import sanitize_date
from imarina_load_researchers.core.excel import get_val
from imarina_load_researchers.core.log_utils import get_logger
from imarina_load_researchers.core.researcher import (
    JOB_TITLE_GROUP_LEADER_ICREA,
    Researcher,
    normalize_name,
)

logger = get_logger(__name__)


class A3Field(Enum):
    # Values are the exact A3.xlsx column headers (row after skiprows=2), so
    # row[field.value] resolves by column name instead of position - adding,
    # removing or reordering unrelated columns in the A3 export no longer
    # breaks this mapping. Only renaming one of these headers would (and
    # that now fails loudly as a KeyError instead of silently reading the
    # wrong column).
    CODE_CENTER = "Código Centro"
    NAME = "Nombre trabajador"
    SURNAME = "Primer apellido trabajador"
    SECOND_SURNAME = "Segundo apellido trabajador"
    DNI = "NIF"
    SEX = "Sexo"
    COUNTRY = "Nacionalidad"
    BORN_COUNTRY = "Pais nacimiento _"
    EMAIL = "E-mail profesional"
    JOB_DESCRIPTION = "Puesto de trabajo"
    UNIT_GROUP = "Grupo Unidad"
    ORCID = "ORCID"
    INI_DATE = "Fecha Inicio Contrato"
    END_DATE = "Fecha Fin Contrato"
    INI_PRORROG = "Fecha Inicio Prórroga"
    END_PRORROG = "Fecha Fin Prórroga"
    DATE_TERMINATION = "Fecha de baja en compañía"

    # Below: not real A3 columns - these members are only ever used as
    # translator-dictionary keys (see Translator/build_translations), never
    # to index a row. Values just need to be unique and are never matched
    # against a spreadsheet header, so each is simply its own member name.
    PERSONAL_WEB = "PERSONAL_WEB"
    SIGNATURE = "SIGNATURE"
    SIGNATURE_CUSTOM = "SIGNATURE_CUSTOM"
    BIRTH_DATE = "BIRTH_DATE"
    ADSCRIPTION_TYPE = "ADSCRIPTION_TYPE"
    ENTITY_TYPE = "ENTITY_TYPE"
    ENTITY_COUNTRY = "ENTITY_COUNTRY"
    ENTITY_COMMUNITY = "ENTITY_COMMUNITY"
    ENTITY_PROVINCE = "ENTITY_PROVINCE"
    ENTITY_CITY = "ENTITY_CITY"
    ENTITY_POSTAL_CODE = "ENTITY_POSTAL_CODE"
    ENTITY_ADDRESS = "ENTITY_ADDRESS"
    ENTITY_WEB = "ENTITY_WEB"
    GOOGLE_SCHOLAR_ID = "GOOGLE_SCHOLAR_ID"
    CONTACT_PHONE = "CONTACT_PHONE"

    JOB_DESCRIPTION_ENTITY = (
        "JOB_DESCRIPTION_ENTITY"  # Special type for 2 columns at the same time
    )


def transform_orcid(orcid: str) -> str:
    if not orcid or orcid == "":
        return ""
    if "-" in orcid:
        return orcid
    orcid = orcid.strip()
    ret = ""
    for counter, char in enumerate(orcid):
        if counter % 4 == 0 and counter != 0:
            ret += "-"
        ret += char
    logger.trace(f"Transform ORCID input is {orcid} and output is {ret}")
    return ret


def normalize_country_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    name = (
        name.replace("\xa0", " ")
        .replace("\u200b", " ")
        .replace("(", "")
        .replace(")", "")
        .strip()
    )
    name = re.sub(r"\d+", "", name)  # remove numbers
    name = "".join(
        c
        for c in unicodedata.normalize("NFD", name)  # remove accents
        if unicodedata.category(c) != "Mn"
    )
    return name.lower().strip()


# exceptions translate country alias
MANUAL_COUNTRY_ALIASES = {
    "iran republica islamica de": "iran",
    "alemania, republica federal": "alemania",
    "alemania republica federal": "alemania",
    "mejico": "mexico",
}


Translator = dict[A3Field, dict[str, str]]


def parse_a3_row_data(row: Any, translator: Translator) -> Any:
    # translator[A3Field.COUNTRY] is pre-normalized by build_translations(), so it can
    # be used directly here without rebuilding it on every row.
    translator_countries = translator[A3Field.COUNTRY]

    born_country_raw = str(
        row[A3Field.BORN_COUNTRY.value]
    ).strip()  # Read the value of the BORN_COUNTRY column for this row. Remove any spaces
    born_country_clean = normalize_country_name(
        born_country_raw
    )  # born country normalize and find in translator_countries

    born_country_clean = MANUAL_COUNTRY_ALIASES.get(
        born_country_clean, born_country_clean
    )

    born_country = translator_countries.get(
        born_country_clean, born_country_clean.capitalize()
    )  # born country fully translated

    country_raw = str(row[A3Field.COUNTRY.value]).strip()
    country_clean = normalize_country_name(country_raw)  #  country normalized

    country_clean = MANUAL_COUNTRY_ALIASES.get(country_clean, country_clean)

    country = translator_countries.get(
        country_clean, country_clean.capitalize()
    )  # country fully translated

    logger.debug(f"Raw born_country: {born_country_raw}")
    logger.debug(f"Clean born_country: {born_country_clean}")
    logger.debug(f"Translated born_country: {born_country}")
    logger.debug(f"Raw country: {country_raw}")
    logger.debug(f"Clean country: {country_clean}")
    logger.debug(f"Translated country: {country}")

    email_val = get_val(row, A3Field.EMAIL.value)
    if email_val is not None:
        email_val = email_val.lower()

    # Translates unit_group into entity
    try:
        entity_val = translator[A3Field.UNIT_GROUP][row[A3Field.UNIT_GROUP.value]]
    except KeyError:
        logger.exception(f"KeyError in UNIT_GROUP: {row[A3Field.UNIT_GROUP.value]!r}")
        raise

    personal_web_val = translator[A3Field.PERSONAL_WEB][entity_val]

    orcid_val = get_val(row, A3Field.ORCID.value)
    if orcid_val is None:
        orcid_val = ""

    try:
        job_description_val = translator[A3Field.JOB_DESCRIPTION][
            row[A3Field.JOB_DESCRIPTION.value]
        ]
    except KeyError:
        logger.exception(
            f"KeyError in JOB DESCRIPTION: {row[A3Field.JOB_DESCRIPTION.value]!r}"
        )
        raise

    # The job description is one of the special job descriptions that are used to determine the entity
    if row[A3Field.JOB_DESCRIPTION.value] in translator[A3Field.JOB_DESCRIPTION_ENTITY]:
        logger.debug(
            f"Special job description found, translating to entity. entity_val was going to be: {entity_val!s}"
        )
        entity_val = translator[A3Field.JOB_DESCRIPTION_ENTITY][
            row[A3Field.JOB_DESCRIPTION.value]
        ]
        logger.debug(f"Entity translated is: {entity_val!s}")

    # Special case for ICREA group leaders, which needs also info from group unit field
    if row[A3Field.UNIT_GROUP.value] == "ICREA":
        job_description_val = JOB_TITLE_GROUP_LEADER_ICREA

    try:
        sex_val = translator[A3Field.SEX][row[A3Field.SEX.value]]
    except KeyError:
        logger.exception(f"KeyError in SEX: {row[A3Field.SEX.value]!r}")
        raise

    data = Researcher(
        code_center=row[A3Field.CODE_CENTER.value],
        dni=row[A3Field.DNI.value],
        email=email_val,
        orcid=transform_orcid(orcid_val),
        name=normalize_name(row[A3Field.NAME.value]),
        surname=normalize_name(row[A3Field.SURNAME.value]),
        second_surname=normalize_name(row[A3Field.SECOND_SURNAME.value]),
        ini_date=sanitize_date(row[A3Field.INI_DATE.value]),
        end_date=sanitize_date(row[A3Field.END_DATE.value]),
        ini_prorrog=sanitize_date(row[A3Field.INI_PRORROG.value]),
        end_prorrog=sanitize_date(row[A3Field.END_PRORROG.value]),
        date_termination=sanitize_date(row[A3Field.DATE_TERMINATION.value]),
        sex=sex_val,
        personal_web=personal_web_val,
        signature="",
        signature_custom="",
        country=country,
        born_country=born_country,
        job_description=job_description_val,
        unit_group=entity_val,
        entity_type=translator[A3Field.ENTITY_TYPE][entity_val],
        google_scholar_id="",
        adscription_type="",
        entity_country="",
        entity_community="",
        entity_province="",
        entity_city="",
        entity_postal_code="",
        entity_address="",
        entity_web="",
        contact_phone="",
        scopus_id="",
    )
    return data
