from __future__ import annotations
from pathlib import Path
from typing import Optional

import pandas as pd

from imarina.core.log_utils import get_logger
from imarina.core.imarina_mapper import append_researchers_to_output_data

logger = get_logger(__name__)


def get_val(row, idx):
    val = row.values[idx]
    if pd.isna(val):
        return None
    return val


class Excel:
    def __init__(self, path: Optional[Path], skiprows=0, header=0):
        if path is None:
            self.dataframe = pd.DataFrame()
        else:
            self.dataframe = pd.read_excel(path, skiprows=skiprows, header=header)

    def parse_two_columns(
        self, key: int, value: int, func_apply_key=None, func_apply_value=None
    ):
        val_col = self.dataframe[value]
        key_col = self.dataframe[key]

        if func_apply_value is not None:
            val_col = val_col.apply(func_apply_value)
        if func_apply_key is not None:
            key_col = key_col.apply(func_apply_key)

        return dict(zip(key_col, val_col))

    def empty(self):
        empty_output_dataframe = self.dataframe[
            0:0
        ].copy()  # retains columns, types, and headers if any
        empty_output_dataframe.loc[0] = [None] * len(self.dataframe.columns)
        self.dataframe = empty_output_dataframe

    def to_excel(self, researchers: list, output_path: Path):

        self.empty()  # DATAFRAME

        append_researchers_to_output_data(researchers, self)  #

        self.dataframe.to_excel(output_path, index=False)

        logger.info(f"iMarina Excel at {output_path} built successfully.")

    def __copy__(self):
        empty = Excel(None)
        empty.dataframe = self.dataframe.copy()
        return empty

    def concat(self, excel: Excel):
        self.dataframe = pd.concat([self.dataframe, excel.dataframe], ignore_index=True)
