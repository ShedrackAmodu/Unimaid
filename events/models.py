from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from accounts.models import User


class Event(models.Model):
    """Library events"""
    EVENT_TYPES = [
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('exhibition', 'Exhibition'),
        ('training', 'Training'),
        ('meeting', 'Meeting'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, default='other')
    featured_image = models.ImageField(upload_to='events/images/', blank=True, null=True)
    
    # Date and Time
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    registration_deadline = models.DateTimeField(null=True, blank=True)
    
    # Location
    location = models.CharField(max_length=200)
    venue = models.CharField(max_length=200, blank=True)
    is_online = models.BooleanField(default=False)
    online_link = models.URLField(blank=True)
    
    # Capacity and Registration
    capacity = models.IntegerField(null=True, blank=True)
    requires_registration = models.BooleanField(default=False)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    
    # Organizer
    organizer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organized_events'
    )
    organizer_name = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Additional Information
    tags = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ['start_date', 'title']
        indexes = [
            models.Index(fields=['is_published', 'start_date']),
            models.Index(fields=['event_type', 'is_published']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def is_upcoming(self):
        """Check if event is upcoming"""
        return self.start_date > timezone.now() and not self.is_cancelled
    
    @property
    def is_ongoing(self):
        """Check if event is currently ongoing"""
        now = timezone.now()
        return self.start_date <= now <= self.end_date and not self.is_cancelled
    
    @property
    def is_past(self):
        """Check if event is past"""
        return self.end_date < timezone.now()
    
    @property
    def registration_count(self):
        """Get number of registrations"""
        return self.registrations.filter(is_confirmed=True).count()
    
    @property
    def available_spots(self):
        """Get available spots"""
        if not self.capacity:
            return None
        return max(0, self.capacity - self.registration_count)
    
    @property
    def is_full(self):
        """Check if event is full"""
        if not self.capacity:
            return False
        return self.registration_count >= self.capacity


class EventRegistration(models.Model):
    """Event registrations"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    is_confirmed = models.BooleanField(default=False)
    is_attended = models.BooleanField(default=False)
    registration_date = models.DateTimeField(auto_now_add=True)
    confirmation_date = models.DateTimeField(null=True, blank=True)
    attendance_date = models.DateTimeField(null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('waived', 'Waived'),
        ],
        default='pending'
    )
    payment_reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Event Registration"
        verbose_name_plural = "Event Registrations"
        ordering = ['-registration_date']
        unique_together = [['event', 'user']]
        indexes = [
            models.Index(fields=['event', 'is_confirmed']),
            models.Index(fields=['user', 'is_confirmed']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
    
    def confirm(self):
        """Confirm registration"""
        self.is_confirmed = True
        self.confirmation_date = timezone.now()
        self.save()
    
    def mark_attended(self):
        """Mark as attended"""
        self.is_attended = True
        self.attendance_date = timezone.now()
        self.save()
