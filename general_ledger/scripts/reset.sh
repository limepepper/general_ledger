#!/bin/bash

set -eu -o pipefail

APP_NAME="general_ledger"

echo "Resetting migrations for app: $APP_NAME"

rm -rf general_ledger/migrations/*.py
touch general_ledger/migrations/__init__.py

python manage.py dbshell <<EOF
    DELETE FROM django_migrations WHERE app = '$APP_NAME';
EOF

echo "dropping tables for app: $APP_NAME"
python manage.py reset_gl | while IFS= read -r line; do
  # do something with $line
  echo "DROP TABLE $line" | python manage.py dbshell
done

# Make new migrations
# python manage.py makemigrations $APP_NAME

# python manage.py migrate $APP_NAME
