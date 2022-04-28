from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_app.settings")

app = Celery("my_app")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.beat_schedule = {
    'New ads newsletter weekly ': {
        'task': "shop_site.tasks.send_email_task",
        "schedule": crontab(day_of_week=1, hour=9, minute=0),
    },
}

app.autodiscover_tasks()
