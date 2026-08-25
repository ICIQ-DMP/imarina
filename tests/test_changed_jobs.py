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

from conftest import build_researcher

from imarina_load_researchers.core.researcher import Researcher


def _researcher(job_description: str) -> Researcher:
    return build_researcher(job_description=job_description)


def test_has_changed_jobs_same_description_is_not_changed():
    before = _researcher("Researcher")
    after = _researcher("Researcher")
    assert before.has_changed_jobs(after) is False


def test_has_changed_jobs_different_description_is_changed():
    before = _researcher("Researcher")
    after = _researcher("Technician")
    assert before.has_changed_jobs(after) is True


def test_has_changed_jobs_postdoc_and_associated_researcher_is_not_changed():
    # Special case: these two titles are treated as the same job.
    postdoc = _researcher("Postdoctoral researcher")
    associated = _researcher("Associated researcher")
    assert postdoc.has_changed_jobs(associated) is False
    assert associated.has_changed_jobs(postdoc) is False


def test_has_changed_jobs_icrea_professor_and_group_leader_is_not_changed():
    # Special case: ICREA-funded group leaders are also just "Group Leader".
    icrea_professor = _researcher("Group Leader / ICREA Professor")
    group_leader = _researcher("Group Leader")
    assert icrea_professor.has_changed_jobs(group_leader) is False
    assert group_leader.has_changed_jobs(icrea_professor) is False
