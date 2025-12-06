from .models import OTPService, User, UserSubscriptionUsage
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


def update_all_user_subscription_usage():
    """
    Updates all users' subscription usage values to new limits:
    - summaries: 10
    - notes: 25
    - reminders: 10
    - smart_search: 10

    This function will:
    1. Loop through all User objects
    2. Get or create UserSubscriptionUsage for each user
    3. Update the usage values

    Returns:
        dict: Summary of the operation (total users, updated count, created count, errors)
    """
    logger.info("=" * 60)
    logger.info("Starting update_all_user_subscription_usage task")
    logger.info("=" * 60)

    total_users = 0
    updated_count = 0
    created_count = 0
    errors = []

    try:
        all_users = User.objects.all()
        total_users = all_users.count()

        logger.info(f"Found {total_users} users to process")

        for user in all_users:
            try:
                # Get or create UserSubscriptionUsage for this user
                usage, created = UserSubscriptionUsage.objects.get_or_create(
                    user=user,
                    defaults={
                        'summaries': 10,
                        'notes': 25,
                        'reminders': 10,
                        'smart_search': 10,
                    }
                )

                if created:
                    created_count += 1
                    logger.info(f"✓ Created new subscription usage for {user.email}")
                else:
                    # Update existing record
                    usage.summaries = 10
                    usage.notes = 25
                    usage.reminders = 10
                    usage.smart_search = 10
                    usage.save()
                    updated_count += 1
                    logger.info(f"✓ Updated subscription usage for {user.email}")

            except Exception as e:
                error_msg = f"Error processing user {user.email}: {str(e)}"
                logger.error(f"✗ {error_msg}")
                errors.append(error_msg)

        # Summary
        logger.info("=" * 60)
        logger.info("Update completed!")
        logger.info(f"Total users: {total_users}")
        logger.info(f"Created: {created_count}")
        logger.info(f"Updated: {updated_count}")
        logger.info(f"Errors: {len(errors)}")
        logger.info("=" * 60)

        result = {
            'status': 'SUCCESS',
            'total_users': total_users,
            'created_count': created_count,
            'updated_count': updated_count,
            'errors_count': len(errors),
            'errors': errors
        }

        return result

    except Exception as e:
        error_msg = f"Fatal error in update_all_user_subscription_usage: {str(e)}"
        logger.error(error_msg)
        return {
            'status': 'FAILED',
            'error': error_msg
        }