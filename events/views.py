from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Event, EventRegistration


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Event.objects.filter(is_published=True, is_cancelled=False)
        
        # Filter by event type
        event_type = self.request.GET.get('type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'upcoming':
            queryset = queryset.filter(start_date__gt=timezone.now())
        elif status == 'past':
            queryset = queryset.filter(end_date__lt=timezone.now())
        
        return queryset.order_by('start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_types'] = Event.EVENT_TYPES
        return context


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Event.objects.filter(is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        # Check if user is registered
        if self.request.user.is_authenticated:
            context['is_registered'] = EventRegistration.objects.filter(
                event=event,
                user=self.request.user
            ).exists()
        else:
            context['is_registered'] = False
        
        return context


class EventRegisterView(LoginRequiredMixin, CreateView):
    model = EventRegistration
    fields = []
    template_name = 'events/event_register.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, slug=kwargs['slug'], is_published=True, is_cancelled=False)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Check if already registered
        existing = EventRegistration.objects.filter(event=self.event, user=self.request.user)
        if existing.exists():
            messages.warning(self.request, 'You are already registered for this event.')
            return redirect('events:event_detail', slug=self.event.slug)
        
        # Check if event is full
        if self.event.is_full:
            messages.error(self.request, 'Sorry, this event is full.')
            return redirect('events:event_detail', slug=self.event.slug)
        
        # Check if registration deadline has passed
        if self.event.registration_deadline and timezone.now() > self.event.registration_deadline:
            messages.error(self.request, 'Registration deadline has passed.')
            return redirect('events:event_detail', slug=self.event.slug)
        
        registration = form.save(commit=False)
        registration.event = self.event
        registration.user = self.request.user
        registration.is_confirmed = True
        registration.confirmation_date = timezone.now()
        registration.save()
        
        messages.success(self.request, f'Successfully registered for "{self.event.title}"!')
        return redirect('events:event_detail', slug=self.event.slug)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context
