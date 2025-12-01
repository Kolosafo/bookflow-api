#!/usr/bin/env bash
# APScheduler startup script for Render background worker
# This script starts the Django APScheduler with proper error handling

set -o errexit  # Exit on error
set -o pipefail # Exit on pipe failure
set -o nounset  # Exit on undefined variable

echo "=================================================="
echo "BookFlow API - APScheduler Worker"
echo "=================================================="
echo "Starting at: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "ERROR: manage.py not found. Are we in the correct directory?"
    exit 1
fi

# Check if Django is installed
if ! python -c "import django" 2>/dev/null; then
    echo "ERROR: Django is not installed"
    exit 1
fi

# Check if APScheduler is installed
if ! python -c "import apscheduler" 2>/dev/null; then
    echo "ERROR: APScheduler is not installed"
    exit 1
fi

# Check database connection
echo "Checking database connection..."
if ! python manage.py check --database default 2>/dev/null; then
    echo "WARNING: Database check failed, but continuing..."
fi

# Run migrations (ensure tables exist)
echo "Running migrations..."
python manage.py migrate --noinput || {
    echo "ERROR: Failed to run migrations"
    exit 1
}

echo ""
echo "✓ Pre-flight checks passed"
echo ""
echo "=================================================="
echo "Starting APScheduler..."
echo "=================================================="
echo ""

# Start the scheduler
# The scheduler command will run indefinitely until stopped
exec python manage.py scheduler
