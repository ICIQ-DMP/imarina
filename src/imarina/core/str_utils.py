# function to normalize names of researchers
import unicodedata


def normalize_name_str(s: str) -> str:
    import re  # importem regular expressions
    import unicodedata  # importem unicodedata

    if not s:
        return s
    s = str(s).lower().strip()
    s = "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )

    s = s.replace("-", " ")  # replace - to spaces " "
    s = re.sub(r"[^a-zñç ]", "", s)  # replace characters not alphabetic except spaces
    s = re.sub(r"\s+", " ", s).strip()  # unify spaces
    return s


def normalize_string(s):
    if not s:
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("-", "").replace(" ", "")
    return s
