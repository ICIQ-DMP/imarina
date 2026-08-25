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

All five internal Graph API field names below are now confirmed against
production via a Graph GET (`.../lists/{list}/columns`). None of them follow
the naive "replace each space with `_x0020_`" encoding of the current
*display* name:

- `FIELD_A3_EXCEL_INPUT_LINK` / `FIELD_IMARINA_EXCEL_INPUT_LINK` are
  unchanged from before STEPS.md renamed the columns' display names —
  SharePoint does not change a column's internal name when its display name
  is edited, only when the column is recreated from scratch.
- `FIELD_WORKFLOW_STATE`'s internal name (`Estat_x0028_Workflow_x0029_`) is
  the `_x0020_`/`_x0028_`/`_x0029_` encoding of an earlier Catalan display
  name, "Estat (Workflow)" — not of the current English display name
  "Workflow State".
- `FIELD_IMARINA_EXCEL_OUTPUT_LINK` / `FIELD_IMARINA_EXCEL_PUBLISHED_LINK`
  carry no space encoding at all (`iMarinaExceloutputlink`,
  `iMarinaExceluploadlink`) — both columns were created with the internal
  name derived from an earlier, space-free working title, then had only
  their display name edited afterwards (the published-link column's display
  name is "iMarina Excel published link", but its internal name still says
  "upload", not "published").

If any of these columns is ever recreated from scratch, its internal name
will change again — re-confirm with the same Graph GET
(`.../lists/{list}/columns` or `.../items/{id}?$expand=fields`) and fix the
constant here; nothing else in the codebase needs to change.
"""

from enum import StrEnum

# Confirmed against production (Graph GET on `.../lists/{list}/columns`).
FIELD_A3_EXCEL_INPUT_LINK = "A3_x0020_Excel_x0020_Link"
FIELD_IMARINA_EXCEL_INPUT_LINK = "iMarina_x0020_Excel_x0020_Link"
FIELD_IMARINA_EXCEL_OUTPUT_LINK = "iMarinaExceloutputlink"
FIELD_IMARINA_EXCEL_PUBLISHED_LINK = "iMarinaExceluploadlink"
FIELD_WORKFLOW_STATE = "Estat_x0028_Workflow_x0029_"


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
