from imarina.core.log_utils import get_logger
from imarina.core.str_utils import normalize_name_str

logger = get_logger(__name__)


class Researcher:

    def __init__(self, **kwargs):
        self.dni = kwargs.get("dni")
        self.email = kwargs.get("email")
        self.name = kwargs.get("name")
        self.surname = kwargs.get("surname")
        self.second_surname = kwargs.get("second_surname")
        self.orcid = kwargs.get("orcid")
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
        self.employee_code = kwargs.get("employee_code")
        self.code_center = kwargs.get("code_center")
        self.adscription_type = kwargs.get("adscription_type")
        self.entity = kwargs.get("entity")
        self.entity_type = kwargs.get("entity_type")
        self.entity_web = kwargs.get("entity_web")
        self.id_one = kwargs.get("id_one")
        self.id_two = kwargs.get("id_two")
        self.id_three = kwargs.get("id_three")
        self.entity_country = kwargs.get("entity_country")
        self.entity_community = kwargs.get("entity_community")
        self.entity_web = kwargs.get("entity_web")
        self.entity_name = kwargs.get("entity_name")
        self.entity_city = kwargs.get("entity_city")
        self.entity_code = kwargs.get("entity_code")
        self.entity_direction = kwargs.get("entity_direction")
        self.entity_type2 = kwargs.get("entity_type2")
        self.entity_type3 = kwargs.get("entity_type3")
        self.entity2 = kwargs.get("entity2")
        self.research_id = kwargs.get("research_id")
        self.author_id = kwargs.get("author_id")
        self.dialnet_id = kwargs.get("dialnet_id")
        self.google_scholar = kwargs.get("google_scholar")
        self.contact_country = kwargs.get("contact_country")
        self.community_contact = kwargs.get("community_contact")
        self.contact_province = kwargs.get("contact_province")
        self.contact_city = kwargs.get("contact_city")
        self.code_contact = kwargs.get("code_contact")
        self.contact_direction = kwargs.get("contact_direction")
        self.contact_phone = kwargs.get("contact_phone")
        self.bio = kwargs.get("bio")




    def __str__(self):
        return (
            f"\nResearcher:\n"
            f"  DNI: {self.dni}\n"
            f"  Email: {self.email}\n"
            f"  Name: {self.name}\n"
            f"  Surname: {self.surname}\n"
            f"  Second Surname: {self.second_surname}\n"
            f"  ORCID: {self.orcid}\n"
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
            f"  Entity: {self.entity}\n"
            f"  Entity type: {self.entity_type}\n"
            f"  Entity web: {self.entity_web}\n"
            f"  Id One : {self.id_one}\n"
            f"  Id two: {self.id_two}\n"
            f"  Id three: {self.id_three}\n"
            f"  Entity country: {self.entity_country}\n"
            f"  Entity community: {self.entity_community}\n"
            f"  Entity name: {self.entity_name}\n"
            f"  Entity city: {self.entity_city}\n"
            f"  Entity code: {self.entity_code}\n"
            f"  Entity direction: {self.entity_direction}\n"
            f"  Entity type 2: {self.entity_type2}\n"
            f"  Entity type 3: {self.entity_type3}\n"
            f"  Entity 2: {self.entity2}\n"
            f"  Research ID: {self.research_id}\n"
            f"  Author ID: {self.author_id}\n"
            f"  Dialnet ID: {self.dialnet_id}\n"
            f"  Google scholar: {self.google_scholar}\n"
            f"  Contact country: {self.contact_country}\n"
            f"  Contact Community: {self.community_contact}\n"
            f"  Contact Province: {self.contact_province}\n"
            f"  Contact City: {self.contact_city}\n"
            f"  Contact Code: {self.code_contact}\n"
            f"  Contact Direction: {self.contact_direction}\n"
            f"  Contact Phone: {self.contact_phone}\n"
            f"  Bio: {self.bio}\n"



        )

    def copy(self):
        return Researcher(
            code_center=self.code_center,
            dni=self.dni,
            email=self.email,
            name=self.name,
            surname=self.surname,
            second_surname=self.second_surname,
            orcid=self.orcid,
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
            adscription_type=self.adscription_type,
            entity=self.entity,
            entity_type=self.entity_type,
            entity_web=self.entity_web,
            entity2=self.entity2,
            entity_type2=self.entity_type2,
            entity_type3=self.entity_type3,
            id_one=self.id_one,
            id_two=self.id_two,
            id_three=self.id_three,
            entity_country=self.entity_country,
            entity_community=self.entity_community,
            entity_name=self.entity_name,
            entity_city=self.entity_city,
            entity_code=self.entity_code,
            entity_direction=self.entity_direction,
            research_id=self.research_id,
            author_id=self.author_id,
            dialnet_id=self.dialnet_id,
            google_scholar=self.google_scholar,
            contact_country=self.contact_country,
            community_contact=self.community_contact,
            contact_province=self.contact_province,
            contact_city=self.contact_city,
            code_contact=self.code_contact,
            contact_direction=self.contact_direction,
            contact_phone=self.contact_phone,
            bio=self.bio,

        )

    def search_data(self, data_input):
        matches = []

        for researcher in data_input:
            if self.is_same_person(researcher):
                matches.append(researcher)

        if matches:
            same_ini = [r for r in matches if r.ini_date == self.ini_date]
            return same_ini if len(same_ini) == 1 else matches

        return []

    def is_same_person(self, other):
        if self.orcid and other.orcid and self.orcid == other.orcid:
            return True
        if self.dni and other.dni and self.dni == other.dni:
            return True
        if self.email and other.email and self.email == other.email:
            return True
        # surname de ambos TODO: fragile
        # if self.name and other.name and self.surname and other.surname and normalize_name_str(self.name) == normalize_name_str(other.name) and normalize_name_str(self.surname) == normalize_name_str(other.surname):
        #    return True

        # match por nombre
        im_n = normalize_name_str(getattr(self, "name", ""))
        a3_n = normalize_name_str(getattr(other, "name", ""))
        im_s = normalize_name_str(getattr(self, "surname", ""))
        a3_s = normalize_name_str(getattr(other, "surname", ""))

        if im_s and a3_s and im_s == a3_s and im_n == a3_n:
            return True

        return False

    def has_changed_jobs(self, researcher):

        # si son iguales no ha cambiado
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


def apply_defaults(researcher: Researcher):
    researcher.personal_web = "https://iciq.es"


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
