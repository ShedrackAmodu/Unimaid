from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.utils import timezone
from catalog.models import Book, Copy
from circulation.models import Loan, Reservation, Fine
from repository.models import Document
from blog.models import Post
from events.models import Event
from accounts.models import User


class AnalyticsDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'analytics/dashboard.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Catalog statistics
        context['total_books'] = Book.objects.filter(is_active=True).count()
        context['total_copies'] = Copy.objects.count()
        context['available_copies'] = Copy.objects.filter(status='available').count()
        context['on_loan'] = Copy.objects.filter(status='on_loan').count()
        
        # Circulation statistics
        context['active_loans'] = Loan.objects.filter(status='active').count()
        context['overdue_loans'] = Loan.objects.filter(status='overdue').count()
        context['pending_reservations'] = Reservation.objects.filter(status='pending').count()
        context['total_fines'] = Fine.objects.filter(status='pending').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Repository statistics
        context['total_documents'] = Document.objects.filter(is_active=True).count()
        context['total_downloads'] = Document.objects.aggregate(
            total=Sum('download_count')
        )['total'] or 0
        
        # User statistics
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        
        # Blog statistics
        context['total_posts'] = Post.objects.filter(is_published=True).count()
        
        # Event statistics
        context['upcoming_events'] = Event.objects.filter(
            is_published=True,
            is_cancelled=False,
            start_date__gt=timezone.now()
        ).count()
        
        return context
