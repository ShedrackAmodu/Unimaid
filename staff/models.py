from django.db import models


class StaffMember(models.Model):
    """Library staff members"""

    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="staff/", blank=True, null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    social_links = models.JSONField(
        default=dict, blank=True
    )  # For Facebook, Twitter, LinkedIn etc.
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} - {self.position}"
