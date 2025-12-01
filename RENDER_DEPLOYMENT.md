# BookFlow API - Render Deployment Guide

This guide explains how to deploy the BookFlow API with APScheduler on Render.

## Architecture Overview

Your application uses **two separate processes** on Render:

1. **Web Service** - Main Django application that serves API requests
2. **Background Worker** - APScheduler process that runs recurring cron jobs

### Why Two Processes?

- **Web Service**: Runs your Django API using Gunicorn (handles HTTP requests)
- **Background Worker**: Runs the APScheduler with `BlockingScheduler` for recurring tasks like:
  - Clearing OTPs daily at 2:00 AM
  - Deleting old job executions weekly on Mondays at midnight

**Important**: Both services share the same PostgreSQL database, so scheduled jobs can access all your Django models.

## Scheduler Types Explained

Your app uses **two different schedulers**:

### 1. BackgroundScheduler (Web Service)
- **File**: [books/scheduler.py](books/scheduler.py)
- **Purpose**: Handles one-off async tasks triggered by user actions
- **Examples**:
  - Book summary generation (runs 2 seconds after user request)
  - Free trial assignment (runs 5 seconds after trigger)
- **Started**: Automatically in [books/apps.py](books/apps.py) when Django starts
- **Runs on**: Web Service only

### 2. BlockingScheduler (Background Worker)
- **File**: [account/management/commands/scheduler.py](account/management/commands/scheduler.py)
- **Purpose**: Handles recurring cron jobs (daily, weekly tasks)
- **Examples**:
  - Daily OTP cleanup at 2:00 AM
  - Weekly old job execution cleanup
- **Started**: Via management command `python manage.py scheduler`
- **Runs on**: Background Worker only

## Deployment Methods

You have **two options** for deploying to Render:

---

## Option 1: Using render.yaml (Recommended)

This is the easiest method - Render will automatically set up both services.

### Steps:

1. **Push your code to GitHub** (including the `render.yaml` file)

2. **Go to Render Dashboard**: https://dashboard.render.com

3. **Click "New +" → "Blueprint"**

4. **Connect your GitHub repository**

5. **Render will automatically detect `render.yaml` and create**:
   - Web Service: `bookflow-api`
   - Background Worker: `bookflow-scheduler`
   - PostgreSQL Database: `bookflow-db`

6. **Set Environment Variables**:
   - Click on each service → "Environment"
   - Add all required environment variables:
     ```
     APP_SECRET_KEY=your_secret_key
     MAIL_SMTP_PASSWORD=your_smtp_password
     DB_NAME=your_db_name
     DB_USERNAME=your_db_username
     DB_PASSWORD=your_db_password
     DB_HOST_NAME=your_db_hostname
     CLOUDINARY_CLOUD_NAME=your_cloudinary_name
     CLOUDINARY_API_KEY=your_cloudinary_key
     CLOUDINARY_API_SECRET=your_cloudinary_secret
     GOOGLE_BOOKS_API_KEY=your_google_books_key
     GOOGLE_API_KEY=your_google_api_key
     ```

7. **Deploy**: Render will build and deploy both services automatically

---

## Option 2: Manual Dashboard Setup

If you prefer to set up services manually through the Render dashboard:

### Step 1: Create the Web Service

1. Go to Render Dashboard → "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `bookflow-api`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `master`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn bookflow_api.wsgi:application`
4. Add all environment variables (see list above)
5. Click "Create Web Service"

### Step 2: Create the Background Worker

1. Go to Render Dashboard → "New +" → "Background Worker"
2. Connect the **same GitHub repository**
3. Configure:
   - **Name**: `bookflow-scheduler`
   - **Environment**: `Python 3`
   - **Region**: **Same as web service**
   - **Branch**: `master`
   - **Build Command**: `./build.sh`
   - **Start Command**: `python manage.py scheduler`
4. Add all the **same environment variables** as the web service
5. Click "Create Background Worker"

### Step 3: Connect to Database

Both services need to connect to the same PostgreSQL database:

1. If you don't have a database, create one:
   - "New +" → "PostgreSQL"
   - Name it `bookflow-db`

2. Add database environment variables to **both services**:
   - Get connection details from your database settings
   - Add `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`, `DB_HOST_NAME`

---

## Verifying Your Deployment

### Check Web Service

1. Go to your web service dashboard
2. Check **Logs** tab - you should see:
   ```
   INFO ... Background scheduler started successfully for async tasks.
   Booting worker with pid: ...
   Listening at: http://0.0.0.0:10000
   ```

### Check Background Worker

1. Go to your background worker dashboard
2. Check **Logs** tab - you should see:
   ```
   INFO ... Added job 'delete_otps'.
   INFO ... Added daily job: 'delete_old_job_executions'.
   INFO ... Starting scheduler...
   ```

