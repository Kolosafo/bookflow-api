from .models import OTPService
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def clear_otps():
    get_all_otps = OTPService.objects.all()
    for otp in get_all_otps:
        otp.delete()

    return "OKAY"


def test_scheduler_job():
    """
    Test job to verify scheduler is working.
    This job runs at 3:45 PM UTC daily for testing purposes.
    Sends an email notification and logs the execution.
    """
    logger.info("=" * 60)
    logger.info("🎉 TEST JOB EXECUTED SUCCESSFULLY!")
    logger.info("=" * 60)
    logger.info("This is a test job running at 3:45 PM UTC")
    logger.info("If you see this message, your scheduler is working!")
    logger.info("=" * 60)

    print("🎉 TEST JOB EXECUTED SUCCESSFULLY! Check the logs!")

    # Send email notification
    try:
        current_time = timezone.now()
        subject = "🎉 APScheduler Test Job - SUCCESS!"
        message = f"""
Hello!

Your APScheduler test job executed successfully!

Execution Time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}
Scheduled Time: 3:45 PM UTC (Daily)

This confirms that:
✅ Your background worker is running
✅ APScheduler is working correctly
✅ Jobs are executing at their scheduled times
✅ Email notifications are working

You can now trust that your other scheduled jobs (OTP cleanup, job execution cleanup)
will run at their scheduled times.

To remove this test job, see TEST_JOB_README.md in your project.

---
BookFlow API - Automated Scheduler
"""

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['kolosafo@gmail.com'],
            fail_silently=False,
        )
        logger.info("✅ Test job email sent successfully to kolosafo@gmail.com")

    except Exception as e:
        logger.error(f"❌ Failed to send test job email: {e}")
        # Don't fail the job if email fails
        pass

    return "TEST_JOB_COMPLETED"