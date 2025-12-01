# books/scheduler.py
"""
Background scheduler for one-off async tasks like book summary generation.
This scheduler is used for tasks triggered by user actions that need to run asynchronously.

For recurring scheduled tasks (like cron jobs), use the management command:
    python manage.py scheduler

IMPORTANT: This scheduler is started automatically when Django starts (see books/apps.py).
Do not manually call scheduler.start() anywhere else.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.conf import settings

# Create the scheduler instance but DO NOT start it here
# It will be started in the BooksConfig.ready() method in apps.py
scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
scheduler.add_jobstore(DjangoJobStore(), "default")
