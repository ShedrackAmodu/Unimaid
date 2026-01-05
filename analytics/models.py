from django.db import models
from django.utils import timezone
from accounts.models import User
from catalog.models import Book
from repository.models import Document


class Metric(models.Model):
    """System metrics and KPIs"""
    METRIC_TYPES = [
        ('circulation', 'Circulation'),
        ('catalog', 'Catalog'),
        ('repository', 'Repository'),
        ('users', 'Users'),
        ('events', 'Events'),
        ('blog', 'Blog'),
        ('system', 'System'),
    ]
    
    name = models.CharField(max_length=200)
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    unit = models.CharField(max_length=50, blank=True)
    date = models.DateField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Metric"
        verbose_name_plural = "Metrics"
        ordering = ['-date', 'metric_type', 'name']
        indexes = [
            models.Index(fields=['metric_type', 'date']),
            models.Index(fields=['-date']),
        ]
    
    def __str__(self):
        return f"{self.name}: {self.value} {self.unit} ({self.date})"


class Report(models.Model):
    """Generated reports"""
    REPORT_TYPES = [
        ('circulation', 'Circulation Report'),
        ('catalog', 'Catalog Report'),
        ('repository', 'Repository Report'),
        ('users', 'User Report'),
        ('fines', 'Fines Report'),
        ('analytics', 'Analytics Report'),
        ('custom', 'Custom Report'),
    ]
    
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    data = models.JSONField(default=dict)
    file = models.FileField(upload_to='reports/', blank=True, null=True)
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_reports'
    )
    generated_date = models.DateTimeField(auto_now_add=True)
    date_range_start = models.DateField(null=True, blank=True)
    date_range_end = models.DateField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ['-generated_date']
        indexes = [
            models.Index(fields=['report_type', '-generated_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"


class UserActivity(models.Model):
    """User activity tracking"""
    ACTION_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('search', 'Search'),
        ('view_book', 'View Book'),
        ('view_document', 'View Document'),
        ('borrow', 'Borrow Book'),
        ('return', 'Return Book'),
        ('reserve', 'Reserve Book'),
        ('download', 'Download Document'),
        ('comment', 'Comment'),
        ('register_event', 'Register Event'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True
    )
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.CharField(max_length=500)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "User Activity"
        verbose_name_plural = "User Activities"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"{user_str} - {self.get_action_type_display()}"


class SearchQuery(models.Model):
    """Search query analytics"""
    query = models.CharField(max_length=500)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='search_queries'
    )
    result_count = models.IntegerField(default=0)
    search_type = models.CharField(
        max_length=50,
        choices=[
            ('catalog', 'Catalog'),
            ('repository', 'Repository'),
            ('blog', 'Blog'),
            ('general', 'General'),
        ],
        default='general'
    )
    filters = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Search Query"
        verbose_name_plural = "Search Queries"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['search_type', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.query} ({self.result_count} results)"
