# APScheduler Troubleshooting Guide

## "No Jobs" Issue - What's Happening?

When you see **"No jobs"** in the database/admin panel, it usually means one of these things:

### 1. Background Worker Isn't Running
The scheduler worker process needs to be running for jobs to be registered.

**Check this:**
1. Go to Render Dashboard
2. Click on `bookflow-scheduler` (Background Worker)
3. Check **Status** - should say "Running"
4. Check **Logs** - you should see:

```
==================================================
APScheduler is starting...
==================================================
✓ Added job: 'daily_otp_cleanup' - Runs daily at 2:00 AM UTC
✓ Added job: 'delete_old_job_executions' - Runs every Monday at midnight UTC
==================================================
Total jobs registered: 2
  - Job ID: daily_otp_cleanup, Next run: 2025-12-02 02:00:00+00:00
  - Job ID: delete_old_job_executions, Next run: 2025-12-02 00:00:00+00:00
==================================================
Starting scheduler... Press Ctrl+C to exit
```

**If you DON'T see this:**
- Worker might have crashed during startup
- Check for error messages in logs
- Verify all environment variables are set
- Check database connection is working

---

### 2. Jobs Are Running But Not in Database Yet
Jobs are registered when the scheduler **starts**, not before. If the worker just started, wait 10-30 seconds.

**To verify:**
Run this command in Render Shell (Web Service):
```bash
python manage.py list_jobs
```

This will show all jobs in the database.

---

### 3. Database Migrations Missing
The `django_apscheduler` app needs database tables to store jobs.

**Check this:**
1. Go to Render Shell (Web Service)
2. Run:
```bash
python manage.py showmigrations django_apscheduler
```

You should see:
```
django_apscheduler
 [X] 0001_initial
 [X] 0002_auto_...
 [X] ... (all should have [X])
```

**If migrations are missing:**
```bash
python manage.py migrate django_apscheduler
```

---

## How to Check if Scheduler is Working

### Method 1: Check Worker Logs (Easiest)

1. Go to Render Dashboard
2. Click `bookflow-scheduler` (Background Worker)
3. Click **Logs** tab
4. Look for the startup messages shown above

**What you should see:**
- ✓ Two jobs registered
- ✓ Next run times listed
- ✓ "Starting scheduler..." message
- ✓ No error messages

---

### Method 2: Query Database Directly

In Render Shell (Web Service):
```bash
python manage.py shell
```

Then run:
```python
from django_apscheduler.models import DjangoJob

# List all jobs
jobs = DjangoJob.objects.all()
print(f"Total jobs: {jobs.count()}")

for job in jobs:
    print(f"- {job.id}: {job.name}, Next run: {job.next_run_time}")
```

**Expected output:**
```
Total jobs: 2
- daily_otp_cleanup: account.tasks.clear_otps, Next run: 2025-12-02 02:00:00+00:00
- delete_old_job_executions: ..., Next run: 2025-12-02 00:00:00+00:00
```

---

### Method 3: Use the Management Command

Run this in Render Shell:
```bash
python manage.py list_jobs
```

This shows all jobs and recent executions.

---

## Common Issues and Solutions

### Issue: Worker Shows "Running" But No Logs

**Problem:** Worker process is stuck or not outputting logs

**Solution:**
1. Manually restart the worker:
   - Render Dashboard → `bookflow-scheduler` → "Manual Deploy" → "Deploy"
2. Check if build.sh ran successfully
3. Verify Python version matches (3.9.18)

---

### Issue: Jobs in Database But Never Execute

**Problem:** Scheduler is running but jobs don't run at scheduled time

**Solutions:**
1. **Check timezone:** Jobs run in UTC (configured in settings.py)
   - 2:00 AM UTC might be different time in your timezone
   - Use https://www.worldtimebuddy.com/ to convert

2. **Check cron trigger syntax:**
   - Current: `hour="02"` means 2 AM
   - Current: `day_of_week="mon"` means Monday
   - These are correct

3. **Wait for scheduled time:**
   - Jobs won't run immediately
   - They run at the scheduled time
   - To test immediately, see "Force Run a Job" below

---

### Issue: Worker Crashes on Startup

**Problem:** Worker starts then immediately stops

**Solutions:**
1. Check logs for error messages
2. Common causes:
   - Missing environment variables
   - Database connection failed
   - Import errors (missing dependencies)

