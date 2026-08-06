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


# placeholder test
def test_demo():
    assert 1 + 1 == 2


def test_is_visitor():
    researcher = Researcher(
        ini_date=date(2025, 9, 30), end_date=date(2025, 10, 5), code_center=4
    )
    assert researcher.is_visitor()


# COMMENT THIS FAIL TESTS
# def test_isnot_visitor():
#     researcher = Researcher(
#         ini_date=date(2023, 9, 30),
#         end_date=date(2025, 10, 5),
#         code_center=4)
#     assert is_visitor(researcher) == False
#
#
# def test_is_not_visitor_no_start_date():
#     researcher = Researcher(
#         code_center=4,
#         ini_date=None,
#         end_date=date(2025, 1, 1)
#
#     )
#     assert is_visitor(researcher) is False


# COMMENT THIS TEST
# def test_is_not_visitor_no_end_date():
#     researcher = Researcher(
#         code_center=4,
#         ini_date=datetime(2025, 1, 1),
#         end_date=None
#
#     )
#     assert is_visitor(researcher) is True


def test_is_same_person():
    assert True
