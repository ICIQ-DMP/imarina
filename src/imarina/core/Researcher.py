import pandas as pd

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
            f"  Job description: {self.job_description}\n"
            f"  Code center: {self.code_center}\n"
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
                          )


# FUNCTION IS VISITOR
def is_visitor(researcher_a3: Researcher) -> bool:
    #  Si es codigo centro 4 tiende a ser  visitante
    if researcher_a3.code_center == 4:

        job = str(researcher_a3.job_description).lower()
        permanent_keywords = ["leader", "manager", "principal", "head"]  # estos puestos normalmente no son visitantes ya que son puestos fijos

        if any(key in job for key in permanent_keywords):  # Si el job_description contiene una de esas keywords entonces
            return False      #retorna False == NO VISITANTE

        return True


    if researcher_a3.ini_date and researcher_a3.end_date:
        duration = (researcher_a3.end_date - researcher_a3.ini_date).days
        if duration < 90:  # Menos de 3 meses es casi siempre VISITANTE
            return True

    return False

def apply_defaults(researcher: Researcher):
    researcher.personal_web = "https://iciq.es"


def is_same_person(imarina_row, a3_row):
    def clean(s):
        if not s: return ""
        return str(s).replace("-", "").replace(".", "").strip().lower()

    im_orcid = clean(getattr(imarina_row, "orcid", ""))
    a3_orcid = clean(getattr(a3_row, "orcid", ""))
    im_dni = clean(getattr(imarina_row, "dni", ""))
    a3_dni = clean(getattr(a3_row, "dni", ""))


    if im_orcid and a3_orcid and im_orcid == a3_orcid: return True
    if im_dni and a3_dni and im_dni == a3_dni: return True

    #match por nombre
    im_n = normalize_name_str(getattr(imarina_row, "name", ""))
    a3_n = normalize_name_str(getattr(a3_row, "name", ""))
    im_s = normalize_name_str(getattr(imarina_row, "surname", ""))
    a3_s = normalize_name_str(getattr(a3_row, "surname", ""))

    # surname de ambos
    if im_s and a3_s and im_s == a3_s:
        return True
    # surname y inicial del name
    im_s_set = set(im_s.split())
    a3_s_set = set(a3_s.split())
    if im_s_set.intersection(a3_s_set) and im_n[:1] == a3_n[:1]:
        return True

    return False


# TODO review logic for researchers have_changed job, left and new
def has_changed_jobs(researcher_a3, researcher_im, translator):
    def clean_job(text):
        if not text: return ""
        t = str(text).lower()
        # limpiar caracteres raros y tildes
        replacements = {
            "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
            "-": " ", "_": " ", ".": " "
        }
        for old, new in replacements.items():
            t = t.replace(old, new)


        stop_words = ["researcher", "investigador", "staff", "position", "the", "en", "de"]
        words = [w for w in t.split() if w not in stop_words]
        return " ".join(words).strip()

    job_a3 = clean_job(researcher_a3.job_description)
    job_im = clean_job(researcher_im.job_description)

    # si son iguales no ha cambiado
    if job_a3 == job_im:
        return False


    if job_a3 in job_im or job_im in job_a3:
        return False


    return True




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