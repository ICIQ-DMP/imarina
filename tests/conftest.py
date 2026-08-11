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

import datetime
from datetime import date
from typing import Any

import pandas as pd

from imarina.core.a3_mapper import A3Field, Translator
from imarina.core.imarina_mapper import ImarinaField
from imarina.core.researcher import Researcher

# Researcher is a kw_only dataclass with no defaults for most fields (see
# core/researcher.py). Tests only care about a handful of fields at a time,
# so this factory fills in every other required field with an inert
# placeholder and lets callers override just what their test is about.
_RESEARCHER_DEFAULTS: dict[str, Any] = {
    "dni": "00000000A",
    "email": "researcher@example.com",
    "name": "Test",
    "surname": "Researcher",
    "second_surname": "",
    "ini_date": date(2020, 1, 1),
    "end_date": date(2021, 1, 1),
    "sex": "",
    "personal_web": "",
    "signature": "",
    "signature_custom": "",
    "country": "",
    "born_country": "",
    "job_description": "",
    "unit_group": "",
    "entity_type": "",
    "orcid": "",
    "scopus_id": "",
    "google_scholar_id": "",
    "adscription_type": "",
    "entity_country": "",
    "entity_community": "",
    "entity_province": "",
    "entity_city": "",
    "entity_postal_code": "",
    "entity_address": "",
    "entity_web": "",
    "contact_phone": "",
}


def build_researcher(**overrides: Any) -> Researcher:
    kwargs = {**_RESEARCHER_DEFAULTS, **overrides}
    return Researcher(**kwargs)


# --- A3 row / translator fixtures -------------------------------------------
#
# parse_a3_row_data() reads a row positionally (row.values[A3Field.X.value]),
# the same way it does when called from a real `dataframe.iterrows()`, so a
# pandas Series built from a plain list reproduces that access pattern
# exactly. Only A3Field members with a non-negative value are ever read this
# way - negative ones (PERSONAL_WEB, ENTITY_TYPE, ...) are translator-dict
# keys instead, never row positions.
_A3_ROW_LENGTH = max(field.value for field in A3Field if field.value >= 0) + 1

_A3_ROW_DEFAULTS: dict[A3Field, Any] = {
    A3Field.CODE_CENTER: 1,
    A3Field.NAME: "john",
    A3Field.SURNAME: "smith",
    A3Field.SECOND_SURNAME: "doe",
    A3Field.DNI: "12345678A",
    A3Field.SEX: "H",
    A3Field.COUNTRY: "España",
    A3Field.BORN_COUNTRY: "España",
    A3Field.EMAIL: "Test@Example.com",
    A3Field.JOB_DESCRIPTION: "Investigador",
    A3Field.UNIT_GROUP: "QOC",
    A3Field.ORCID: "0000000212345678",
    # Naive on purpose: A3 exports have no timezone, and parse_a3_row_data()
    # relies on sanitize_date() to attach MADRID_TZ to values like this.
    A3Field.INI_DATE: datetime.datetime(2020, 1, 1),  # noqa: DTZ001
    A3Field.END_DATE: datetime.datetime(2021, 1, 1),  # noqa: DTZ001
    A3Field.INI_PRORROG: None,
    A3Field.END_PRORROG: None,
    A3Field.DATE_TERMINATION: None,
}


def build_a3_row(overrides: dict[A3Field, Any] | None = None) -> pd.Series:
    values: list[Any] = [None] * _A3_ROW_LENGTH
    for field, value in {**_A3_ROW_DEFAULTS, **(overrides or {})}.items():
        values[field.value] = value
    return pd.Series(values)


# translator[A3Field.COUNTRY] keys are pre-normalized (lowercase, no accents)
# by build_translations() before parse_a3_row_data() ever sees them - see the
# comment at the top of that function.
_A3_TRANSLATOR_DEFAULTS: Translator = {
    A3Field.COUNTRY: {"espana": "Spain"},
    A3Field.JOB_DESCRIPTION: {"Investigador": "Researcher"},
    A3Field.PERSONAL_WEB: {"ICIQ": "https://iciq.org/"},
    A3Field.UNIT_GROUP: {"QOC": "ICIQ", "ICREA": "ICIQ"},
    A3Field.ENTITY_TYPE: {"ICIQ": "Research Institute"},
    A3Field.JOB_DESCRIPTION_ENTITY: {},
    A3Field.SEX: {"H": "Male", "D": "Female"},
}


def build_a3_translator(
    overrides: dict[A3Field, dict[str, str]] | None = None,
) -> Translator:
    translator = {
        field: dict(mapping) for field, mapping in _A3_TRANSLATOR_DEFAULTS.items()
    }
    for field, mapping in (overrides or {}).items():
        translator[field].update(mapping)
    return translator


# --- iMarina row fixtures -----------------------------------------------------
_IMARINA_ROW_LENGTH = max(field.value for field in ImarinaField) + 1

_IMARINA_ROW_DEFAULTS: dict[ImarinaField, Any] = {
    ImarinaField.NAME: "john",
    ImarinaField.SURNAME: "smith",
    ImarinaField.SECOND_SURNAME: "doe",
    ImarinaField.SIGNATURE: "sig",
    ImarinaField.SIGNATURE_CUSTOM: "sig-custom",
    ImarinaField.DNI: "12345678A",
    ImarinaField.SEX: "M",
    ImarinaField.COUNTRY: "Spain",
    ImarinaField.EMAIL: "Test@Example.com",
    ImarinaField.PERSONAL_WEB: "https://example.com",
    ImarinaField.ADSCRIPTION_TYPE: "Research",
    ImarinaField.JOB_DESCRIPTION: "Researcher",
    # Naive on purpose: same as the A3 row fixture above - sanitize_date()
    # is what attaches MADRID_TZ.
    ImarinaField.INI_DATE: datetime.datetime(2020, 1, 1),  # noqa: DTZ001
    ImarinaField.END_DATE: datetime.datetime(2021, 1, 1),  # noqa: DTZ001
    ImarinaField.UNIT_GROUP: "ICIQ",
    ImarinaField.ENTITY_TYPE: "Research Institute",
    ImarinaField.ENTITY_COUNTRY: "Spain",
    ImarinaField.ENTITY_COMMUNITY: "Cataluña",
    ImarinaField.ENTITY_PROVINCE: "Tarragona",
    ImarinaField.ENTITY_CITY: "Tarragona",
    ImarinaField.ENTITY_POSTAL_CODE: "43007",
    ImarinaField.ENTITY_ADDRESS: "Av. Països Catalans, 16",
    ImarinaField.ENTITY_WEB: "https://iciq.org/",
    ImarinaField.ORCID: "0000-0001-2345-6789",
    ImarinaField.GOOGLE_SCHOLAR_ID: "abc123",
    ImarinaField.SCOPUS_ID: "987654",
    ImarinaField.CONTACT_PHONE: "34977920200",
}


def build_imarina_row(overrides: dict[ImarinaField, Any] | None = None) -> pd.Series:
    values: list[Any] = [None] * _IMARINA_ROW_LENGTH
    for field, value in {**_IMARINA_ROW_DEFAULTS, **(overrides or {})}.items():
        values[field.value] = value
    return pd.Series(values)
