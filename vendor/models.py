from django.template.defaultfilters import default
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
import secrets
from django.utils import timezone
from account.models import User
# Create your models here.


vendor_account_status = (
    ("not activated", "not activated"),
    ("activated", "activated"),
    ("suspended", "suspended"),
)


class BookInsight(models.Model):
    """
    Model for saving AI-generated book insights and actions.
    """

    book_title = models.CharField(max_length=255)
    author_title = models.CharField(max_length=255, blank=True, null=True)
    insights = models.JSONField(
        help_text="Array of 2-3 key insights"
    )
    actionable_steps = models.JSONField(
        help_text="Array of 1-2 actionable steps"
    )
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.book_title





class VendorPlan(models.TextChoices):
    FREE = "free", "Free"
    PRO = "pro", "Pro"
    ENTERPRISE = "enterprise", "Enterprise"


class Vendor(models.Model):
    """
    Vendors who access BookInsights via API key
    """

    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=150)

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    plan = models.CharField(
        max_length=20,
        choices=VendorPlan.choices,
        default=VendorPlan.FREE
    )

    daily_usage_limit = models.PositiveIntegerField(default=100)
    daily_usage_count = models.PositiveIntegerField(default=0)
    dropdown_preview_text = models.TextField(default="See how this book aligns with your goals and what it offers you.")
    is_widget_open_by_default = models.BooleanField(default=False)
    last_usage_reset = models.DateField(default=timezone.now)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.plan})"

    def reset_daily_usage_if_needed(self):
        today = timezone.now().date()
        if self.last_usage_reset != today:
            self.daily_usage_count = 0
            self.last_usage_reset = today
            self.save(update_fields=["daily_usage_count", "last_usage_reset"])

    def can_use_api(self):
        self.reset_daily_usage_if_needed()
        return self.daily_usage_count < self.daily_usage_limit

    def increment_usage(self, amount=1):
        self.reset_daily_usage_if_needed()
        self.daily_usage_count += amount
        self.save(update_fields=["daily_usage_count"])


class VendorAccount(models.Model):
    """
    Vendor account model for authentication and management
    """
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    website_url = models.URLField(max_length=500, blank=True, null=True)
    company_name = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20,
        choices=vendor_account_status,
        default="not activated"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Link to the Vendor instance (one-to-one relationship)
    vendor = models.OneToOneField(
        Vendor,
        on_delete=models.CASCADE,
        related_name='account',
        null=True,
        blank=True
    )
    
    # Link to User model for JWT authentication
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='vendor_account',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.email} - {self.company_name}"

    def save(self, *args, **kwargs):
        # Hash password if it's not already hashed
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        """
        Check if the provided password matches the stored hashed password
        """
        return check_password(raw_password, self.password)


class BookROI(models.Model):
    """
    Model for saving Book ROI (Return on Investment) analysis
    Helps readers gauge whether a book would help them achieve their goal
    """
    book_title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    reader_goal = models.TextField()
    reader_challenge = models.TextField()
    available_time = models.CharField(max_length=100)

    roi_score = models.IntegerField(help_text="ROI Score from 0-100")
    match_reasoning = models.TextField()
    relevant_takeaways = models.JSONField(help_text="Array of relevant takeaways")
    time_analysis = models.TextField()
    estimated_reading_hours = models.FloatField()
    recommendation = models.CharField(
        max_length=50,
        choices=[
            ("highly_recommended", "Highly Recommended"),
            ("recommended", "Recommended"),
            ("moderately_recommended", "Moderately Recommended"),
            ("not_recommended", "Not Recommended")
        ]
    )

    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book_title} - ROI Score: {self.roi_score}"


class WidgetTestUsage(models.Model):
    """
    Model for tracking global daily usage of the widget test endpoint.
    Limits total analysis to 120 per day.
    """
    date = models.DateField(unique=True, default=timezone.now)
    total_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.date}: {self.total_count} analyses"

    @classmethod
    def get_count_for_today(cls):
        today = timezone.now().date()
        usage, created = cls.objects.get_or_create(date=today)
        return usage.total_count

    @classmethod
    def increment_count(cls):
        today = timezone.now().date()
        usage, created = cls.objects.get_or_create(date=today)
        usage.total_count += 1
        usage.save()


class VendorTestKey(models.Model):
    """
    Model for individual vendor test API keys.
    Each key has a maximum lifetime usage of 5 analyses.
    """
    key = models.CharField(max_length=255, unique=True, default=secrets.token_urlsafe)
    usage_count = models.PositiveIntegerField(default=0)
    is_assigned = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Assigned" if self.is_assigned else "Unassigned"
        return f"{self.key} ({self.usage_count}/5) - {status}"

    def can_be_used(self):
        return self.is_active and self.usage_count < 5

    def increment_usage(self):
        self.usage_count += 1
        self.save()