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

import pytest
from conftest import build_a3_row, build_a3_translator

from imarina.core.a3_mapper import A3Field, parse_a3_row_data
from imarina.core.researcher import JOB_TITLE_GROUP_LEADER_ICREA


def test_parse_a3_row_data_translates_country_and_born_country():
    row = build_a3_row()
    translator = build_a3_translator()
    researcher = parse_a3_row_data(row, translator)
    assert researcher.country == "Spain"
    assert researcher.born_country == "Spain"


def test_parse_a3_row_data_country_and_born_country_are_translated_independently():
    row = build_a3_row({A3Field.COUNTRY: "España", A3Field.BORN_COUNTRY: "Italia"})
    translator = build_a3_translator({A3Field.COUNTRY: {"italia": "Italy"}})
    researcher = parse_a3_row_data(row, translator)
    assert researcher.country == "Spain"
    assert researcher.born_country == "Italy"


def test_parse_a3_row_data_applies_manual_country_alias():
    # "Méjico" normalizes to "mejico", which MANUAL_COUNTRY_ALIASES maps to
    # "mexico" before the translator lookup happens.
    row = build_a3_row({A3Field.COUNTRY: "Méjico"})
    translator = build_a3_translator()
    researcher = parse_a3_row_data(row, translator)
    assert researcher.country == "Mexico"


def test_parse_a3_row_data_untranslated_country_falls_back_to_capitalized_name():
    row = build_a3_row({A3Field.COUNTRY: "Ruritania"})
    translator = build_a3_translator()
    researcher = parse_a3_row_data(row, translator)
    assert researcher.country == "Ruritania"


def test_parse_a3_row_data_lowercases_email():
    row = build_a3_row({A3Field.EMAIL: "Person@Example.COM"})
    translator = build_a3_translator()
    researcher = parse_a3_row_data(row, translator)
    assert researcher.email == "person@example.com"


def test_parse_a3_row_data_missing_email_stays_none():
    row = build_a3_row({A3Field.EMAIL: None})
    translator = build_a3_translator()
    researcher = parse_a3_row_data(row, translator)
    assert researcher.email is None


def test_parse_a3_row_data_transforms_orcid_into_dash_grouped_format():
    row = build_a3_row({A3Field.ORCID: "0000000212345678"})
    translator = build_a3_translator()
    researcher = parse_a3_row_data(row, translator)
    assert researcher.orcid == "0000-0002-1234-5678"


def test_parse_a3_row_data_missing_orcid_becomes_empty_string():
    row = build_a3_row({A3Field.ORCID: None})
    translator = build_a3_translator()
    researcher = parse_a3_row_data(row, translator)
    assert researcher.orcid == ""


def test_parse_a3_row_data_icrea_unit_group_forces_group_leader_job_title():
    # Special case: ICREA-funded group leaders don't have their own A3 job
    # title, so the unit group is used to detect and relabel them.
    row = build_a3_row(
        {A3Field.UNIT_GROUP: "ICREA", A3Field.JOB_DESCRIPTION: "Investigador"}
    )
    translator = build_a3_translator()
    researcher = parse_a3_row_data(row, translator)
    assert researcher.job_description == JOB_TITLE_GROUP_LEADER_ICREA
    assert researcher.unit_group == "ICIQ"


def test_parse_a3_row_data_special_job_description_overrides_entity():
    row = build_a3_row({A3Field.JOB_DESCRIPTION: "Director"})
    translator = build_a3_translator(
        {
            A3Field.JOB_DESCRIPTION: {"Director": "Director"},
            A3Field.JOB_DESCRIPTION_ENTITY: {"Director": "Rectorate"},
            A3Field.ENTITY_TYPE: {"Rectorate": "Special Entity Type"},
        }
    )
    researcher = parse_a3_row_data(row, translator)
    assert researcher.job_description == "Director"
    assert researcher.unit_group == "Rectorate"
    assert researcher.entity_type == "Special Entity Type"


def test_parse_a3_row_data_unknown_unit_group_raises_keyerror():
    row = build_a3_row({A3Field.UNIT_GROUP: "NOT_IN_TRANSLATOR"})
    translator = build_a3_translator()
    with pytest.raises(KeyError):
        parse_a3_row_data(row, translator)


def test_parse_a3_row_data_unknown_job_description_raises_keyerror():
    row = build_a3_row({A3Field.JOB_DESCRIPTION: "NOT_IN_TRANSLATOR"})
    translator = build_a3_translator()
    with pytest.raises(KeyError):
        parse_a3_row_data(row, translator)


def test_parse_a3_row_data_unknown_sex_raises_keyerror():
    row = build_a3_row({A3Field.SEX: "NOT_IN_TRANSLATOR"})
    translator = build_a3_translator()
    with pytest.raises(KeyError):
        parse_a3_row_data(row, translator)
