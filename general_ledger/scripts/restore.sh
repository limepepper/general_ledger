#!/bin/bash

set -eu -o pipefail

export DJANGO_SETTINGS_MODULE=dashboard.settings



python manage.py makemigrations

python manage.py migrate

#python manage.py dumpdata --format yaml \
#    general_ledger.user -o ./general_ledger/fixtures/users.yaml

python manage.py loaddata \
    --format yaml \
    general_ledger/fixtures/users.yaml
