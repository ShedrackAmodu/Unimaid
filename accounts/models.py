from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import uuid


class User(AbstractUser):
    """Custom User model extending AbstractUser"""
    
    MEMBERSHIP_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff'),
        ('public', 'Public'),
        ('admin', 'Administrator'),
    ]
    
    membership_type = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_CHOICES,
        default='student'
    )
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    qr_code_data = models.CharField(max_length=255, blank=True)
    is_librarian = models.BooleanField(default=False)
    is_staff_member = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.get_membership_type_display()})"
    
    def generate_qr_code(self):
        """Generate QR code for user"""
        if not self.qr_code_data:
            self.qr_code_data = str(uuid.uuid4())
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.qr_code_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        filename = f'qr_{self.username}_{self.qr_code_data[:8]}.png'
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
        return self.qr_code
    
    def save(self, *args, **kwargs):
        if not self.qr_code_data:
            self.qr_code_data = str(uuid.uuid4())
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)


class Profile(models.Model):
    """Extended profile information for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    department = models.CharField(max_length=200, blank=True)
    student_id = models.CharField(max_length=50, blank=True, null=True)
    staff_id = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact = models.CharField(max_length=200, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
    
    def __str__(self):
        return f"Profile of {self.user.username}"


class StaffMember(models.Model):
    """Library staff directory"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    position = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    office_location = models.CharField(max_length=200, blank=True)
    office_hours = models.CharField(max_length=200, blank=True)
    specialization = models.TextField(blank=True)
    qualifications = models.TextField(blank=True)
    phone_extension = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"
        ordering = ['display_order', 'user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"
