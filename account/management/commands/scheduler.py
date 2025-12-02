# scheduler.py
import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from apscheduler.triggers.interval import IntervalTrigger
from account.tasks import clear_otps, test_scheduler_job

logger = logging.getLogger(__name__)


def my_job():
    """Your job processing logic here..."""
    print("JOB RUNNING!!")
    pass


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.
    
    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
    logger.info(f"✓ Deleted job executions older than {max_age} seconds")


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        logger.info("=" * 50)
        logger.info("APScheduler is starting...")
        logger.info("=" * 50)

        # DAILY OTP CLEANUP JOB
        scheduler.add_job(
            clear_otps,
            trigger=CronTrigger(hour="02", minute="00"),  # 2:00AM EVERYDAY
            id="daily_otp_cleanup",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("✓ Added job: 'daily_otp_cleanup' - Runs daily at 2:00 AM UTC")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),  # Monday Midnight
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("✓ Added job: 'delete_old_job_executions' - Runs every Monday at midnight UTC")

        # TEST JOB - Runs daily at 5:55 PM UTC for testing
        scheduler.add_job(
            test_scheduler_job,
            trigger=CronTrigger(hour="17", minute="55"),  # 5:55 PM UTC daily
            id="test_scheduler_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("✓ Added job: 'test_scheduler_job' - Runs daily at 5:55 PM UTC (FOR TESTING)")

        # List all registered jobs
        logger.info("=" * 50)
        logger.info(f"Total jobs registered: {len(scheduler.get_jobs())}")
        logger.info("=" * 50)

        try:
            logger.info("🚀 Starting scheduler... Press Ctrl+C to exit")
            scheduler.start()
            
            # NOW log the next run times AFTER scheduler starts
            # (This won't actually run because scheduler.start() is blocking)
            
        except KeyboardInterrupt:
            logger.info("⏹️  Stopping scheduler...")
            scheduler.shutdown()
            logger.info("✓ Scheduler shut down successfully!")