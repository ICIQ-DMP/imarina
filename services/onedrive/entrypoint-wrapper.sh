#!/bin/bash
# Renders conf/config.template into conf/config, injecting DRIVE_ID from the
# Docker secret, then hands off to the onedrive image's own entrypoint.sh so
# behaviour (user/group handling, arg building from ONEDRIVE_* env vars,
# gosu drop-privileges) stays identical to running the image unwrapped.
set -euo pipefail

CONF_DIR="/onedrive/conf"
TEMPLATE="${CONF_DIR}/config.template"
CONFIG="${CONF_DIR}/config"
SECRET_FILE="/run/secrets/DRIVE_ID"

if [ ! -f "${TEMPLATE}" ]; then
	echo "onedrive entrypoint-wrapper: missing ${TEMPLATE}" >&2
	exit 1
fi

if [ ! -f "${SECRET_FILE}" ]; then
	echo "onedrive entrypoint-wrapper: missing secret file ${SECRET_FILE}" >&2
	exit 1
fi

DRIVE_ID="$(cat "${SECRET_FILE}")"

while IFS= read -r line || [ -n "${line}" ]; do
	echo "${line//__DRIVE_ID__/${DRIVE_ID}}"
done <"${TEMPLATE}" >"${CONFIG}"

exec /entrypoint.sh "$@"
