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

from imarina_load_researchers.core.researcher import normalize_name


def test_normalize_name_all_uppercase_is_title_cased():
    assert normalize_name("JOHN SMITH") == "John Smith"


def test_normalize_name_all_lowercase_is_title_cased():
    assert normalize_name("john smith") == "John Smith"


def test_normalize_name_mixed_case_is_left_unchanged():
    # Only all-upper or all-lower input gets re-cased; anything already
    # mixed-case (e.g. a name typed correctly) is trusted as-is.
    assert normalize_name("John McDonald") == "John McDonald"


def test_normalize_name_strips_surrounding_whitespace():
    assert normalize_name("  JOHN  ") == "John"


def test_normalize_name_empty_string_returns_empty_string():
    assert normalize_name("") == ""


def test_normalize_name_whitespace_only_returns_empty_string():
    assert normalize_name("   ") == ""


def test_normalize_name_non_string_input_returns_empty_string():
    assert normalize_name(None) == ""
