#!/bin/bash

set -eu -o pipefail

export DJANGO_SETTINGS_MODULE=mysite.settings.test

python manage.py reset_db --noinput

rm -rf general_ledger/migrations/*.py
touch general_ledger/migrations/__init__.py

python manage.py makemigrations

python manage.py migrate

#python manage.py dumpdata --format yaml \
#    general_ledger.user -o ./general_ledger/fixtures/users.yaml

python manage.py loaddata \
    --format yaml \
    general_ledger/fixtures/users.yaml
