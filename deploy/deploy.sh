#!/usr/bin/env bash
set -Eeuo pipefail

: "${IMAGE_REPO:?IMAGE_REPO is required}"
: "${IMAGE_TAG:?IMAGE_TAG is required}"

ENV_FILE=".env"
BACKUP_FILE=".env.previous"
PROJECT_NAME="${PROJECT_NAME:-hello-deploy}"

compose() {
  docker compose --project-name "${PROJECT_NAME}" "$@"
}

if [[ -f "${ENV_FILE}" ]]; then
  cp "${ENV_FILE}" "${BACKUP_FILE}"
fi

cat > "${ENV_FILE}" <<EOF_ENV
IMAGE_REPO=${IMAGE_REPO}
IMAGE_TAG=${IMAGE_TAG}
APP_ENV=${APP_ENV:-production}
PUBLIC_PORT=${PUBLIC_PORT:-80}
FORCE_UNHEALTHY=${FORCE_UNHEALTHY:-false}
EOF_ENV
chmod 600 "${ENV_FILE}"

echo "Pulling ${IMAGE_REPO}:${IMAGE_TAG}"
compose pull app proxy

echo "Starting candidate release"
compose up --detach --remove-orphans

container_id="$(compose ps --quiet app)"
if [[ -z "${container_id}" ]]; then
  echo "Application container was not created."
  exit 1
fi

echo "Waiting for application health"
for attempt in {1..20}; do
  health_status="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "${container_id}" 2>/dev/null || true)"
  echo "Attempt ${attempt}/20: ${health_status:-unknown}"

  if [[ "${health_status}" == "healthy" ]]; then
    echo "Deployment succeeded: ${IMAGE_TAG}"
    docker image prune --force >/dev/null 2>&1 || true
    exit 0
  fi

  sleep 3
done

echo "Candidate release failed its health check."
compose logs --tail=100 app || true

if [[ -f "${BACKUP_FILE}" ]]; then
  echo "Rolling back to the previous release."
  cp "${BACKUP_FILE}" "${ENV_FILE}"
  compose pull app proxy
  compose up --detach --remove-orphans

  rollback_id="$(compose ps --quiet app)"
  for attempt in {1..20}; do
    rollback_status="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "${rollback_id}" 2>/dev/null || true)"
    echo "Rollback attempt ${attempt}/20: ${rollback_status:-unknown}"
    if [[ "${rollback_status}" == "healthy" ]]; then
      echo "Rollback succeeded. Previous healthy release restored."
      exit 1
    fi
    sleep 3
  done

  echo "Rollback was attempted but the previous release is not healthy."
else
  echo "No previous release is available for rollback."
fi

exit 1
