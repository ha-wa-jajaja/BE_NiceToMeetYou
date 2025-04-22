#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py load_tags

uwsgi --socket :9000 --workers 4 --master --enable-threads --module udn_nba.wsgi
