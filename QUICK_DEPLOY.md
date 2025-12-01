# Quick Deployment Guide for Render

## 🚀 Deploy in 5 Minutes

### Step 1: Push to GitHub
```bash
git add .
git commit -m "feat: APScheduler setup for Render deployment"
git push origin master
```

### Step 2: Deploy on Render

**Option A: Using Blueprint (Automatic)**
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render detects `render.yaml` automatically
5. Review services:
   - ✅ Web Service: `bookflow-api`
   - ✅ Background Worker: `bookflow-scheduler`
   - ✅ PostgreSQL: `bookflow-db`
6. Click **"Apply"**

**Option B: Manual Setup**
1. Create Web Service: `gunicorn bookflow_api.wsgi:application --bind 0.0.0.0:$PORT`
2. Create Background Worker: `python manage.py scheduler`
3. Both use same database and environment variables

### Step 3: Set Environment Variables

Add these to **BOTH** services (Web + Worker):

```
APP_SECRET_KEY=<your_value>
MAIL_SMTP_PASSWORD=<your_value>
DB_NAME=<your_value>
DB_USERNAME=<your_value>
DB_PASSWORD=<your_value>
DB_HOST_NAME=<your_value>
CLOUDINARY_CLOUD_NAME=<your_value>
CLOUDINARY_API_KEY=<your_value>
CLOUDINARY_API_SECRET=<your_value>
GOOGLE_BOOKS_API_KEY=<your_value>
GOOGLE_API_KEY=<your_value>
```

### Step 4: Verify Deployment

**Check Web Service Logs:**
```
INFO ... Background scheduler started successfully for async tasks.
Booting worker with pid: ...
Listening at: http://0.0.0.0:10000
```

**Check Background Worker Logs (IMPORTANT):**
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

**If you see "No Jobs" in the database:**
- This is normal! Jobs appear when the **worker starts**
- Check background worker logs (above)
- If logs show jobs registered, everything is working
- See [SCHEDULER_TROUBLESHOOTING.md](SCHEDULER_TROUBLESHOOTING.md) for details

### Step 5: Verify Jobs Are Registered

In Render Shell (Web Service), run:
```bash
python manage.py list_jobs
```

You should see 2 jobs listed. If not, see troubleshooting guide.

### Step 6: Test

1. Visit your web service URL
2. Test API endpoints
3. Monitor worker logs for job executions

---

## 📋 Scheduled Jobs

Your background worker runs these jobs:

| Job | Schedule | Description |
|-----|----------|-------------|
| `clear_otps` | Daily at 2:00 AM UTC | Clears all OTP records |
| `delete_old_job_executions` | Monday at 12:00 AM UTC | Cleans up old job execution records |

---

## 🔧 Common Commands

**View Web Service Logs:**
```bash
# In Render dashboard, click Web Service → Logs
```

**View Worker Logs:**
```bash
# In Render dashboard, click Background Worker → Logs
```

**Access Shell (Web Service):**
```bash
# In Render dashboard, click Web Service → Shell
python manage.py shell
```

**Create Superuser:**
```bash
# In Render shell
python manage.py createsuperuser
```

---

## ⚠️ Important Notes

1. **Database Connection**: Both services automatically connect to the same PostgreSQL database
2. **Auto-Deploy**: Worker auto-deploys when web service deploys
3. **Health Check**: Web service uses `/admin/` as health check endpoint
4. **Timezone**: All jobs run in UTC (configured in settings.py)
5. **Job Storage**: Jobs are stored in `django_apscheduler_djangojob` table

---

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Worker not starting | Check environment variables are set |
| Jobs not running | Verify worker logs show "Starting scheduler..." |
| Database errors | Ensure both services use same DB credentials |
| Import errors | Check build.sh ran successfully |

---

## 📖 Full Documentation

For detailed information, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Blueprint created or services set up manually
- [ ] Environment variables added to both services
- [ ] Build completed successfully
- [ ] Web service is running
- [ ] Background worker is running
- [ ] Database connected
- [ ] Logs show no errors
- [ ] API endpoints responding
- [ ] Scheduler jobs registered

**You're ready to go! 🎉**
