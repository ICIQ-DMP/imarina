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

import pandas as pd
import pytest

from imarina.core.date_utile import sanitize_date
from imarina.core.defines import MADRID_TZ, PERMANENT_CONTRACT_DATE


def test_sanitize_date_naive_datetime_gets_madrid_timezone():
    # Naive on purpose: that's exactly the input sanitize_date() is meant to handle.
    naive = datetime.datetime(2020, 5, 1, 10, 30)  # noqa: DTZ001
    assert sanitize_date(naive) == naive.replace(tzinfo=MADRID_TZ)


def test_sanitize_date_naive_pandas_timestamp_gets_madrid_timezone():
    timestamp = pd.Timestamp(2020, 5, 1)
    assert sanitize_date(timestamp) == datetime.datetime(2020, 5, 1, tzinfo=MADRID_TZ)


def test_sanitize_date_already_tz_aware_datetime_is_returned_unchanged():
    aware = datetime.datetime(2020, 5, 1, tzinfo=datetime.UTC)
    result = sanitize_date(aware)
    assert result is aware
    assert result.tzinfo == datetime.UTC


def test_sanitize_date_nat_returns_permanent_contract_date():
    assert sanitize_date(pd.NaT) == PERMANENT_CONTRACT_DATE


def test_sanitize_date_none_returns_permanent_contract_date():
    assert sanitize_date(None) == PERMANENT_CONTRACT_DATE


def test_sanitize_date_nan_float_returns_permanent_contract_date():
    assert sanitize_date(float("nan")) == PERMANENT_CONTRACT_DATE


def test_sanitize_date_parses_ddmmyyyy_string():
    assert sanitize_date("15/03/2021") == datetime.datetime(
        2021, 3, 15, tzinfo=MADRID_TZ
    )


def test_sanitize_date_strips_surrounding_quotes_from_string():
    # A3 exports sometimes wrap date cells in single quotes to force Excel to
    # treat them as text rather than reformatting them.
    assert sanitize_date("'15/03/2021'") == datetime.datetime(
        2021, 3, 15, tzinfo=MADRID_TZ
    )


def test_sanitize_date_unsupported_type_raises_value_error():
    with pytest.raises(ValueError, match="Unknown type for date to sanitize"):
        sanitize_date(12345)
