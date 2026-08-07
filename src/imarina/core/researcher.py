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

import datetime
from dataclasses import dataclass, replace
from typing import Any

from imarina.core.log_utils import get_logger

logger = get_logger(__name__)


@dataclass(kw_only=True)
class Researcher:
    dni: Any = None
    email: Any = None
    name: Any = None
    surname: Any = None
    second_surname: Any = None
    ini_date: datetime.datetime | None = None
    end_date: datetime.datetime | None = None
    ini_prorrog: datetime.datetime | None = None
    end_prorrog: datetime.datetime | None = None
    date_termination: datetime.datetime | None = None
    sex: Any = None
    personal_web: Any = None
    signature: Any = None
    signature_custom: Any = None
    country: Any = None
    born_country: Any = None
    job_description: Any = None
    code_center: Any = None
    unit_group: Any = None
    entity_type: Any = None
    orcid: Any = None
    scopus_id: Any = None
    google_scholar_id: Any = None

    # ICIQ's fixed institutional info. Every researcher works at ICIQ, so
    # these are the same for everyone unless a caller supplies its own value
    # (e.g. iMarina rows carry their own copy of this data; A3 rows don't
    # have these columns at all and always fall back to the default).
    adscription_type: str | None = None
    entity_country: str | None = None
    entity_community: str | None = None
    entity_province: str | None = None
    entity_city: str | None = None
    entity_postal_code: str | None = None
    entity_address: str | None = None
    entity_web: str | None = None
    contact_phone: str | None = None

    def __post_init__(self) -> None:
        defaults = self._institutional_defaults()
        self.adscription_type = self.adscription_type or defaults["adscription_type"]
        self.entity_country = self.entity_country or defaults["entity_country"]
        self.entity_community = self.entity_community or defaults["entity_community"]
        self.entity_province = self.entity_province or defaults["entity_province"]
        self.entity_city = self.entity_city or defaults["entity_city"]
        self.entity_postal_code = (
            self.entity_postal_code or defaults["entity_postal_code"]
        )
        self.entity_address = self.entity_address or defaults["entity_address"]
        self.entity_web = self.entity_web or defaults["entity_web"]
        self.contact_phone = self.contact_phone or defaults["contact_phone"]

    @staticmethod
    def _institutional_defaults() -> dict[str, str]:
        """ICIQ's fixed institutional/contact info, used to fill in any of
        these fields a caller didn't supply its own value for."""
        return {
            "adscription_type": "Research",
            "entity_country": "Spain",
            "entity_community": "Cataluña",
            "entity_province": "Tarragona",
            "entity_city": "Tarragona",
            "entity_postal_code": "43007",
            "entity_address": "Av. Països Catalans, 16",
            "entity_web": "https://iciq.org/",
            "contact_phone": "34977920200",
        }

    def __str__(self) -> str:
        return (
            f"\nResearcher:\n"
            f"  DNI: {self.dni}\n"
            f"  Email: {self.email}\n"
            f"  Name: {self.name}\n"
            f"  Surname: {self.surname}\n"
            f"  Second Surname: {self.second_surname}\n"
            f"  End Date: {self.end_date}\n"
            f"  Ini Date: {self.ini_date}\n"
            f"  Ini Prorrog: {self.ini_prorrog}\n"
            f"  End Prorrog: {self.end_prorrog}\n"
            f"  Date Termination: {self.date_termination}\n"
            f"  Sex: {self.sex}\n"
            f"  Personal web: {self.personal_web}\n"
            f"  Signature: {self.signature}\n"
            f"  Signature custom: {self.signature_custom}\n"
            f"  Country: {self.country}\n"
            f"  Born country: {self.born_country}\n"
            f'  Job description: "{self.job_description}"\n'
            f"  Code center: {self.code_center}\n"
            f"  Adscription type : {self.adscription_type}\n"
            f"  Unit group: {self.unit_group}\n"
            f"  Entity type: {self.entity_type}\n"
            f"  Entity country: {self.entity_country}\n"
            f"  Entity community: {self.entity_community}\n"
            f"  Entity province: {self.entity_province}\n"
            f"  Entity city: {self.entity_city}\n"
            f"  Entity postal code: {self.entity_postal_code}\n"
            f"  Entity address: {self.entity_address}\n"
            f"  Entity web: {self.entity_web}\n"
            f"  Contact Phone: {self.contact_phone}\n"
            f"  ORCID: {self.orcid}\n"
            f"  Scopus ID: {self.scopus_id}\n"
            f"  Google scholar ID: {self.google_scholar_id}\n"
        )

    def copy(self) -> Researcher:
        return replace(self)

    def search_data(self, data_input: list[Researcher]) -> list[Researcher]:
        matches = [
            researcher for researcher in data_input if self.is_same_person(researcher)
        ]

        if matches:
            same_ini = [r for r in matches if r.ini_date == self.ini_date]
            return same_ini if len(same_ini) == 1 else matches

        return []

    def is_same_person(self, other: Researcher) -> bool:
        if self.orcid and other.orcid and self.orcid == other.orcid:
            return True
        if self.dni and other.dni and self.dni == other.dni:
            return True
        return bool(self.email and other.email and self.email == other.email)

    def has_changed_jobs(self, researcher: Researcher) -> bool:
        if (
            self.job_description == "Postdoctoral researcher"
            and researcher.job_description == "Associated researcher"
        ) or (
            self.job_description == "Associated researcher"
            and researcher.job_description == "Postdoctoral researcher"
        ):
            return False

        if (
            self.job_description == "Group Leader / ICREA Professor"
            and researcher.job_description == "Group Leader"
        ) or (
            self.job_description == "Group Leader"
            and researcher.job_description == "Group Leader / ICREA Professor"
        ):
            return False

        return bool(self.job_description != researcher.job_description)

    def is_visitor(self) -> bool:
        # Center code 4 tends to be a visitor
        if self.code_center == 4:

            job = str(self.job_description).lower()
            permanent_keywords = [
                "leader",
                "manager",
                "principal",
                "head",
            ]  # these positions are usually not visitors since they are permanent positions

            # If the job_description contains one of those keywords, then it's NOT a visitor
            return not any(key in job for key in permanent_keywords)

        if self.ini_date and self.end_date:
            duration = (self.end_date - self.ini_date).days
            if duration < 90:  # Less than 3 months is almost always a VISITOR
                return True

        return False


# normalize the researcher's name
def normalize_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        return ""

    name = name.strip()

    fixed = name.title() if name.isupper() or name.islower() else name

    return fixed
