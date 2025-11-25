#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

docker stop onedrive
docker rm onedrive

echo "Running on ${SCRIPT_DIR}"

sp_path="Institutional Strengthening/_Projects/iMarina_load_automation/input"

mkdir -p "${SCRIPT_DIR}/conf"
mkdir -p "${SCRIPT_DIR}/data"
mkdir -p "${SCRIPT_DIR}/logs"

echo "*
!.gitignore
!config" > "${SCRIPT_DIR}/conf/.gitignore"

echo "*
!.gitignore" > "${SCRIPT_DIR}/data/.gitignore"

echo "*
!.gitignore" > "${SCRIPT_DIR}/logs/.gitignore"

docker run \
  -it \
  --name onedrive \
  --userns host \
  -v ${SCRIPT_DIR}/conf:/onedrive/conf \
  -v ${SCRIPT_DIR}/data:/onedrive/data \
  -v ${SCRIPT_DIR}/logs:/onedrive/logs \
  -l io.containers.autoupdate=image \
  --restart unless-stopped \
  --health-cmd "sh -c '[ -s /onedrive/conf/items.sqlite3-wal ]'" \
  --health-interval 60s \
  --health-retries 2 \
  --health-timeout 5s \
  docker.io/driveone/onedrive:latest \
  --single-directory "${sp_path}" \
  --monitor \
  --syncdir /onedrive/data \
  --confdir /onedrive/conf
