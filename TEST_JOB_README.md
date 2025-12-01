# Test Scheduler Job - 3:45 PM UTC Daily

## What is this?

I've added a **test job** that runs **daily at 3:45 PM UTC** so you can verify your APScheduler is working correctly.

## What the test job does:

When it runs at 3:45 PM UTC, it will:
1. ✅ Log a success message to the background worker logs
2. ✅ Print a celebration message
3. ✅ **Send an email to kolosafo@gmail.com** 📧
4. ✅ Return "TEST_JOB_COMPLETED"

## How to verify it's working:

### Step 1: Check it's registered

After deploying, check your background worker logs on Render. You should see:

```
==================================================
APScheduler is starting...
==================================================
✓ Added job: 'daily_otp_cleanup' - Runs daily at 2:00 AM UTC
✓ Added job: 'delete_old_job_executions' - Runs every Monday at midnight UTC
✓ Added job: 'test_scheduler_job' - Runs daily at 3:45 PM UTC (FOR TESTING)
==================================================
Total jobs registered: 3
  - Job ID: daily_otp_cleanup, Next run: ...
  - Job ID: delete_old_job_executions, Next run: ...
  - Job ID: test_scheduler_job, Next run: 2025-12-01 15:45:00+00:00
==================================================
```

### Step 2: Wait for 3:45 PM UTC

Convert to your timezone:
- **3:45 PM UTC** = What time in your timezone?
- Use: https://www.worldtimebuddy.com/

### Step 3: Watch for email at 3:45 PM UTC

At exactly 3:45 PM UTC, you'll receive an email at **kolosafo@gmail.com** with:

**Subject:** 🎉 APScheduler Test Job - SUCCESS!

**Email will contain:**
- Execution timestamp
- Confirmation that scheduler is working
- Next steps

### Step 4: Check the logs (optional)

You can also check your background worker logs at 3:45 PM UTC:

```
============================================================
🎉 TEST JOB EXECUTED SUCCESSFULLY!
============================================================
This is a test job running at 3:45 PM UTC
If you see this message, your scheduler is working!
============================================================
✅ Test job email sent successfully to kolosafo@gmail.com
```

## Current time check:

To see what time it is in UTC right now:
```bash
python manage.py shell -c "from django.utils import timezone; print(f'Current UTC time: {timezone.now()}')"
```

## Alternative: Run test job manually

Don't want to wait? Run it immediately:

```bash
# In Render Shell (Web Service)
python manage.py shell
```

```python
from account.tasks import test_scheduler_job
test_scheduler_job()
```

You should see the success message immediately.

## Check job execution history

After the job runs at 3:45 PM UTC:

```bash
python manage.py list_jobs
```

This will show recent executions including the test job.

Or in Django shell:
```python
from django_apscheduler.models import DjangoJobExecution

# Get recent test job executions
executions = DjangoJobExecution.objects.filter(
    job__id='test_scheduler_job'
).order_by('-run_time')[:5]

for execution in executions:
    print(f"{execution.run_time}: {execution.status}")
```

## When to remove this test job

Once you've confirmed the scheduler is working (you see the test job execute successfully), you can remove it:

1. Open `account/management/commands/scheduler.py`
2. Remove or comment out the test job section:
```python
# TEST JOB - Runs daily at 3:45 PM UTC for testing
scheduler.add_job(
  test_scheduler_job,
  trigger=CronTrigger(hour="15", minute="45"),
  id="test_scheduler_job",
  max_instances=1,
  replace_existing=True,
)
```

3. Redeploy to Render

## Files modified:

- [account/tasks.py](account/tasks.py) - Added `test_scheduler_job()` function
- [account/management/commands/scheduler.py](account/management/commands/scheduler.py) - Added test job to scheduler

## Summary

✅ **Test job added**: Runs daily at 3:45 PM UTC
✅ **Easy to verify**: Check logs at 3:45 PM UTC
✅ **Easy to remove**: Delete/comment out when done testing
✅ **Proves scheduler works**: If this runs, all your jobs will work

Good luck with your test! 🚀
