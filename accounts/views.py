from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView as BaseLoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User, Profile
from circulation.models import Loan, Reservation, Fine
from catalog.models import Book


class RegisterView(CreateView):
    model = User
    template_name = 'accounts/register.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'membership_type', 'phone_number', 'password']
    success_url = reverse_lazy('accounts:dashboard')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        Profile.objects.create(user=user)
        login(self.request, user)
        messages.success(self.request, 'Registration successful! Welcome to Ramat Library.')
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['password'].widget.attrs.update({'class': 'form-control', 'type': 'password'})
        for field in form.fields:
            if field != 'password':
                form.fields[field].widget.attrs.update({'class': 'form-control'})
        return form


class LoginView(BaseLoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().get_full_name() or form.get_user().username}!')
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Active loans
        context['active_loans'] = Loan.objects.filter(user=user, status='active').order_by('due_date')
        context['overdue_loans'] = Loan.objects.filter(user=user, status='overdue')
        
        # Reservations
        context['reservations'] = Reservation.objects.filter(user=user, status__in=['pending', 'available']).order_by('queue_position')
        
        # Fines
        context['pending_fines'] = Fine.objects.filter(user=user, status='pending')
        context['total_fines'] = sum(fine.amount for fine in context['pending_fines'])
        
        # Recently viewed (can be implemented with session/cache)
        context['recent_books'] = Book.objects.filter(is_featured=True)[:5]
        
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = getattr(self.request.user, 'profile', None)
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'accounts/profile_edit.html'
    fields = ['bio', 'profile_picture', 'department', 'student_id', 'staff_id', 'emergency_contact', 'emergency_phone']
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)
