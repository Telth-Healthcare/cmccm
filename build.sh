#!/bin/bash
pip install -r requirements/local.txt
python natlife/manage.py collectstatic --noinput --clear
