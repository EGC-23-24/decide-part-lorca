import os
import ssl

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "decide.settings")

if settings.DEBUG:
    app = Celery("decide")
else:
    app = Celery(
        "decide",
        broker_use_ssl={
            'ssl_cert_reqs': ssl.CERT_NONE,
        },
        redis_backend_use_ssl={
            'ssl_cert_reqs': ssl.CERT_NONE
        }
    )


app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
