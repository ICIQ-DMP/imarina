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

import datetime
from dataclasses import dataclass, replace

from imarina_load_researchers.core.log_utils import get_logger

logger = get_logger(__name__)


# The A3 snapshot includes more people than iMarina needs, because visitors
# aren't meant to be loaded into iMarina. Center code 4 generally marks a
# visitor, but ICREA group leaders and CSC-scholarship predoctoral
# researchers are also filed under code 4 despite not being visitors - see
# is_visitor()'s docstring for how that's meant to be disambiguated.
VISITOR_CENTER_CODE = 4
# General visitor heuristic for researchers NOT under VISITOR_CENTER_CODE:
# a contract shorter than this is almost always a short-term visit.
VISITOR_MAX_DURATION_DAYS = 90

# Job-description strings that job-matching/visitor-detection logic below
# compares against. Centralized here (rather than re-typed at each call
# site) so a typo can't silently break a comparison - see the StrEnum
# gotcha in CLAUDE.md for the same failure class.
JOB_TITLE_POSTDOCTORAL_RESEARCHER = "Postdoctoral researcher"
JOB_TITLE_ASSOCIATED_RESEARCHER = "Associated researcher"
JOB_TITLE_GROUP_LEADER = "Group Leader"
JOB_TITLE_GROUP_LEADER_ICREA = "Group Leader / ICREA Professor"

# Job-description keywords that denote a permanent position - used to rule
# out "visitor" status in is_visitor().
PERMANENT_POSITION_KEYWORDS = ("leader", "manager", "principal", "head")

