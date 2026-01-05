from django.views.generic import ListView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from .models import Loan, Reservation, Fine
from catalog.models import Book


class MyLoansView(LoginRequiredMixin, ListView):
    model = Loan
    template_name = 'circulation/my_loans.html'
    context_object_name = 'loans'
    
    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user).order_by('-checkout_date')


class MyReservationsView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'circulation/my_reservations.html'
    context_object_name = 'reservations'
    
    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user).order_by('-reserved_date')


class ReserveBookView(LoginRequiredMixin, RedirectView):
    pattern_name = 'catalog:book_detail'
    
    def get_redirect_url(self, *args, **kwargs):
        book = get_object_or_404(Book, pk=kwargs['book_id'], is_active=True)
        
        # Check if already reserved
        existing = Reservation.objects.filter(user=self.request.user, book=book, status='pending')
        if existing.exists():
            messages.warning(self.request, 'You already have a pending reservation for this book.')
            return reverse_lazy('catalog:book_detail', kwargs={'pk': book.pk})
        
        # Create reservation
        reservation = Reservation.objects.create(
            user=self.request.user,
            book=book,
            status='pending'
        )
        reservation.update_queue_position()
        
        messages.success(self.request, f'Book "{book.title}" has been reserved. You are #{reservation.queue_position} in the queue.')
        return reverse_lazy('catalog:book_detail', kwargs={'pk': book.pk})


class RenewLoanView(LoginRequiredMixin, RedirectView):
    pattern_name = 'circulation:my_loans'
    
    def get_redirect_url(self, *args, **kwargs):
        loan = get_object_or_404(Loan, pk=kwargs['loan_id'], user=self.request.user)
        
        if loan.renew():
            messages.success(self.request, f'Loan renewed successfully. New due date: {loan.due_date.date()}')
        else:
            messages.error(self.request, 'Unable to renew loan. Maximum renewals reached or loan is overdue.')
        
        return reverse_lazy('circulation:my_loans')


class MyFinesView(LoginRequiredMixin, ListView):
    model = Fine
    template_name = 'circulation/my_fines.html'
    context_object_name = 'fines'
    
    def get_queryset(self):
        return Fine.objects.filter(user=self.request.user).order_by('-created_at')
