from django.db import models
from django.contrib.auth.models import  AbstractUser, PermissionsMixin
from .utils import generate_id
from .managers import UserManager
import markdown

# Create your models here.


account_status = (
    ("not activated", "not activated"),
    ("activated", "activated"),
    ("suspended", "suspended"),
)

subscription_choices = (
    ("free", "free"),
    ("basic", "basic"),
    ("premium", "premium"),
    ("scholar", "scholar"),
)

user_types = (
    ("vendor", "vendor"),
    ("user", "user"),
)


class User(AbstractUser, PermissionsMixin):
    id = models.CharField(primary_key=True, default=generate_id(), editable=False, blank=True, max_length=100)
    email = models.EmailField(max_length=255,blank=True, null = True, unique=True)
    interests = models.JSONField(default=list)
    deviceId = models.CharField(max_length=255,blank=True, null = True, unique=True)
    date_joined = models.DateTimeField(auto_now_add = True, blank=True)
    subscription= models.CharField(max_length=100, choices=subscription_choices, default="free")
    timezone= models.IntegerField(default=1)
    notification_token= models.CharField(max_length=100, null=True, blank=True)
    date_subscribed = models.DateField(blank=True, null=True)
    date_subscription_ends = models.DateField(blank=True, null=True)
    free_trail = models.BooleanField(default=False)
    free_trail_end_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=account_status, blank=False, default="not activated")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    type = models.CharField(max_length=100, choices=user_types, default="user")
    
    # THIS IS THE KEY CHANGE - Use email as the login field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    
    def __str__(self):
        return f"{self.email}"


otp_service_type = [
    ('email_verification', 'email_verification'),
    ('password_reset', 'password_reset'),
]


class UserSubscriptionUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_subscription_usage')
    summaries =  models.IntegerField(default=1)
    notes = models.IntegerField(default=3)
    reminders = models.IntegerField(default=2)
    smart_search = models.IntegerField(default=3)

    def __str__(self):
        return self.user.email

class OTPService(models.Model):
    type =  models.CharField(max_length=100, choices=otp_service_type)
    email = models.CharField(max_length=255)
    otp = models.CharField(max_length=4)

    def __str__(self):
        return self.email


class PaystackResponse(models.Model):
    data = models.JSONField(null=True, blank=True)
    
    

class SubscribeInApp(models.Model):
    id = models.CharField(primary_key=True, default=generate_id(), editable=False, blank=True, max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_in_app_subscription')
    productId = models.CharField(max_length=150, blank=True, null=True)
    amount = models.FloatField(default=0)
    transactionRef = models.CharField(max_length=255)
    status = models.CharField(max_length=100, blank=True, null=True)
    data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.email
    
    

   
    
class DeleteAccount(models.Model):
    id = models.CharField(primary_key=True, default=generate_id(), editable=False, blank=True, max_length=100)
    reason = models.TextField()
    additionalFeedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.reason
    
    


class PrivacyPolicy(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Markdown content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def get_content_html(self):
        return markdown.markdown(
            self.content,
            extensions=['extra', 'codehilite']
        )
    
    def __str__(self):
        return self.title
    
    

class TermsOfUse(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Markdown content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def get_content_html(self):
        return markdown.markdown(
            self.content,
            extensions=['extra', 'codehilite']
        )
    
    def __str__(self):
        return self.title
    


class SupportMessage(models.Model):
    id = models.CharField(primary_key=True, default=generate_id(), editable=False, blank=True, max_length=100)
    email = models.CharField(max_length=300, blank=True, null=True)
    message = models.CharField(max_length=300, blank=True, null=True)
    isResolved = models.BooleanField(default=False)
    

    def __str__(self):
        return self.email