INSTITUTIONAL_DEFAULTS = {
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


@dataclass(kw_only=True)
class Researcher:
    """One researcher's data, in the shape shared by both A3 rows and
    iMarina rows once parsed - the common representation `build` diffs
    between the previous iMarina upload and the latest A3 dump."""

    dni: str
    email: str
    name: str
    surname: str
    second_surname: str
    ini_date: datetime.datetime
    end_date: datetime.datetime
    ini_prorrog: datetime.datetime | None = None
    end_prorrog: datetime.datetime | None = None
    date_termination: datetime.datetime | None = None
    sex: str
    personal_web: str
    signature: str
    signature_custom: str
    country: str
    born_country: str
    job_description: str
    code_center: int | None = None
    unit_group: str
    entity_type: str
    orcid: str
    scopus_id: str
    google_scholar_id: str

    # ICIQ's fixed institutional info. Every researcher works at ICIQ, so
    # these are the same for everyone unless a caller supplies its own value
    # (e.g. iMarina rows carry their own copy of this data; A3 rows don't
    # have these columns at all and always fall back to the default).
    adscription_type: str
    entity_country: str
    entity_community: str
    entity_province: str
    entity_city: str
    entity_postal_code: str
    entity_address: str
    entity_web: str
    contact_phone: str

    def __post_init__(self) -> None:
        """Fills any unset institutional/contact field with ICIQ's fixed
        default value (`INSTITUTIONAL_DEFAULTS`)."""
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
        return INSTITUTIONAL_DEFAULTS

    def __str__(self) -> str:
        """Multi-line, human-readable dump of every field, used for `logger.debug` calls."""
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
        """
        Returns an independent copy of this researcher.

        Returns:
            Researcher: A new `Researcher` with the same field values.
        """
        return replace(self)

    def search_data(self, data_input: list[Researcher]) -> list[Researcher]:
        """
        Finds this researcher's match(es) in another list of researchers.

        Matches by `is_same_person` (ORCID, then DNI, then email). If more
        than one match is found, the results are narrowed down to those
        that also share this researcher's `ini_date`, when that narrows the
        set to exactly one; otherwise every `is_same_person` match is
        returned as-is.

        Args:
            data_input (list[Researcher]): The researchers to search among
                (typically the A3 or iMarina researcher list).

        Returns:
            list[Researcher]: The matching researcher(s), or `[]` if none match.
        """
        matches = [
            researcher for researcher in data_input if self.is_same_person(researcher)
        ]

        if matches:
            same_ini = [r for r in matches if r.ini_date == self.ini_date]
            return same_ini if len(same_ini) == 1 else matches

        return []

    def is_same_person(self, other: Researcher) -> bool:
        """
        Whether `self` and `other` represent the same person.

        Matches on the first of ORCID, DNI or email that both researchers
        have a (non-empty) value for.

        Args:
            other (Researcher): The researcher to compare against.

        Returns:
            bool: `True` if `self` and `other` are the same person.
        """
        if self.orcid and other.orcid and self.orcid == other.orcid:
            return True
        if self.dni and other.dni and self.dni == other.dni:
            return True
        return bool(self.email and other.email and self.email == other.email)

    def has_changed_jobs(self, researcher: Researcher) -> bool:
        """
        Whether `self` (the new A3 position) counts as a job change from
        `researcher` (the outgoing iMarina position).

        `JOB_TITLE_POSTDOCTORAL_RESEARCHER`/`JOB_TITLE_ASSOCIATED_RESEARCHER`
        and `JOB_TITLE_GROUP_LEADER`/`JOB_TITLE_GROUP_LEADER_ICREA` are
        treated as equivalent pairs, not a job change.

        Args:
            researcher (Researcher): The researcher's previous (iMarina) position.

        Returns:
            bool: `True` if the job description differs and isn't one of
                the equivalent-title pairs above.
        """
        equivalent_job_titles = (
            {JOB_TITLE_POSTDOCTORAL_RESEARCHER, JOB_TITLE_ASSOCIATED_RESEARCHER},
            {JOB_TITLE_GROUP_LEADER_ICREA, JOB_TITLE_GROUP_LEADER},
        )
        if {self.job_description, researcher.job_description} in equivalent_job_titles:
            return False

        return bool(self.job_description != researcher.job_description)

    def is_visitor(self) -> bool:
        """Whether this researcher is a short-term visitor, who shouldn't be
        loaded into iMarina.

        Center code 4 (VISITOR_CENTER_CODE) generally marks a visitor, but
        ICREA group leaders and CSC-scholarship predoctoral researchers are
        also filed under code 4 despite not being visitors. Per policy,
        code-4 people should be disambiguated using their ini/end date span
        (a real visit is under about a year) - the job-description keyword
        check below only catches the ICREA case (title contains "leader"),
        not CSC predocs, since a predoc's title doesn't match any of
        PERMANENT_POSITION_KEYWORDS.

        NOTE: the duration check described above isn't implemented for the
        code_center == VISITOR_CENTER_CODE branch - only the keyword check
        is. This means a code-4 CSC predoc is currently misclassified as a
        visitor. Flagging this since it doesn't match the policy above -
        fix if that's unintentional.
        """
        # Center code 4 tends to be a visitor
        if self.code_center == VISITOR_CENTER_CODE:
            job = str(self.job_description).lower()

            # If the job_description contains one of those keywords, then it's NOT a visitor
            return not any(key in job for key in PERMANENT_POSITION_KEYWORDS)

        if self.ini_date and self.end_date:
            duration = (self.end_date - self.ini_date).days
            if (
                duration < VISITOR_MAX_DURATION_DAYS
            ):  # Less than 3 months is almost always a VISITOR
                return True

        return False


# normalize the researcher's name
def normalize_name(name: str) -> str:
    """
    Normalizes a researcher's (first/sur)name to title case.

    Only converts names that are entirely uppercase or entirely lowercase
    (as A3/iMarina exports often are); a name with mixed case is assumed to
    already be correctly cased and is left untouched.

    Args:
        name (str): The raw name value.

    Returns:
        str: The title-cased name, stripped of surrounding whitespace, or
            `""` if `name` isn't a non-blank string.
    """
    if not isinstance(name, str) or not name.strip():
        return ""

    name = name.strip()

    fixed = name.title() if name.isupper() or name.islower() else name

    return fixed
