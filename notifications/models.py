from django.db import models
from account.utils import generate_id
from account.models import User

# Create your models here.



# export type NotificationFrequency =
#   | "daily"
#   | "every-other-day"
#   | "weekly"
#   | "monthly";

NotificationFrequency = (
    ("daily", "daily"),
    ("every-other-day", "every-other-day"),
    ("weekly", "weekly"),
    ("monthly", "monthly"),
)

class NoteNotification(models.Model):
    id = models.CharField(primary_key=True, default=generate_id(), editable=False, blank=True, max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_notification')
    reminder_time =models.CharField(max_length=50, blank=True, null=True)
    frequency = models.CharField(max_length=500, blank=True, null=True, choices=NotificationFrequency, default="daily")
    title =  models.CharField(max_length=1000, blank=True, null=True)
    content = models.TextField()
    noteId = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.email}"