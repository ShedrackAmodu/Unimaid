from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Subscriber(models.Model):
    """Email subscribers for admissions/announcements"""

    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


class Event(models.Model):
    """Simple Event model for listing events"""

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    """Model for contact form submissions"""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"


class LibraryDivision(models.Model):
    """Model for library divisions and information centers"""

    DIVISION_CATEGORIES = [
        ("division", "Division"),
        ("center", "Information Center"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to="divisions/", blank=True, null=True)
    category = models.CharField(
        max_length=20, choices=DIVISION_CATEGORIES, default="division"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:200]
            self.slug = base
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:division_detail", args=[self.slug])

    def __str__(self):
        return self.name
