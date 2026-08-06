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

from typing import Any

from imarina.core.log_utils import get_logger

logger = get_logger(__name__)


class Researcher:

    def __init__(self, **kwargs: Any) -> None:
        self.dni = kwargs.get("dni")
        self.email = kwargs.get("email")
        self.name = kwargs.get("name")
        self.surname = kwargs.get("surname")
        self.second_surname = kwargs.get("second_surname")
        self.ini_date = kwargs.get("ini_date")
        self.end_date = kwargs.get("end_date")
        self.ini_prorrog = kwargs.get("ini_prorrog")
        self.end_prorrog = kwargs.get("end_prorrog")
        self.date_termination = kwargs.get("date_termination")
        self.sex = kwargs.get("sex")
        self.personal_web = kwargs.get("personal_web")
        self.signature = kwargs.get("signature")
        self.signature_custom = kwargs.get("signature_custom")
        self.country = kwargs.get("country")
        self.born_country = kwargs.get("born_country")
        self.job_description = kwargs.get("job_description")
        self.code_center = kwargs.get("code_center")
        self.adscription_type = "Research"
        self.unit_group = kwargs.get("unit_group")
        self.entity_type = kwargs.get("entity_type")

        self.entity_country = "Spain"
        self.entity_community = "Cataluña"
        self.entity_province = "Tarragona"
        self.entity_city = "Tarragona"
        self.entity_postal_code = "43007"
        self.entity_address = "Av. Països Catalans, 16"
        self.entity_web = "https://iciq.org/"
        self.contact_phone = "34977920200"

        self.orcid = kwargs.get("orcid")
        self.scopus_id = kwargs.get("scopus_id")
        self.google_scholar_id = kwargs.get("google_scholar_id")

    def __str__(self) -> Any:
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

    def copy(self) -> Any:
        return Researcher(
            dni=self.dni,
            email=self.email,
            name=self.name,
            surname=self.surname,
            second_surname=self.second_surname,
            ini_date=self.ini_date,
            end_date=self.end_date,
            ini_prorrog=self.ini_prorrog,
            end_prorrog=self.end_prorrog,
            date_termination=self.date_termination,
            sex=self.sex,
            personal_web=self.personal_web,
            signature=self.signature,
            signature_custom=self.signature_custom,
            country=self.country,
            born_country=self.born_country,
            job_description=self.job_description,
            code_center=self.code_center,
            adscription_type=self.adscription_type,
            unit_group=self.unit_group,
            entity_type=self.entity_type,
            entity_country=self.entity_country,
            entity_community=self.entity_community,
            entity_province=self.entity_province,
            entity_city=self.entity_city,
            entity_postal_code=self.entity_postal_code,
            entity_address=self.entity_address,
            entity_web=self.entity_web,
            contact_phone=self.contact_phone,
            orcid=self.orcid,
            scopus_id=self.scopus_id,
            google_scholar_id=self.google_scholar_id,
        )

    def search_data(self, data_input: Any) -> Any:
        matches = []

        for researcher in data_input:
            if self.is_same_person(researcher):
                matches.append(researcher)

        if matches:
            same_ini = [r for r in matches if r.ini_date == self.ini_date]
            return same_ini if len(same_ini) == 1 else matches

        return []

    def is_same_person(self, other: Any) -> bool:
        if self.orcid and other.orcid and self.orcid == other.orcid:
            return True
        if self.dni and other.dni and self.dni == other.dni:
            return True
        return bool(self.email and other.email and self.email == other.email)

    def has_changed_jobs(self, researcher: Any) -> Any:
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

        return self.job_description != researcher.job_description

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

    if name.isupper() or name.islower():
        fixed = name.title()

    else:
        fixed = name

    return fixed
