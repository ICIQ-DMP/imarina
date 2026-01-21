from imarina.core.Researcher import Researcher
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


# # test para comprobar si el researcher ha cambiado de posicion is True if has_changed_job
# def test_change_position():
#     """Detecta si ha canviat la posició (job_description)."""
#     a3 = Researcher(
#         "Immaculada Escofet", "Administrative/Director", ini_date=d("03/03/2025")
#     )
#     im = Researcher(
#         "Immaculada Escofet", "Scientific Coordinator", ini_date=d("14/11/2011")
#     )
#     assert has_changed_jobs(a3, im, translator) is True
# TODO: remove personal data, use dummy data, and convert to unit test, do not use a3 data

# COMMENT TEST FAILED
# # test que comprova si la posició es la mateixa, si no hi ha hagut changed job, retorna result False
# def test_debug_same_position():
#     a3 = Researcher("Immaculada Escofet", "Administrative/Director")
#     im = Researcher("Immaculada Escofet", "Administrative/Director")
#
#     result = has_changed_jobs(a3, im, translator)
#     print("Resultat de has_changed_jobs:", result)
#     print("a3:", repr(a3.job_description))
#     print("im:", repr(im.job_description))
#
#     assert result is False


# # fechas distintas, mismo puesto, is true
# def test_change_ini_date_only():
#     """Detecta canvi només per data d'inici diferent."""
#     a3 = Researcher("Immaculada Escofet", "Administrative/Director", ini_date=d("03/03/2025"))
#     im = Researcher("Immaculada Escofet", "Administrative/Director", ini_date=d("14/11/2011"))
#     assert has_changed_jobs(a3, im, translator) is True
#
#
# def test_change_end_date_only():
#     """Detecta canvi només per data de finalització diferent."""
#     a3 = Researcher("Immaculada Escofet", "Administrative/Director", ini_date=d("03/03/2025"), end_date=d("03/03/2026"))
#     im = Researcher("Immaculada Escofet", "Administrative/Director", ini_date=d("03/03/2025"), end_date=d("03/03/2024"))
#     assert has_changed_jobs(a3, im, translator) is True


# def test_missing_ini_date_in_old_record():
#     """Detecta canvi si una de les dues dates falta."""
#     a3 = Researcher("Immaculada Escofet", "Administrative/Director", ini_date=d("03/03/2025"))
#     im = Researcher("Immaculada Escofet", "Administrative/Director", ini_date=None)
#     assert has_changed_jobs(a3, im, translator) is True
