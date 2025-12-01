# APScheduler Startup Script Documentation

## Overview

The `scheduler.sh` script is a robust startup wrapper for the APScheduler background worker on Render. It performs pre-flight checks and starts the scheduler with proper error handling.

## File: scheduler.sh

**Location:** `/scheduler.sh` (project root)

**Purpose:** Start the APScheduler worker with health checks and error handling

---

## What the Script Does

### 1. Pre-flight Checks

Before starting the scheduler, it verifies:

- ✅ **manage.py exists** - Ensures we're in the correct directory
- ✅ **Django is installed** - Verifies Django package is available
- ✅ **APScheduler is installed** - Verifies APScheduler package is available
- ✅ **Database connection** - Checks if database is reachable
- ✅ **Migrations are applied** - Runs `python manage.py migrate`

### 2. Error Handling

The script uses:
- `set -o errexit` - Exit immediately if any command fails
- `set -o pipefail` - Catch errors in piped commands
- `set -o nounset` - Exit if undefined variables are used

### 3. Start Scheduler

After all checks pass:
- Uses `exec python manage.py scheduler` to replace the shell process
- Runs the APScheduler indefinitely until stopped
- All scheduler logs go directly to stdout/stderr (visible in Render logs)

---

## Usage

### On Render (Automatic)

The script is automatically used by the background worker service via `render.yaml`:

```yaml
startCommand: "./scheduler.sh"
```

No manual intervention needed - Render runs this on worker startup.

### Manual Execution (Testing)

**On Render Shell:**
```bash
./scheduler.sh
```

**Locally:**
```bash
chmod +x scheduler.sh
./scheduler.sh
```

**Note:** This will block the terminal and run continuously. Press `Ctrl+C` to stop.

---

## Expected Output

When the script runs successfully, you'll see:

```
==================================================
BookFlow API - APScheduler Worker
==================================================
Starting at: 2025-12-01 14:30:00 UTC

Checking database connection...
Running migrations...
Operations to perform:
  Apply all migrations: ...
Running migrations:
  No migrations to apply.

✓ Pre-flight checks passed

==================================================
Starting APScheduler...
==================================================

INFO ... ==================================================
INFO ... APScheduler is starting...
INFO ... ==================================================
INFO ... ✓ Added job: 'daily_otp_cleanup' - Runs daily at 2:00 AM UTC
INFO ... ✓ Added job: 'delete_old_job_executions' - Runs every Monday at midnight UTC
INFO ... ✓ Added job: 'test_scheduler_job' - Runs daily at 3:45 PM UTC (FOR TESTING)
INFO ... ==================================================
INFO ... Total jobs registered: 3
INFO ...   - Job ID: daily_otp_cleanup, Next run: 2025-12-02 02:00:00+00:00
INFO ...   - Job ID: delete_old_job_executions, Next run: 2025-12-02 00:00:00+00:00
INFO ...   - Job ID: test_scheduler_job, Next run: 2025-12-01 15:45:00+00:00
INFO ... ==================================================
INFO ... Starting scheduler... Press Ctrl+C to exit
```

---

## Error Messages

### "manage.py not found"
```
ERROR: manage.py not found. Are we in the correct directory?
```
**Cause:** Script is not running from project root
**Fix:** Ensure script is executed from `/Users/daudakolo/Documents/bookflow/bookflow_api/`

### "Django is not installed"
```
ERROR: Django is not installed
```
**Cause:** Django package missing
**Fix:** Run `pip install -r requirements.txt`

### "APScheduler is not installed"
```
ERROR: APScheduler is not installed
```
**Cause:** APScheduler package missing
**Fix:** Run `pip install -r requirements.txt`

### "Failed to run migrations"
```
ERROR: Failed to run migrations
```
**Cause:** Database connection issue or migration error
**Fix:** Check database credentials and connection

---

## Comparison: Direct vs Script

### Direct Command (Old Way)
```yaml
startCommand: "python manage.py scheduler"
```
- ❌ No pre-flight checks
- ❌ Silent failures possible
- ❌ No migration check
- ✅ Simple and direct

### Using scheduler.sh (New Way)
```yaml
startCommand: "./scheduler.sh"
```
- ✅ Pre-flight checks ensure environment is ready
- ✅ Clear error messages
- ✅ Automatic migration runner
- ✅ Better debugging with startup logs
- ❌ Slightly more complex

**Recommendation:** Use `scheduler.sh` for production - the pre-flight checks catch issues early.

---

## Customization

You can modify `scheduler.sh` to add:

### Additional Health Checks

```bash
# Check if a specific table exists
echo "Checking if OTPService table exists..."
python manage.py shell -c "from account.models import OTPService; print('✓ OTPService table exists')"
```

### Email Notification on Startup

```bash
# Send email when scheduler starts
python manage.py shell -c "
from django.core.mail import send_mail
from django.conf import settings
send_mail(
    'Scheduler Started',
    'APScheduler worker started at $(date)',
    settings.EMAIL_HOST_USER,
    ['kolosafo@gmail.com']
)
"
```

### Delay Before Starting

```bash
# Wait 10 seconds before starting (useful if database is slow to start)
echo "Waiting 10 seconds for database to be fully ready..."
sleep 10
```

---

## Troubleshooting

### Script exits immediately

**Check:**
1. Is the script executable? `chmod +x scheduler.sh`
2. Are there syntax errors? Run `bash -n scheduler.sh`
3. Check Render logs for error messages

### Database connection fails

**Check:**
1. Environment variables are set correctly
2. Database service is running
3. Network connectivity between worker and database

### Migrations fail

**Check:**
1. Database migrations are compatible
2. Database user has correct permissions
3. Try running `python manage.py migrate` manually in shell

---

## Integration with Render

### render.yaml Configuration

```yaml
- type: worker
  name: bookflow-scheduler
  startCommand: "./scheduler.sh"
  buildCommand: "./build.sh"
```

### Build Process

1. **Build stage:** `build.sh` runs (installs deps, runs migrations, collects static)
2. **Start stage:** `scheduler.sh` runs (health checks, starts scheduler)

**Note:** Migrations run in **both** stages for redundancy. The second run is fast (no-op if already applied).

---

## Files Modified

| File | Change |
|------|--------|
| [scheduler.sh](scheduler.sh) | Created - APScheduler startup script |
| [render.yaml](render.yaml#L50) | Updated startCommand to use `./scheduler.sh` |
| [SCHEDULER_SCRIPT.md](SCHEDULER_SCRIPT.md) | Created - This documentation |

---

## Summary

✅ **scheduler.sh provides:**
- Pre-flight health checks
- Automatic migration runner
- Clear error messages
- Better debugging with startup logs
- Robust error handling

✅ **Used automatically on Render** via `render.yaml`

✅ **Can be run manually** for testing: `./scheduler.sh`

✅ **Customizable** - add your own checks or notifications

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Render will use new `./scheduler.sh` start command
3. ✅ Check worker logs for new startup messages
4. ✅ Verify scheduler starts successfully

**The script is already configured in render.yaml - no manual changes needed!**
