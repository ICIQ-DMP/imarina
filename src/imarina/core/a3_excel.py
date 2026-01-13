import pandas as pd

from imarina.core.a3_mapper import A3_Field
from imarina.core.log_utils import get_logger

logger = get_logger(__name__)


# function to find duplicates in excel A3
# TODO: this should be a script or a test
def find_duplicates_in_a3(a3_data):
    # small function to clean
    def clean(x):
        if pd.isna(x) or not x:  # isna = None or nan
            return ""
        return str(x).strip().lower().replace("-", "").replace(" ", "")

    # clean the columns to compare
    df_clean = a3_data.copy()
    df_clean["orcid_clean"] = df_clean.iloc[:, A3_Field.ORCID.value].apply(
        clean
    )  # clean the ORCID Field
    df_clean["dni_clean"] = df_clean.iloc[:, A3_Field.DNI.value].apply(
        clean
    )  # clean the DNI Field
    df_clean["email_clean"] = df_clean.iloc[:, A3_Field.EMAIL.value].apply(
        clean
    )  # clean the EMAIL Field
    df_clean["name"] = df_clean.iloc[:, A3_Field.NAME.value]

    # duplicates ORCID
    orcid_dups = df_clean[df_clean["orcid_clean"] != ""]["orcid_clean"].duplicated(
        keep=False
    )
    if orcid_dups.any():
        print(" ORCID duplicados encontrados:")
        dup_rows = df_clean[orcid_dups][["orcid_clean", "name"]]
        for idx, row in dup_rows.iterrows():
            print(f"   Fila {idx}: ORCID={row['orcid_clean']}, Name={row['name']}")
        print()

    # duplicates DNI
    dni_dups = df_clean[df_clean["dni_clean"] != ""]["dni_clean"].duplicated(keep=False)
    if dni_dups.any():
        print("️ DNI duplicados encontrados:")
        dup_rows = df_clean[dni_dups][["dni_clean", "name"]]
        for idx, row in dup_rows.iterrows():
            print(f"   Fila {idx}: DNI={row['dni_clean']}, Name={row['name']}")
        print()

    # duplicates EMAIL
    email_dups = df_clean[df_clean["email_clean"] != ""]["email_clean"].duplicated(
        keep=False
    )
    if email_dups.any():
        print(" EMAIL duplicados encontrados:")
        dup_rows = df_clean[email_dups][["email_clean", "name"]]
        for idx, row in dup_rows.iterrows():
            print(f"   Fila {idx}: EMAIL={row['email_clean']}, Name={row['name']}")
        print()