### Test Scheduled Jobs

To verify the scheduler is working:

1. **Check database** - Look for records in `django_apscheduler_djangojob` table
2. **Monitor logs** - Wait for scheduled times and check worker logs
3. **Manually trigger** - Use Django admin or shell to verify job execution

---

## Troubleshooting

### Worker Not Starting

**Problem**: Background worker shows errors or doesn't start

**Solutions**:
- Check that `build.sh` is executable (should be)
- Verify all environment variables are set
- Check worker logs for specific errors
- Ensure database migrations have run

### Scheduler Running Twice

**Problem**: Jobs are executed multiple times

**Solutions**:
- Make sure you only have ONE background worker instance
- Check that `replace_existing=True` in job definitions
- Verify job IDs are unique

### Database Connection Errors

**Problem**: Worker can't connect to database

**Solutions**:
- Verify database environment variables match web service
- Check that both services are in the same region
- Ensure database allows connections from Render

### Jobs Not Running at Scheduled Time

**Problem**: Cron jobs don't execute when expected

**Solutions**:
- Check `TIME_ZONE` setting in [settings.py](bookflow_api/settings.py) (currently UTC)
- Verify `CronTrigger` times in [scheduler.py](account/management/commands/scheduler.py)
- Check worker logs for scheduler errors
- Ensure worker service is running (not sleeping)

### Memory Issues

**Problem**: Worker crashes with memory errors

**Solutions**:
- Upgrade to a paid plan with more memory
- Optimize job functions to use less memory
- Add error handling to prevent memory leaks

---

## Important Files

| File | Purpose |
|------|---------|
| [render.yaml](render.yaml) | Render infrastructure configuration |
| [build.sh](build.sh) | Build script for both services |
| [requirements.txt](requirements.txt) | Python dependencies (includes gunicorn) |
| [books/scheduler.py](books/scheduler.py) | BackgroundScheduler for async tasks |
| [books/apps.py](books/apps.py) | Starts BackgroundScheduler on web service |
| [books/tasks.py](books/tasks.py) | Task functions for async jobs |
| [account/management/commands/scheduler.py](account/management/commands/scheduler.py) | BlockingScheduler for cron jobs |
| [account/tasks.py](account/tasks.py) | Task function for clearing OTPs |

---

## Production Deployment

Your application is configured for production deployment with:
- **Web Service**: Runs your Django API with Gunicorn (Starter plan or higher)
- **Background Worker**: Runs APScheduler 24/7 for cron jobs (Starter plan or higher)
- **PostgreSQL Database**: Persistent storage for all data (Starter plan or higher)

### Plan Recommendations

- **Starter Plan**: Good for getting started, moderate traffic
- **Standard Plan**: Better performance, more memory, recommended for production
- **Pro Plan**: High traffic, enterprise features

You can adjust the `plan:` values in [render.yaml](render.yaml) to match your needs.

---

## Environment Variables Checklist

Make sure these are set on **BOTH** services:

- [ ] `APP_SECRET_KEY`
- [ ] `MAIL_SMTP_PASSWORD`
- [ ] `DB_NAME`
- [ ] `DB_USERNAME`
- [ ] `DB_PASSWORD`
- [ ] `DB_HOST_NAME`
- [ ] `CLOUDINARY_CLOUD_NAME`
- [ ] `CLOUDINARY_API_KEY`
- [ ] `CLOUDINARY_API_SECRET`
- [ ] `GOOGLE_BOOKS_API_KEY`
- [ ] `GOOGLE_API_KEY`

---

## Next Steps After Deployment

1. **Run migrations**: Should happen automatically via `build.sh`
2. **Create superuser**:
   ```bash
   # In Render shell for web service
   python manage.py createsuperuser
   ```
3. **Test API endpoints**: Visit your web service URL
4. **Monitor scheduler**: Check background worker logs
5. **Set up monitoring**: Consider using Render's metrics or external services

---

## Getting Help

If you encounter issues:

1. Check Render logs (Web Service and Background Worker)
2. Review this documentation
3. Check [Django APScheduler docs](https://github.com/jcass77/django-apscheduler)
4. Contact Render support for infrastructure issues

---

## Summary

✅ **Web Service**: Handles API requests + one-off async tasks (BackgroundScheduler)
✅ **Background Worker**: Runs recurring cron jobs (BlockingScheduler)
✅ **Both share**: Same database, same codebase, same environment variables
✅ **Different commands**: Web uses `gunicorn`, Worker uses `python manage.py scheduler`

Your scheduler setup is now production-ready for Render! 🚀
