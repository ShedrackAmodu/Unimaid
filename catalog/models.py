from django.db import models
from django.urls import reverse
from django.utils import timezone
from accounts.models import User


class Genre(models.Model):
    """Book genres/categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('catalog:genre_detail', kwargs={'slug': self.slug})


class Publisher(models.Model):
    """Book publishers"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Publisher"
        verbose_name_plural = "Publishers"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Author(models.Model):
    """Book authors"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return str(self)
    
    def get_absolute_url(self):
        return reverse('catalog:author_detail', kwargs={'pk': self.pk})


class Book(models.Model):
    """Main book/resource model"""
    title = models.CharField(max_length=500)
    subtitle = models.CharField(max_length=500, blank=True)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    isbn13 = models.CharField(max_length=20, unique=True, blank=True, null=True)
    authors = models.ManyToManyField(Author, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    edition = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=50, default='English')
    pages = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='book_qr_codes/', blank=True, null=True)
    total_copies = models.IntegerField(default=0)
    available_copies = models.IntegerField(default=0)
    location = models.CharField(max_length=200, blank=True)
    call_number = models.CharField(max_length=100, blank=True)
    subject_heading = models.CharField(max_length=500, blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ['-created_at', 'title']
        indexes = [
            models.Index(fields=['title', 'isbn']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('catalog:book_detail', kwargs={'pk': self.pk})
    
    def update_available_copies(self):
        """Update available copies count"""
        self.available_copies = self.copies.filter(status='available').count()
        self.save(update_fields=['available_copies'])
    
    @property
    def is_available(self):
        return self.available_copies > 0


class Copy(models.Model):
    """Individual copy of a book"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_loan', 'On Loan'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Under Maintenance'),
        ('lost', 'Lost'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    barcode = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    location = models.CharField(max_length=200, blank=True)
    acquisition_date = models.DateField(null=True, blank=True)
    acquisition_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    condition = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Copy"
        verbose_name_plural = "Copies"
        ordering = ['book', 'barcode']
    
    def __str__(self):
        return f"{self.book.title} - Copy {self.barcode}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.book.update_available_copies()
