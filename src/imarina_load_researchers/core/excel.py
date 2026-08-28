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

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pandas as pd

from imarina_load_researchers.core.log_utils import get_logger

logger = get_logger(__name__)


def get_val(row: pd.Series, field: str) -> Any:
    """
    Reads a cell value from a dataframe row, normalizing pandas' NaN to `None`.

    Args:
        row (pd.Series): The row to read from.
        field (str): The column/field name to read.

    Returns:
        Any: The cell value, or `None` if it's `NaN`/missing.
    """
    val = row[field]
    if pd.isna(val):
        return None
    return val


def get_str_val(row: pd.Series, field: str) -> str:
    """
    Reads a cell value from a dataframe row as a stripped string.

    Args:
        row (pd.Series): The row to read from.
        field (str): The column/field name to read.

    Returns:
        str: The cell value converted to `str` and stripped, or `""` if the
            cell is `NaN`/missing.
    """
    val = get_val(row, field)
    return str(val).strip() if val is not None else ""


class Excel:
    """Thin wrapper around a pandas dataframe loaded from (or destined for)
    an `.xlsx` file, used throughout `build` for both input dictionaries and
    the output spreadsheet."""

    def __init__(
        self,
        path: Path | None,
        skiprows: int = 0,
        header: int | None = 0,
    ) -> None:
        """
        Loads an Excel file into a dataframe, or starts with an empty one.

        Args:
            path (Path | None): Path to the `.xlsx` file to load, or `None`
                to start with an empty dataframe (used by `__copy__`).
            skiprows (int): Number of leading rows to skip before the header,
                forwarded to `pandas.read_excel`.
            header (int | None): Row index to use as the column header,
                forwarded to `pandas.read_excel`.
        """
        if path is None:
            self.dataframe = pd.DataFrame()
        else:
            self.dataframe = pd.read_excel(path, skiprows=skiprows, header=header)

    def parse_two_columns(
        self,
        key: int,
        value: int,
        func_apply_key: Callable[[Any], Any] | None = None,
        func_apply_value: Callable[[Any], Any] | None = None,
    ) -> dict[Any, Any]:
        """
        Builds a `{key: value}` dict out of two columns of this sheet.

        Used to load the two-column translation-dictionary spreadsheets
        (e.g. country name mappings) into lookup dicts.

        Args:
            key (int): Column index to use as dict keys.
            value (int): Column index to use as dict values.
            func_apply_key (Callable[[Any], Any] | None): Optional function
                applied to every key value before building the dict.
            func_apply_value (Callable[[Any], Any] | None): Optional function
                applied to every value before building the dict.

        Returns:
            dict[Any, Any]: The resulting key/value mapping.
        """
        val_col = self.dataframe[value]
        key_col = self.dataframe[key]

        if func_apply_value is not None:
            val_col = val_col.apply(func_apply_value)
        if func_apply_key is not None:
            key_col = key_col.apply(func_apply_key)

        return dict(zip(key_col, val_col, strict=True))

    def empty(self) -> None:
        """Drops all rows from the dataframe, keeping its columns/dtypes/header."""
        # retains columns, types, and headers if any, but 0 rows
        self.dataframe = self.dataframe[0:0].copy()

    def to_excel(self, output_path: Path) -> None:
        """
        Writes this dataframe out to an `.xlsx` file.

        Args:
            output_path (Path): Destination path for the spreadsheet.
        """
        self.dataframe.to_excel(output_path, index=False)
        logger.info(f"iMarina Excel at {output_path} built successfully.")

    def __copy__(self) -> Excel:
        """
        Returns a shallow copy of this `Excel` with an independently-copied
        dataframe.

        Returns:
            Excel: A new `Excel` instance wrapping a copy of `self.dataframe`.
        """
        empty = Excel(None)
        empty.dataframe = self.dataframe.copy()
        return empty

    def concat(self, excel: Excel) -> None:
        """
        Appends another `Excel`'s rows onto this one's dataframe, in place.

        Args:
            excel (Excel): The `Excel` whose rows are appended.
        """
        self.dataframe = pd.concat([self.dataframe, excel.dataframe], ignore_index=True)
