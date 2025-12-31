from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import ContactMessage, LibraryDivision, Subscriber, Event
from .forms import ContactForm, SubscriberForm, EventForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from library.utils import paginate_queryset


def admissions(request):
    """Admissions / Subscribe page"""
    if request.method == "POST":
        form = SubscriberForm(request.POST)
        if form.is_valid():
            try:
                subscriber, created = Subscriber.objects.get_or_create(
                    **form.cleaned_data
                )
            except Exception:
                subscriber = None
                created = False

            if subscriber:
                if created:
                    messages.success(request, "Thanks for subscribing!")
                else:
                    messages.info(request, "You are already subscribed.")
            else:
                messages.error(request, "Could not save your subscription. Try again.")

            return redirect("core:admissions")
    else:
        form = SubscriberForm()

    return render(request, "core/admissions.html", {"form": form})


def courses(request):
    """Courses / divisions overview"""
    divisions = LibraryDivision.objects.all()
    return render(request, "core/courses.html", {"divisions": divisions})


def events(request):
    """Events listing — show published events with pagination."""
    q = request.GET.get("q", "").strip()
    events_qs = Event.objects.filter(is_published=True).order_by("-start_date")
    if q:
        events_qs = events_qs.filter(title__icontains=q) | events_qs.filter(
            description__icontains=q
        )

    events_page = paginate_queryset(events_qs, request.GET.get("page"), per_page=6)

    return render(request, "core/events.html", {"events": events_page, "query": q})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_published=True)
    return render(request, "core/event_detail.html", {"event": event})


@login_required
def event_create(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            ev = form.save()
            messages.success(request, "Event created.")
            return redirect("core:event_detail", pk=ev.pk)
    else:
        form = EventForm()

    return render(request, "core/events_form.html", {"form": form, "create": True})


@login_required
def event_update(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            ev = form.save()
            messages.success(request, "Event updated.")
            return redirect("core:event_detail", pk=ev.pk)
    else:
        form = EventForm(instance=event)

    return render(
        request,
        "core/events_form.html",
        {"form": form, "create": False, "event": event},
    )


@login_required
def event_delete(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted.")
        return redirect("core:events")

    return render(request, "core/events_confirm_delete.html", {"event": event})


def home(request):
    """Homepage view"""
    divisions = LibraryDivision.objects.all()[:6]  # Show first 6 divisions on homepage
    context = {
        "divisions": divisions,
    }
    return render(request, "core/home.html", context)


def contact(request):
    """Contact page view"""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save contact message to database
            contact_message = form.save()

            # Send email notification (optional)
            try:
                send_mail(
                    f"Contact Form: {contact_message.subject}",
                    f"From: {contact_message.name} ({contact_message.email})\n\n{contact_message.message}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],  # Send to admin
                    fail_silently=True,
                )
            except Exception as e:
                # Log the error but don't fail the form submission
                print(f"Email sending failed: {e}")

            messages.success(request, "Your message has been sent successfully!")
            return redirect("core:contact")
    else:
        form = ContactForm()

    context = {
        "form": form,
    }
    return render(request, "core/contact.html", context)


def about(request):
    """About page view"""
    return render(request, "core/about.html")


def history(request):
    """History page view"""
    return render(request, "core/history.html")


def library_organization(request):
    """Library organization/divisions page"""
    divisions = LibraryDivision.objects.filter(category="division")
    centers = LibraryDivision.objects.filter(category="center")

    context = {
        "divisions": divisions,
        "centers": centers,
    }
    return render(request, "core/library_organization.html", context)


def search(request):
    """Search functionality across the site"""
    query = request.GET.get("q", "")
    results = []

    if query:
        # Search in library divisions
        divisions = LibraryDivision.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

        results = {
            "divisions": divisions,
            "query": query,
        }

    context = {
        "results": results,
        "query": query,
    }
    return render(request, "core/search.html", context)


def division_detail(request, slug):
    """Detail view for a library division or information center"""
    division = get_object_or_404(LibraryDivision, slug=slug)
    context = {"division": division}
    return render(request, "core/division_detail.html", context)
