# account/management/commands/list_jobs.py
"""
Management command to list all scheduled jobs in the database.
Usage: python manage.py list_jobs
"""
from django.core.management.base import BaseCommand
from django_apscheduler.models import DjangoJob, DjangoJobExecution


class Command(BaseCommand):
    help = "List all APScheduler jobs registered in the database"

    def handle(self, *args, **options):
        jobs = DjangoJob.objects.all()

        if not jobs.exists():
            self.stdout.write(self.style.WARNING("No jobs found in database."))
            self.stdout.write("")
            self.stdout.write("This is normal if:")
            self.stdout.write("  1. The scheduler worker hasn't started yet")
            self.stdout.write("  2. Jobs are running but not persisted (check worker logs)")
            self.stdout.write("")
            self.stdout.write("To verify scheduler is running:")
            self.stdout.write("  - Check background worker logs on Render")
            self.stdout.write("  - Look for 'Starting scheduler...' message")
            return

        self.stdout.write(self.style.SUCCESS(f"\nFound {jobs.count()} job(s) in database:\n"))

        for job in jobs:
            self.stdout.write("=" * 60)
            self.stdout.write(f"Job ID: {job.id}")
            self.stdout.write(f"Name: {job.name}")
            self.stdout.write(f"Next Run: {job.next_run_time}")
            self.stdout.write("")

        # Also show recent job executions
        executions = DjangoJobExecution.objects.all().order_by('-run_time')[:10]

        if executions.exists():
            self.stdout.write(self.style.SUCCESS(f"\nRecent job executions ({executions.count()}):\n"))
            for execution in executions:
                status = "✓ SUCCESS" if execution.status == "Success" else "✗ FAILED"
                self.stdout.write(f"{execution.run_time} - {execution.job.name} - {status}")
        else:
            self.stdout.write(self.style.WARNING("\nNo job executions yet."))
            self.stdout.write("Jobs will execute at their scheduled times.")
