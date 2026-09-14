#!/usr/bin/env bash

set -euo pipefail

IMAGE_TAG="${1:?Usage: bash scripts/deploy.sh <image-tag>}"
PROJECT_DIR="/home/ubuntu/apps/resturantordering"
AWS_REGION="eu-central-1"
ECR_REGISTRY="272086646330.dkr.ecr.eu-central-1.amazonaws.com"
IMAGE="$ECR_REGISTRY/restohubapi-web:$IMAGE_TAG"

cd "$PROJECT_DIR"

aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$ECR_REGISTRY"

export IMAGE_TAG
COMPOSE=(
  docker compose
  --env-file .env.prod
  -f docker-compose.yml
  -f docker-compose.prod.yml
)

"${COMPOSE[@]}" pull web
"${COMPOSE[@]}" up -d

CONTAINER_ID="$("${COMPOSE[@]}" ps -q web)"
DEPLOYED_IMAGE="$(docker inspect --format '{{.Config.Image}}' "$CONTAINER_ID")"

if [[ "$DEPLOYED_IMAGE" != "$IMAGE" ]]; then
  echo "Expected $IMAGE, but the web container uses $DEPLOYED_IMAGE" >&2
  exit 1
fi

for attempt in {1..12}; do
  if curl --fail --silent --show-error --output /dev/null \
    https://restohubapi.duckdns.org/api/docs/; then
    echo "Deployment succeeded with image $IMAGE"
    exit 0
  fi

  echo "Waiting for the API to become healthy ($attempt/12)..."
  sleep 5
done

"${COMPOSE[@]}" logs --tail=100 web
echo "Deployment failed: the API did not become healthy" >&2
exit 1
