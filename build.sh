set -e

python3 tools/vault.py --infile=env.prod --outfile=src/.env

echo "export CUSTOM_GIT_COMMIT_HASH='`git rev-parse HEAD`'" >> src/.env

cp requirements-prod.txt requirements.txt
docker build -t backend_base --file Dockerfile.api .
docker build -t nginx --file Dockerfile.nginx .
