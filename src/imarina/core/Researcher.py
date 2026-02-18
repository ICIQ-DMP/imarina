from imarina.core.log_utils import get_logger
from typing import Any
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

    def __str__(self)-> Any:
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

    def is_same_person(self, other:Any)-> bool:
        if self.orcid and other.orcid and self.orcid == other.orcid:
            return True
        if self.dni and other.dni and self.dni == other.dni:
            return True
        if self.email and other.email and self.email == other.email:
            return True

        return False

    def has_changed_jobs(self, researcher: Any)-> Any:
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

        if self.job_description == researcher.job_description:
            return False

        return True

    def is_visitor(self) -> bool:
        #  Si es codigo centro 4 tiende a ser  visitante
        if self.code_center == 4:

            job = str(self.job_description).lower()
            permanent_keywords = [
                "leader",
                "manager",
                "principal",
                "head",
            ]  # estos puestos normalmente no son visitantes ya que son puestos fijos

            if any(
                key in job for key in permanent_keywords
            ):  # Si el job_description contiene una de esas keywords entonces
                return False  # retorna False == NO VISITANTE

            return True

        if self.ini_date and self.end_date:
            duration = (self.end_date - self.ini_date).days
            if duration < 90:  # Menos de 3 meses es casi siempre VISITANTE
                return True

        return False


# normalitzar el nom del researcher
def normalize_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        return ""

    name = name.strip()

    if name.isupper() or name.islower():
        fixed = name.title()

    else:
        fixed = name

    return fixed
