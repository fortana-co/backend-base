#!/bin/sh
. ./.env
celery worker -A config -c 4 -Ofair
