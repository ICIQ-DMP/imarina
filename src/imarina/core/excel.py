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

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pandas as pd

from imarina.core.log_utils import get_logger

logger = get_logger(__name__)


def get_val(row: pd.Series, field: int) -> Any:
    val = row.values[field]
    if pd.isna(val):
        return None
    return val


def get_str_val(row: pd.Series, field: int) -> str:
    val = get_val(row, field)
    return str(val).strip() if val is not None else ""


class Excel:
    def __init__(
        self,
        path: Path | None,
        skiprows: int = 0,
        header: int | None = 0,
    ) -> None:
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
        val_col = self.dataframe[value]
        key_col = self.dataframe[key]

        if func_apply_value is not None:
            val_col = val_col.apply(func_apply_value)
        if func_apply_key is not None:
            key_col = key_col.apply(func_apply_key)

        return dict(zip(key_col, val_col, strict=True))

    def empty(self) -> None:
        # retains columns, types, and headers if any, but 0 rows
        self.dataframe = self.dataframe[0:0].copy()

    def to_excel(self, output_path: Path) -> None:
        self.dataframe.to_excel(output_path, index=False)
        logger.info(f"iMarina Excel at {output_path} built successfully.")

    def __copy__(self) -> Excel:
        empty = Excel(None)
        empty.dataframe = self.dataframe.copy()
        return empty

    def concat(self, excel: Excel) -> None:
        self.dataframe = pd.concat([self.dataframe, excel.dataframe], ignore_index=True)
