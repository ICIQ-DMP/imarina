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


def normalize_string(s: str) -> str:
    if not s:
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("-", "").replace(" ", "")
    return s
