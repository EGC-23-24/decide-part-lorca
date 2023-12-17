import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "decide.settings")

app = Celery("decide")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
