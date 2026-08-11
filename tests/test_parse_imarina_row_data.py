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

from conftest import build_imarina_row

from imarina.core.defines import MADRID_TZ
from imarina.core.imarina_mapper import ImarinaField, parse_imarina_row_data


def test_parse_imarina_row_data_maps_and_normalizes_basic_fields():
    row = build_imarina_row()
    researcher = parse_imarina_row_data(row)
    assert researcher.name == "John"
    assert researcher.surname == "Smith"
    assert researcher.second_surname == "Doe"
    assert researcher.dni == "12345678A"
    assert researcher.ini_date == datetime.datetime(2020, 1, 1, tzinfo=MADRID_TZ)
    assert researcher.end_date == datetime.datetime(2021, 1, 1, tzinfo=MADRID_TZ)


def test_parse_imarina_row_data_country_and_born_country_share_the_same_column():
    # iMarina rows carry a single COUNTRY column - unlike A3, there's no
    # separate born-country field, so both end up with the same value.
    row = build_imarina_row({ImarinaField.COUNTRY: "  Spain  "})
    researcher = parse_imarina_row_data(row)
    assert researcher.country == "Spain"
    assert researcher.born_country == "Spain"


def test_parse_imarina_row_data_lowercases_email():
    row = build_imarina_row({ImarinaField.EMAIL: "Person@Example.COM"})
    researcher = parse_imarina_row_data(row)
    assert researcher.email == "person@example.com"


def test_parse_imarina_row_data_strips_whitespace_from_entity_and_contact_fields():
    row = build_imarina_row(
        {
            ImarinaField.ENTITY_CITY: "  Tarragona  ",
            ImarinaField.CONTACT_PHONE: " 34977920200 ",
        }
    )
    researcher = parse_imarina_row_data(row)
    assert researcher.entity_city == "Tarragona"
    assert researcher.contact_phone == "34977920200"


def test_parse_imarina_row_data_job_description_is_stripped():
    row = build_imarina_row({ImarinaField.JOB_DESCRIPTION: "  Researcher  "})
    researcher = parse_imarina_row_data(row)
    assert researcher.job_description == "Researcher"


def test_parse_imarina_row_data_missing_optional_ids_default_to_empty_string():
    row = build_imarina_row(
        {
            ImarinaField.SCOPUS_ID: None,
            ImarinaField.GOOGLE_SCHOLAR_ID: None,
            ImarinaField.ORCID: None,
        }
    )
    researcher = parse_imarina_row_data(row)
    assert researcher.scopus_id == ""
    assert researcher.google_scholar_id == ""
    assert researcher.orcid == ""


def test_parse_imarina_row_data_missing_entity_and_contact_fields_use_institutional_defaults():
    row = build_imarina_row(
        {
            ImarinaField.ENTITY_WEB: None,
            ImarinaField.CONTACT_PHONE: None,
        }
    )
    researcher = parse_imarina_row_data(row)
    # get_str_val() turns the missing cell into "", and Researcher.__post_init__
    # then fills it in with ICIQ's fixed institutional info.
    assert researcher.entity_web == "https://iciq.org/"
    assert researcher.contact_phone == "34977920200"


def test_parse_imarina_row_data_scopus_id_integer_valued_float_has_no_decimal():
    # Excel stores whole numbers as floats (e.g. 987654.0); scopus IDs must
    # round-trip without a trailing ".0".
    row = build_imarina_row({ImarinaField.SCOPUS_ID: 987654.0})
    researcher = parse_imarina_row_data(row)
    assert researcher.scopus_id == "987654"


def test_parse_imarina_row_data_scopus_id_non_integer_value_is_kept_as_is():
    row = build_imarina_row({ImarinaField.SCOPUS_ID: "  ABC123  "})
    researcher = parse_imarina_row_data(row)
    assert researcher.scopus_id == "ABC123"
