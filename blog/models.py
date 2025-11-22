from django.db import models
from account.utils import generate_id
from django.utils.text import slugify
import random
from django.utils import timezone
from datetime import timedelta

# Create your models here.

status = (
    ("public", "public"),
    ("draft", "draft"),
)


def random_created_date():
    now = timezone.now()
    three_months_ago = now - timedelta(days=90)
    random_seconds = random.randint(0, int((now - three_months_ago).total_seconds()))
    return three_months_ago + timedelta(seconds=random_seconds)

class Post(models.Model):
    id = models.CharField(
        primary_key=True,
        default=generate_id(),
        editable=False,
        blank=True,
        max_length=100
    )
    headerImage = models.ImageField(upload_to='images/', blank=True, null=True)
    title = models.CharField(max_length=10000, blank=True, null=True)
    slug = models.CharField(max_length=10000, blank=True, null=True, unique=True)
    exerpt = models.TextField()
    content = models.TextField()
    status = models.CharField(max_length=100, choices=status, default="draft")
    created_at = models.DateTimeField(default=random_created_date)
    updated_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.title:
            base_slug = slugify(self.title)  # removes special chars, spaces → "-"
            slug = base_slug
            num = 1
            # ensure unique slug
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title or ""

class PostMedia(models.Model):
    media = models.ImageField(upload_to='images/', blank=True, null=True)
    def __str__(self):
        return self.media.url or ""
    
