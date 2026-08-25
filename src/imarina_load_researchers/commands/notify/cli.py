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

from imarina_load_researchers.core.defines import DEFAULT_NOTIFY_SHAREPOINT_PATH
from imarina_load_researchers.core.log_utils import get_logger
from imarina_load_researchers.core.mail import (
    EmailContent,
    WorkflowStatus,
    build_error_body,
    build_published_body,
    build_success_body,
    get_access_token,
    get_creator_email,
    send_email,
)
from imarina_load_researchers.core.secret import SecretName, read_secret
from imarina_load_researchers.core.shared_options import (
    NotifyIdOpt,
    NotifySharepointPathOpt,
    NotifyStatusOpt,
)
from imarina_load_researchers.core.sharepoint import (
    get_list_id,
    get_site_id,
    get_token_manager,
    update_list_item_fields,
)
from imarina_load_researchers.core.sharepoint_fields import (
    FIELD_WORKFLOW_STATE,
    WorkflowState,
)

logger = get_logger(__name__)


def notify_controller(
    id_element: NotifyIdOpt,
    status: NotifyStatusOpt,
    sharepoint_path: NotifySharepointPathOpt = DEFAULT_NOTIFY_SHAREPOINT_PATH,
) -> None:
    """
    Sends the creator of the MS List item an email reporting the outcome of
    a run: "success" (upload finished, awaiting review) from the main
    download/build/upload pipeline, or "published"/"error" from either that
    pipeline or the separate, approval-gated publish pipeline
    (publish.Jenkinsfile).

    On a failure status, also updates the request's Workflow State field to
    "Error" (STEPS.md) -- notify is the common failure handler called from
    every step's error path, so this is the single place that write happens,
    rather than duplicating it in download/build/upload/publish.
    """

    site_id = get_site_id(
        get_token_manager(),
        read_secret(SecretName.SHAREPOINT_DOMAIN),
        read_secret(SecretName.SITE_NAME),
    )
    list_id = get_list_id(
        get_token_manager(), site_id, read_secret(SecretName.LIST_NAME)
    )

    logger.info("Getting access token...")
    token = get_access_token(
        read_secret(SecretName.TENANT_ID),
        read_secret(SecretName.CLIENT_ID),
        read_secret(SecretName.CLIENT_SECRET),
    )

    logger.info(f"Getting creator info for item ID {id_element}...")
    to_email, name = get_creator_email(token, site_id, list_id, str(id_element))
    logger.info(f"Sending email to: {to_email} ({name})")

    if status == WorkflowStatus.SUCCESS:
        subject = f"iMarina - Workflow ID {id_element} completed successfully"
        body = build_success_body(name, str(id_element), str(sharepoint_path))
    elif status == WorkflowStatus.PUBLISHED:
        subject = f"iMarina - Workflow ID {id_element} published to iMarina"
        body = build_published_body(name, str(id_element))
    else:
        subject = f"iMarina - Workflow ID {id_element} failed"
        body = build_error_body(name, str(id_element))
        try:
            update_list_item_fields(
                str(id_element), {FIELD_WORKFLOW_STATE: WorkflowState.ERROR}
            )
        except Exception:
            # Best-effort bookkeeping: must not block the error email below.
            logger.exception("Error updating Workflow State to Error")

    smtp_user = read_secret(SecretName.SMTP_USERNAME)
    send_email(
        EmailContent(
            to_email=to_email, subject=subject, body=body, from_email=smtp_user
        ),
        smtp_user,
        read_secret(SecretName.SMTP_PASSWORD),
        read_secret(SecretName.SMTP_HOST),
        int(read_secret(SecretName.SMTP_PORT)),
    )
    logger.info("Email sent. Process complete.")
