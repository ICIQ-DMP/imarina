import re
import unicodedata
from enum import Enum

from imarina.core.Researcher import Researcher, normalize_name
from imarina.core.date_utile import sanitize_date
from imarina.core.excel import get_val
from imarina.core.log_utils import get_logger

logger = get_logger(__name__)


class A3_Field(Enum):
    CODE_CENTER = 1
    NAME = 2
    SURNAME = 3
    SECOND_SURNAME = 4
    DNI = 5
    SEX = 6
    COUNTRY = 7
    BORN_COUNTRY = 8
    EMAIL = 9
    JOB_DESCRIPTION = 10
    UNIT_GROUP = 11
    ORCID = 13
    INI_DATE = 14
    END_DATE = 15
    INI_PRORROG = 16
    END_PRORROG = 17
    DATE_TERMINATION = 18
    PERSONAL_WEB = -1
    SIGNATURE = -1
    SIGNATURE_CUSTOM = -1
    BIRTH_DATE = -1
    ADSCRIPTION_TYPE = -1



def parse_a3_row_data(row, translator):

    # function per normalitzar el nom del country
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
        name = re.sub(r"\d+", "", name)  # eliminar números
        name = "".join(
            c
            for c in unicodedata.normalize("NFD", name)  # elimina accents
            if unicodedata.category(c) != "Mn"
        )
        return name.lower().strip()

    # exceptions translate country alias
    manual_country_aliases = {
        "iran republica islamica de": "iran",
        "alemania, republica federal": "alemania",
        "alemania republica federal": "alemania",
        "mejico": "mexico",
    }
    translator_countries = {
        normalize_country_name(k): v.strip()
        for k, v in translator[A3_Field.COUNTRY].items()
    }

    born_country_raw = str(
        row.values[A3_Field.BORN_COUNTRY.value]
    ).strip()  # llegeix el value de la row(row.values) del excel A3 i el Field.BORN_COUNTRY.value  .strip delete whitespaces
    born_country_clean = normalize_country_name(
        born_country_raw
    )  # born country ja normalitzat i el busca al translator_countries

    born_country_clean = manual_country_aliases.get(
        born_country_clean, born_country_clean
    )

    born_country = translator_countries.get(
        born_country_clean, born_country_clean.capitalize()
    )  # born country completament traduit

    country_raw = str(
        row.values[A3_Field.COUNTRY.value]
    ).strip()  # llegeix la row.values del Country del field de A3
    country_clean = normalize_country_name(country_raw)  # el country normalitzat

    country_clean = manual_country_aliases.get(country_clean, country_clean)

    country = translator_countries.get(
        country_clean, country_clean.capitalize()
    )  # el country completament traduit



    logger.debug(f"Raw born_country: {born_country_raw}")
    logger.debug(f"Clean born_country: {born_country_clean}")
    logger.debug(f"Translated born_country: {born_country}")
    logger.debug(f"Raw country: {country_raw}")
    logger.debug(f"Clean country: {country_clean}")
    logger.debug(f"Translated country: {country}")

    email_val = get_val(row, A3_Field.EMAIL.value)
    if email_val is not None:
        email_val = email_val.lower()

    # Translates unit_group into entity
    entity_val = translator[A3_Field.UNIT_GROUP][row.values[A3_Field.UNIT_GROUP.value]]

    personal_web_val = translator[A3_Field.PERSONAL_WEB][entity_val]
    print("translating " + entity_val + " into " + personal_web_val)
    data = Researcher(
        code_center=row.values[A3_Field.CODE_CENTER.value],
        dni=row.values[A3_Field.DNI.value],
        email=email_val,
        orcid=str(row.values[A3_Field.ORCID.value])
        .replace("-", "")
        .replace(".", "")
        .strip()
        .lower(),
        name=normalize_name(row.values[A3_Field.NAME.value]),
        surname=normalize_name(row.values[A3_Field.SURNAME.value]),
        second_surname=normalize_name(row.values[A3_Field.SECOND_SURNAME.value]),
        ini_date=sanitize_date(row.values[A3_Field.INI_DATE.value]),
        end_date=sanitize_date(row.values[A3_Field.END_DATE.value]),
        ini_prorrog=sanitize_date(row.values[A3_Field.INI_PRORROG.value]),
        end_prorrog=sanitize_date(row.values[A3_Field.END_PRORROG.value]),
        date_termination=sanitize_date(row.values[A3_Field.DATE_TERMINATION.value]),
        sex=translator[A3_Field.SEX][row.values[A3_Field.SEX.value]],
        personal_web=personal_web_val,
        signature="",
        signature_custom="",
        country=country,
        born_country=born_country,
        job_description=translator[A3_Field.JOB_DESCRIPTION][
            row.values[A3_Field.JOB_DESCRIPTION.value]
        ],
        adscription_type="Research",
        unit_group=entity_val
    )
    return data
