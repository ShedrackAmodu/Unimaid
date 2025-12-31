from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Document(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="repository/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200]
            self.slug = base
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("repository:doc_detail", args=[self.slug])
