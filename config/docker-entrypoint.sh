#! /bin/sh

set -e

cd /app

python manage.py migrate

uwsgi --ini uwsgi.ini
