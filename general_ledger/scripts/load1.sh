#!/bin/bash

# Make new migrations
python manage.py makemigrations $APP_NAME

python manage.py migrate $APP_NAME

python manage.py loaddata  --format yml general_ledger/fixtures/tax_types.yaml
python manage.py loaddata  --format yml general_ledger/fixtures/account_types.yaml
python manage.py loaddata  --format yml general_ledger/fixtures/tax_rates.yaml
python manage.py loaddata  --format yml general_ledger/fixtures/books.yaml
python manage.py loaddata  --format yml general_ledger/fixtures/ledgers.yaml
python manage.py loaddata  --format yml general_ledger/fixtures/accounts.yaml