3. Verify build succeeded:
   - Check build logs for errors
   - Ensure `pip install -r requirements.txt` completed
   - Check that migrations ran

---

## Force Run a Job (For Testing)

To test if a job works **right now** instead of waiting for scheduled time:

### Method 1: Create a Test Command

Create `account/management/commands/test_jobs.py`:
```python
from django.core.management.base import BaseCommand
from account.tasks import clear_otps

class Command(BaseCommand):
    help = "Test job execution"

    def handle(self, *args, **options):
        self.stdout.write("Running clear_otps job...")
        result = clear_otps()
        self.stdout.write(self.style.SUCCESS(f"Result: {result}"))
```

Then run:
```bash
python manage.py test_jobs
```

### Method 2: Run in Shell

```bash
python manage.py shell
```

```python
from account.tasks import clear_otps
result = clear_otps()
print(f"Result: {result}")
```

---

## Expected Behavior

### On Worker Startup
1. ✓ Scheduler initializes
2. ✓ Jobs are registered to database
3. ✓ Jobs show in `django_apscheduler_djangojob` table
4. ✓ Logs show job details
5. ✓ Worker stays running (doesn't exit)

### During Operation
1. ✓ Worker logs show "Starting scheduler..."
2. ✓ Worker doesn't crash or restart
3. ✓ At scheduled time, job executes
4. ✓ Execution is logged to `django_apscheduler_djangojobexecution` table

### After Job Runs
1. ✓ Check job execution table for results
2. ✓ Check logs for job output
3. ✓ Next run time is updated

---

## Verification Checklist

Run through this checklist:

- [ ] Background worker is **Running** on Render
- [ ] Worker logs show "APScheduler is starting..."
- [ ] Worker logs show "Total jobs registered: 2"
- [ ] Worker logs show next run times for both jobs
- [ ] Worker logs show "Starting scheduler..."
- [ ] No error messages in worker logs
- [ ] Database has `django_apscheduler_djangojob` table
- [ ] Running `python manage.py list_jobs` shows 2 jobs
- [ ] Web service is also running (for BackgroundScheduler)

---

## Quick Diagnosis Commands

Run these in Render Shell (Web Service):

```bash
# 1. Check if migrations are applied
python manage.py showmigrations django_apscheduler

# 2. List all scheduled jobs
python manage.py list_jobs

# 3. Check database tables exist
python manage.py dbshell
\dt django_apscheduler*
\q

# 4. Test a job manually
python manage.py shell -c "from account.tasks import clear_otps; print(clear_otps())"
```

---

## Still Having Issues?

If jobs still don't show up after checking everything above:

1. **Share worker logs:**
   - Copy the full log output from `bookflow-scheduler`
   - Look for any ERROR or WARNING messages

2. **Check these files are deployed:**
   - [ ] `account/management/commands/scheduler.py`
   - [ ] `account/tasks.py`
   - [ ] `books/scheduler.py`
   - [ ] `books/apps.py`

3. **Verify database connection:**
   - Both web service and worker should connect to same database
   - Check environment variables match on both services

4. **Check Python version:**
   - Should be 3.9.18 (configured in render.yaml)
   - Render logs show Python version during build

---

## What "No Jobs" Actually Means

The "jobs" you're looking for are stored in this database table:
```
django_apscheduler_djangojob
```

This table is populated when:
1. ✅ The scheduler worker starts
2. ✅ Calls `scheduler.add_job(...)`
3. ✅ With a `DjangoJobStore` configured

If this table is empty, it means step 1-3 haven't completed yet.

**This is normal if:**
- Worker just started (wait 30 seconds)
- Worker hasn't started yet
- Worker crashed during startup

**This is a problem if:**
- Worker shows "Running" for 5+ minutes
- Worker logs don't show job registration messages
- Worker logs show errors

---

## Summary

✅ **Jobs are registered when the worker starts**
✅ **Check worker logs first** - they tell you everything
✅ **Use `python manage.py list_jobs`** to verify database
✅ **Jobs won't run until their scheduled time**
✅ **Both services need to be running** (web + worker)

Your scheduler is working if:
- Worker logs show "Starting scheduler..."
- No errors in logs
- Jobs show in database (`python manage.py list_jobs`)
