from django.db import models
from django.urls import reverse
from django.utils import timezone
from accounts.models import User


class Collection(models.Model):
    """Document collections/categories"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Collection"
        verbose_name_plural = "Collections"
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('repository:collection_detail', kwargs={'slug': self.slug})


class Document(models.Model):
    """Institutional repository documents"""
    DOCUMENT_TYPES = [
        ('thesis', 'Thesis'),
        ('dissertation', 'Dissertation'),
        ('journal', 'Journal Article'),
        ('conference', 'Conference Paper'),
        ('project', 'Project Report'),
        ('book', 'Book Chapter'),
        ('dataset', 'Dataset'),
        ('other', 'Other'),
    ]
    
    ACCESS_LEVELS = [
        ('open', 'Open Access'),
        ('restricted', 'Restricted'),
        ('embargoed', 'Embargoed'),
        ('private', 'Private'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=500)
    subtitle = models.CharField(max_length=500, blank=True)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Authorship
    author = models.CharField(max_length=200)  # Primary author
    authors = models.ManyToManyField(User, related_name='authored_documents', blank=True)
    department = models.CharField(max_length=200, blank=True)
    faculty = models.CharField(max_length=200, blank=True)
    supervisor = models.CharField(max_length=200, blank=True)
    
    # Publication Information
    publication_date = models.DateField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    journal_name = models.CharField(max_length=200, blank=True)
    volume = models.CharField(max_length=50, blank=True)
    issue = models.CharField(max_length=50, blank=True)
    pages = models.CharField(max_length=50, blank=True)
    
    # File and Access
    file = models.FileField(upload_to='repository/documents/')
    file_size = models.BigIntegerField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='repository/thumbnails/', blank=True, null=True)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='open')
    embargo_date = models.DateField(null=True, blank=True)
    
    # Metadata (Dublin Core compatible)
    abstract = models.TextField(blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    subject = models.CharField(max_length=500, blank=True)
    language = models.CharField(max_length=50, default='English')
    doi = models.CharField(max_length=100, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    issn = models.CharField(max_length=20, blank=True)
    
    # Rights and Licensing
    license = models.CharField(max_length=200, blank=True)
    copyright_holder = models.CharField(max_length=200, blank=True)
    rights_statement = models.TextField(blank=True)
    
    # Submission Information
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_documents'
    )
    submission_date = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_documents'
    )
    review_date = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Statistics
    download_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    
    # Additional Fields
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-submission_date', 'title']
        indexes = [
            models.Index(fields=['document_type', 'is_active']),
            models.Index(fields=['department', 'year']),
            models.Index(fields=['-submission_date']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('repository:document_detail', kwargs={'pk': self.pk})
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_download_count(self):
        """Increment download count"""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def is_accessible(self, user=None):
        """Check if document is accessible to user"""
        if self.access_level == 'open':
            return True
        if self.access_level == 'private':
            return user and (user == self.submitted_by or user.is_staff)
        if self.access_level == 'embargoed':
            if not self.embargo_date:
                return True
            return timezone.now().date() >= self.embargo_date
        if self.access_level == 'restricted':
            return user and user.is_authenticated
        return False
    
    def save(self, *args, **kwargs):
        # Auto-set year from publication_date if not set
        if not self.year and self.publication_date:
            self.year = self.publication_date.year
        # Auto-set file_size if file exists
        if self.file and not self.file_size:
            try:
                self.file_size = self.file.size
            except:
                pass
        super().save(*args, **kwargs)
