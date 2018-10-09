#!/bin/bash

python manage.py db upgrade

uwsgi --socket 0.0.0.0:5000 --wsgi-file manage.py --master
