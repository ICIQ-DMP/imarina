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

from datetime import date

from imarina.core.researcher import Researcher

# --- is_visitor -------------------------------------------------------------
#
# is_visitor() has two mutually-exclusive branches: for code_center == 4,
# the result depends only on job_description keywords and the ini/end dates
# are never even looked at; for anything else, it depends only on the gap
# between ini_date and end_date. A researcher can never hit both checks, so
# each branch needs its own tests rather than one test trying to cover both.


def test_is_visitor_code_center_4_without_permanent_keyword_is_visitor():
    researcher = Researcher(code_center=4, job_description="Predoctoral researcher")
    assert researcher.is_visitor() is True


def test_is_visitor_code_center_4_with_permanent_keyword_is_not_visitor():
    researcher = Researcher(code_center=4, job_description="Group Leader")
    assert researcher.is_visitor() is False


def test_is_visitor_code_center_4_ignores_date_span():
    # Even a multi-year ini/end date gap doesn't matter for code_center 4 -
    # only the job title does.
    researcher = Researcher(
        code_center=4,
        job_description="Predoctoral researcher",
        ini_date=date(2023, 9, 30),
        end_date=date(2025, 10, 5),
    )
    assert researcher.is_visitor() is True


def test_is_visitor_short_duration_is_visitor():
    researcher = Researcher(
        ini_date=date(2025, 9, 30),
        end_date=date(2025, 10, 5),
    )
    assert researcher.is_visitor() is True


def test_is_visitor_long_duration_is_not_visitor():
    researcher = Researcher(
        ini_date=date(2023, 9, 30),
        end_date=date(2025, 10, 5),
    )
    assert researcher.is_visitor() is False


def test_is_visitor_missing_start_date_is_not_visitor():
    researcher = Researcher(ini_date=None, end_date=date(2025, 1, 1))
    assert researcher.is_visitor() is False


def test_is_visitor_missing_end_date_is_not_visitor():
    researcher = Researcher(ini_date=date(2025, 1, 1), end_date=None)
    assert researcher.is_visitor() is False


# --- is_same_person -----------------------------------------------------------


def test_is_same_person_matching_orcid():
    a = Researcher(orcid="0000-0001-2345-6789", dni="X", email="a@example.com")
    b = Researcher(orcid="0000-0001-2345-6789", dni="Y", email="b@example.com")
    assert a.is_same_person(b) is True


def test_is_same_person_matching_dni():
    a = Researcher(dni="12345678A")
    b = Researcher(dni="12345678A")
    assert a.is_same_person(b) is True


def test_is_same_person_matching_email():
    a = Researcher(email="person@example.com")
    b = Researcher(email="person@example.com")
    assert a.is_same_person(b) is True


def test_is_same_person_no_matching_identifiers():
    a = Researcher(orcid="1", dni="A", email="a@example.com")
    b = Researcher(orcid="2", dni="B", email="b@example.com")
    assert a.is_same_person(b) is False


def test_is_same_person_no_identifiers_at_all():
    a = Researcher()
    b = Researcher()
    assert a.is_same_person(b) is False
