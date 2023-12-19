#!/bin/sh
cd decide/
cp local_settings.deploy.py local_settings.py
celery -A decide worker -l info 