#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py migrate
python manage.py collectstatic --no-input
python load_data.py

uwsgi --socket :9000 --workers 4 --master --enable-threads --module config.wsgi