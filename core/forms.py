from django import forms
from .models import ContactMessage, Subscriber, Event


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your email",
                    "required": True,
                }
            )
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "slug",
            "description",
            "start_date",
            "end_date",
            "location",
            "image",
            "is_published",
        ]
        widgets = {
            "start_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class ContactForm(forms.ModelForm):
    """Contact form for user inquiries"""

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control valid",
                    "onfocus": "this.placeholder = ''",
                    "onblur": "this.placeholder = 'Enter your name'",
                    "placeholder": "Enter your name",
                    "required": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control valid",
                    "onfocus": "this.placeholder = ''",
                    "onblur": "this.placeholder = 'Enter email address'",
                    "placeholder": "Email",
                    "required": True,
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "onfocus": "this.placeholder = ''",
                    "onblur": "this.placeholder = 'Enter Subject'",
                    "placeholder": "Enter Subject",
                    "required": True,
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control w-100",
                    "cols": 30,
                    "rows": 9,
                    "onfocus": "this.placeholder = ''",
                    "onblur": "this.placeholder = 'Enter Message'",
                    "placeholder": "Enter Message",
                    "required": True,
                }
            ),
        }
