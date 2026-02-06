# from imarina.core.Researcher import Researcher
from imarina.core.a3_mapper import A3_Field
from dataclasses import dataclass

from datetime import date, datetime

translator = {
    A3_Field.JOB_DESCRIPTION: {
        "Investigador": "Researcher",
        "Técnico": "Technician",
        "Group Leader Starting Career": "Group Leader",
        "Director/a Administrativo/a": "Administrative/Director",
        "Coordinador/a científico/a de laboratorio": "Scientific Coordinator",
        "visitantes": "Visitors",
        "Asistente dirección": "Technician",
        "Técnico de laboratorio": "Laboratory Technician",
    }
}


@dataclass
class Researcher:
    name: str
    job_description: str
    ini_date: date | None = None
    end_date: date | None = None
    ini_prorrog: date | None = None
    end_prorrog: date | None = None
    date_termination: date | None = None


def d(s: str):  # petit helper per fer dates ràpid
    return datetime.strptime(s, "%d/%m/%Y").date()
