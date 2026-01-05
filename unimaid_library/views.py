from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from blog.models import Post
from events.models import Event
from catalog.models import Book
from repository.models import Document
from accounts.models import StaffMember


class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_posts'] = Post.objects.filter(is_published=True)[:3]
        context['upcoming_events'] = Event.objects.filter(is_published=True, is_cancelled=False).order_by('start_date')[:3]
        context['featured_books'] = Book.objects.filter(is_featured=True, is_active=True)[:6]
        context['recent_documents'] = Document.objects.filter(is_active=True, is_approved=True).order_by('-submission_date')[:6]
        context['staff_members'] = StaffMember.objects.filter(is_active=True)[:6]
        return context


class ContactView(FormView):
    template_name = 'contact.html'
    success_url = reverse_lazy('contact')
    
    def get_form_class(self):
        from django import forms
        
        class ContactForm(forms.Form):
            name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }))
            email = forms.EmailField(widget=forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email'
            }))
            subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject'
            }))
            message = forms.CharField(widget=forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Your Message'
            }))
        
        return ContactForm
    
    def form_valid(self, form):
        # Send email
        try:
            send_mail(
                subject=f"Contact Form: {form.cleaned_data['subject']}",
                message=f"From: {form.cleaned_data['name']} ({form.cleaned_data['email']})\n\n{form.cleaned_data['message']}",
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else settings.LIBRARY_EMAIL,
                recipient_list=[settings.LIBRARY_EMAIL],
                fail_silently=False,
            )
            messages.success(self.request, 'Thank you for contacting us! We will get back to you soon.')
        except Exception as e:
            messages.error(self.request, 'Sorry, there was an error sending your message. Please try again later.')
        
        return super().form_valid(form)


class NewsletterSubscribeView(FormView):
    template_name = 'base.html'
    success_url = reverse_lazy('home')
    
    def get_form_class(self):
        from django import forms
        
        class NewsletterForm(forms.Form):
            email = forms.EmailField()
        
        return NewsletterForm
    
    def form_valid(self, form):
        # In a real application, you would save this to a NewsletterSubscriber model
        messages.success(self.request, 'Thank you for subscribing to our newsletter!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please enter a valid email address.')
        return redirect('home')

