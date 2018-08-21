set -e

if [ -z "${1}" ]; then
  echo "you must pass the name of an image (e.g. backend_base)"
  exit 1
fi

IMAGE_NAME=$1
VERSION=$(git rev-parse HEAD)

docker tag ${IMAGE_NAME}:latest <AWS_ECR_URL>/${IMAGE_NAME}:latest
docker tag ${IMAGE_NAME}:latest <AWS_ECR_URL>/${IMAGE_NAME}:${VERSION}

curl -d '{"app_type":"backend", "git_hash":"'$VERSION'"}' -H "Content-Type: application/json" -H "Authorization: Bearer `cat .internal-auth-key`" -X POST https://api.SITE_URL/api/internal/app_versions/

$(aws ecr get-login --no-include-email --region us-west-2)
docker push <AWS_ECR_URL>/${IMAGE_NAME}:${VERSION}
docker push <AWS_ECR_URL>/${IMAGE_NAME}:latest
