import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "udn_nba.settings")

# Create the celery app
app = Celery("udn_nba")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Run every day at 12:00 PM Taiwan time (UTC+8)
    "scrape-daily-at-noon-gmt+8": {
        "task": "news.tasks.fetch_news",
        "schedule": crontab(hour="4", minute="0"),  # 4:00 UTC = 12:00 Taiwan
    },
    # DEBUG SCHEDULE: Run every minute
    # "test-scrape-every-minute": {
    #     "task": "news.tasks.fetch_news",
    #     "schedule": crontab(minute="*"),  # Run every minute
    # },
}
