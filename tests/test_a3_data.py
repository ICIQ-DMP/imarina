import pandas as pd
import pytest

from imarina.core.a3_mapper import A3_Field


@pytest.mark.skip(reason="Integration test, skipped by default")
def test_no_duplicates_in_a3():
    a3_data = pd.read_excel("input/A3.xlsx", skiprows=2)

    def clean(x):
        return (
            str(x).strip().lower().replace("-", "").replace(" ", "")
            if pd.notnull(x)
            else ""
        )

    dnis = a3_data.iloc[:, A3_Field.DNI.value].apply(clean)
    dnis = dnis[dnis != ""]

    assert (
        not dnis.duplicated().any()
    ), f"S'han trobat DNIs duplicats: {dnis[dnis.duplicated()].unique()}"

    emails = a3_data.iloc[:, A3_Field.EMAIL.value].apply(clean)
    emails = emails[emails != ""]

    assert (
        not emails.duplicated().any()
    ), f"S'han trobat Emails duplicats: {emails[emails.duplicated()].unique()}"
