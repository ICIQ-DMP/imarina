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

"""Microsoft List schema for the request-tracking list backing this workflow
(field names and the "Workflow State" state machine), per STEPS.md.

Internal Graph API field names for `FIELD_A3_EXCEL_INPUT_LINK` and
`FIELD_IMARINA_EXCEL_INPUT_LINK` are confirmed from production (they're
unchanged from before STEPS.md renamed the columns' *display* names —
SharePoint does not change a column's internal name when its display name is
edited, only when the column is recreated from scratch).

The other three constants (`FIELD_IMARINA_EXCEL_OUTPUT_LINK`,
`FIELD_IMARINA_EXCEL_PUBLISHED_LINK`, `FIELD_WORKFLOW_STATE`) are NOT verified
against the live tenant: those columns didn't exist before STEPS.md, so
there's no production value to confirm against yet. They're a best-effort
guess at SharePoint's standard "replace each space with `_x0020_`" internal
name encoding, applied to STEPS.md's display names. Once those columns exist
in the real list, confirm the actual internal names with a Graph GET
(`.../items/{id}?$expand=fields`) and fix these three constants if they're
wrong — nothing else in the codebase needs to change.
"""

from enum import StrEnum

# Confirmed against production.
FIELD_A3_EXCEL_INPUT_LINK = "A3_x0020_Excel_x0020_Link"
FIELD_IMARINA_EXCEL_INPUT_LINK = "iMarina_x0020_Excel_x0020_Link"

# NOT verified against the live tenant -- see module docstring.
FIELD_IMARINA_EXCEL_OUTPUT_LINK = "iMarina_x0020_Excel_x0020_output_x0020_link"
FIELD_IMARINA_EXCEL_PUBLISHED_LINK = "iMarina_x0020_Excel_x0020_published_x0020_link"
FIELD_WORKFLOW_STATE = "Workflow_x0020_State"


class WorkflowState(StrEnum):
    """Values of the "Workflow State" MS List field, per STEPS.md.

    Must be StrEnum, not `(str, Enum)`: these values are f-string-interpolated
    into JSON PATCH bodies sent to Graph, and only StrEnum makes
    f"{WorkflowState.NEW}" render as "New" rather than "WorkflowState.NEW"
    (see CLAUDE.md's SecretName gotcha for the same failure mode).
    """

    NEW = "New"
    PREPARING = "Preparing"
    BUILDING = "Building"
    UPLOADING = "Uploading"
    REQUESTED_REVIEW = "Requested review"
    NOT_PUBLISHED = "Not published"
    PUBLISHING = "Publishing"
    PUBLISHED = "Published"
    ERROR = "Error"
