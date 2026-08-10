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

from datetime import date
from typing import Any

from imarina.core.researcher import Researcher

# Researcher is a kw_only dataclass with no defaults for most fields (see
# core/researcher.py). Tests only care about a handful of fields at a time,
# so this factory fills in every other required field with an inert
# placeholder and lets callers override just what their test is about.
_RESEARCHER_DEFAULTS: dict[str, Any] = {
    "dni": "00000000A",
    "email": "researcher@example.com",
    "name": "Test",
    "surname": "Researcher",
    "second_surname": "",
    "ini_date": date(2020, 1, 1),
    "end_date": date(2021, 1, 1),
    "sex": "",
    "personal_web": "",
    "signature": "",
    "signature_custom": "",
    "country": "",
    "born_country": "",
    "job_description": "",
    "unit_group": "",
    "entity_type": "",
    "orcid": "",
    "scopus_id": "",
    "google_scholar_id": "",
    "adscription_type": "",
    "entity_country": "",
    "entity_community": "",
    "entity_province": "",
    "entity_city": "",
    "entity_postal_code": "",
    "entity_address": "",
    "entity_web": "",
    "contact_phone": "",
}


def build_researcher(**overrides: Any) -> Researcher:
    kwargs = {**_RESEARCHER_DEFAULTS, **overrides}
    return Researcher(**kwargs)
