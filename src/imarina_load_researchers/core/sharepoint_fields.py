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
(field names and the "Workflow State" state machine), per CLAUDE.md's
"Microsoft List schema" section.

All five internal Graph API field names below are confirmed against
production via a Graph GET (`.../lists/{list}/columns`).

- `FIELD_WORKFLOW_STATE`'s internal name (`Estat_x0028_Workflow_x0029_`) is
  the `_x0020_`/`_x0028_`/`_x0029_` encoding of an earlier Catalan display
  name, "Estat (Workflow)" — not of the current English display name
  "Workflow State". It's a Choice column; the allowed values are exactly
  `WorkflowState`'s members.
- `FIELD_A3_EXCEL_INPUT_LINK` / `FIELD_IMARINA_EXCEL_INPUT_LINK` /
  `FIELD_IMARINA_EXCEL_OUTPUT_LINK` / `FIELD_IMARINA_EXCEL_PUBLISHED_LINK`
  were originally "Hyperlink or Picture" columns. That column type cannot be
  written through Graph's `.../items/{id}/fields` PATCH at all — every
  format tried (plain string, the `{"Url", "Description"}` object Graph's
  own GET returns for a populated hyperlink field, v1.0 vs beta) comes back
  `400 invalidRequest`, and the SharePoint REST API (`_api/web/lists/...`)
  isn't a usable workaround either: it rejects this app's Azure AD
  client-credentials tokens outright ("Unsupported app only token") since it
  only accepts delegated tokens or legacy ACS "add-in-only" tokens from a
  separate SharePoint-registered principal, which this app doesn't have.
  Graph also refuses to convert an existing Hyperlink-or-Picture column to
  Text in place (`400 "Provided data is not compatible with target field
  type"` on `PATCH columns/{id}` with a `text` facet) — matching
  SharePoint's own "Edit column" UI, which doesn't offer that conversion
  either. So as of 2026-08-25 these 4 columns were deleted and recreated as
  plain single-line-of-text columns (same displayName/description,
  `text: {}` facet), which is why their internal names carry a trailing `0`
  — Graph auto-suffixes a new column's name when a just-deleted column of
  the same name is still in the site's recycle bin. Plain-string PATCH
  writes work against a Text column the same way they already did against
  `FIELD_WORKFLOW_STATE` (a Choice column) — the Hyperlink/Picture type was
  the whole problem, not the field name or the value's format.

If any of these columns is ever recreated from scratch again, its internal
name will change again — re-confirm with the same Graph GET
(`.../lists/{list}/columns` or `.../items/{id}?$expand=fields`) and fix the
constant here; nothing else in the codebase needs to change.
"""

from enum import StrEnum

# Confirmed against production (Graph GET on `.../lists/{list}/columns`).
FIELD_A3_EXCEL_INPUT_LINK = "A3ExcelInputLink0"
FIELD_IMARINA_EXCEL_INPUT_LINK = "iMarinaExcelInputLink0"
FIELD_IMARINA_EXCEL_OUTPUT_LINK = "iMarinaExcelOutputLink0"
FIELD_IMARINA_EXCEL_PUBLISHED_LINK = "iMarinaExcelPublishedLink0"
FIELD_WORKFLOW_STATE = "Estat_x0028_Workflow_x0029_"


class WorkflowState(StrEnum):
    """Values of the "Workflow State" MS List field, per CLAUDE.md's
    "Microsoft List schema" section.

    Must be StrEnum, not `(str, Enum)`: these values are f-string-interpolated
    into JSON PATCH bodies sent to Graph, and only StrEnum makes
    f"{WorkflowState.NEW}" render as "New" rather than "WorkflowState.NEW"
    (see CLAUDE.md's SecretName gotcha for the same failure mode).
    """

    NEW = "New"
    PREPARING_POWER_AUTOMATE = "Preparing (Power Automate)"
    PREPARING = "Preparing"
    BUILDING = "Building"
    UPLOADING = "Uploading"
    REQUESTED_REVIEW = "Requested review"
    NOT_PUBLISHED = "Not published"
    APPROVED_PUBLICATION = "Approved publication"
    PUBLISHING = "Publishing"
    PUBLISHED = "Published"
    ERROR = "Error"
