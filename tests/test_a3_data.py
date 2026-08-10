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

import pandas as pd
import pytest

from imarina.core.a3_mapper import A3Field


@pytest.mark.skip(reason="Integration test, skipped by default")
def test_no_duplicates_in_a3():
    a3_data = pd.read_excel("input/A3.xlsx", skiprows=2)

    def clean(x):
        return (
            str(x).strip().lower().replace("-", "").replace(" ", "")
            if pd.notnull(x)
            else ""
        )

    dnis = a3_data.iloc[:, A3Field.DNI.value].apply(clean)
    dnis = dnis[dnis != ""]

    assert (
        not dnis.duplicated().any()
    ), f"S'han trobat DNIs duplicats: {dnis[dnis.duplicated()].unique()}"

    emails = a3_data.iloc[:, A3Field.EMAIL.value].apply(clean)
    emails = emails[emails != ""]

    assert (
        not emails.duplicated().any()
    ), f"S'han trobat Emails duplicats: {emails[emails.duplicated()].unique()}"
