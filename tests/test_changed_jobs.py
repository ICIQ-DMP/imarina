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

# from imarina.core.researcher import Researcher
from dataclasses import dataclass
from datetime import date, datetime

from imarina.core.a3_mapper import A3_Field
from imarina.core.defines import MADRID_TZ

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
    return datetime.strptime(s, "%d/%m/%Y").replace(tzinfo=MADRID_TZ).date()
