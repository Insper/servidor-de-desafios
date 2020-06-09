#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py flush --no-input
python manage.py migrate
python manage.py collectstatic --no-input --clear --settings=servidor_dessoft.settings.production

exec "$@"