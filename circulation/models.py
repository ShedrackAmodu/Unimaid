from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from catalog.models import Book, Copy


class Loan(models.Model):
    """Book loan/borrowing record"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    copy = models.ForeignKey(Copy, on_delete=models.CASCADE, related_name='loans')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    checkout_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    renewed_count = models.IntegerField(default=0)
    max_renewals = models.IntegerField(default=2)
    notes = models.TextField(blank=True)
    checked_out_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checked_out_loans'
    )
    returned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='returned_loans'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Loan"
        verbose_name_plural = "Loans"
        ordering = ['-checkout_date']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} (Due: {self.due_date.date()})"
    
    def is_overdue(self):
        """Check if loan is overdue"""
        return self.status == 'active' and timezone.now() > self.due_date
    
    def can_renew(self):
        """Check if loan can be renewed"""
        return (
            self.status == 'active' and
            self.renewed_count < self.max_renewals and
            not self.is_overdue()
        )
    
    def renew(self, days=14):
        """Renew the loan"""
        if self.can_renew():
            self.due_date = timezone.now() + timedelta(days=days)
            self.renewed_count += 1
            self.save()
            return True
        return False
    
    def return_book(self, returned_by=None):
        """Mark loan as returned"""
        self.status = 'returned'
        self.return_date = timezone.now()
        if returned_by:
            self.returned_to = returned_by
        self.save()
        # Update copy status
        self.copy.status = 'available'
        self.copy.save()
    
    def save(self, *args, **kwargs):
        # Auto-update status to overdue if past due date
        if self.status == 'active' and self.due_date and timezone.now() > self.due_date:
            self.status = 'overdue'
        super().save(*args, **kwargs)


class Reservation(models.Model):
    """Book reservation/waiting list"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('available', 'Available for Pickup'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    queue_position = models.IntegerField(default=1)
    reserved_date = models.DateTimeField(auto_now_add=True)
    notification_sent = models.BooleanField(default=False)
    expiry_date = models.DateTimeField(null=True, blank=True)
    fulfilled_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"
        ordering = ['book', 'queue_position', 'reserved_date']
        unique_together = [['user', 'book', 'status']]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['book', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} (Position: {self.queue_position})"
    
    def update_queue_position(self):
        """Update queue position based on other pending reservations"""
        pending = Reservation.objects.filter(
            book=self.book,
            status='pending'
        ).exclude(pk=self.pk).order_by('reserved_date')
        self.queue_position = pending.count() + 1
        self.save(update_fields=['queue_position'])
    
    def fulfill(self):
        """Mark reservation as fulfilled"""
        self.status = 'fulfilled'
        self.fulfilled_date = timezone.now()
        self.save()
        # Update queue positions for remaining reservations
        remaining = Reservation.objects.filter(
            book=self.book,
            status='pending'
        ).exclude(pk=self.pk)
        for idx, res in enumerate(remaining, 1):
            res.queue_position = idx
            res.save(update_fields=['queue_position'])


class Fine(models.Model):
    """Overdue fines and fees"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('waived', 'Waived'),
        ('cancelled', 'Cancelled'),
    ]
    
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='fines')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fines')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField()
    paid_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    waived_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='waived_fines'
    )
    waiver_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Fine"
        verbose_name_plural = "Fines"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - ${self.amount} ({self.get_status_display()})"
    
    def mark_paid(self, payment_method='', transaction_id=''):
        """Mark fine as paid"""
        self.status = 'paid'
        self.paid_date = timezone.now()
        self.payment_method = payment_method
        self.transaction_id = transaction_id
        self.save()
    
    def waive(self, waived_by, reason=''):
        """Waive the fine"""
        self.status = 'waived'
        self.waived_by = waived_by
        self.waiver_reason = reason
        self.save()
