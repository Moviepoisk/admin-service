#!/bin/sh

# run
python manage.py migrate movies
python manage.py migrate
python manage.py runserver 0.0.0.0:8000