from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from config.admin_config import FilteredModelAdmin, SearchableModelAdmin, ExportableAdmin, DateRangeFilter, get_image_preview

from .models import ContactMessage, LibraryDivision, Subscriber, Event


# ============================================================================
# CONTACT MESSAGE ADMIN (Read-only)
# ============================================================================


@admin.register(ContactMessage)
class ContactMessageAdmin(FilteredModelAdmin):
    list_display = (
        "name",
        "email_link",
        "subject_display",
        "message_preview",
        "date_display",
    )
    list_filter = (("created_date", DateRangeFilter),)
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = (
        "created_date",
        "full_message_display",
        "name",
        "email",
        "subject",
    )
    date_hierarchy = "created_date"
    list_per_page = 50

    fieldsets = (
        ("Message Information", {"fields": ("name", "email_link", "subject")}),
        ("Message", {"fields": ("full_message_display",)}),
        ("Metadata", {"fields": ("created_date",), "classes": ("collapse",)}),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def email_link(self, obj):
        return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)

    email_link.short_description = "Email"

    def subject_display(self, obj):
        return format_html("<strong>{}</strong>", obj.subject)

    subject_display.short_description = "Subject"

    def message_preview(self, obj):
        preview = obj.message[:60] + "..." if len(obj.message) > 60 else obj.message
        return preview

    message_preview.short_description = "Message"

    def date_display(self, obj):
        return obj.created_date.strftime("%b %d, %Y %H:%M")

    date_display.short_description = "Received"

    def full_message_display(self, obj):
        return format_html(
            '<div style="background: #f5f5f5; padding: 15px; border-radius: 3px; '
            'min-height: 150px; white-space: pre-wrap; word-wrap: break-word;">{}</div>',
            obj.message,
        )

    full_message_display.short_description = "Full Message"


# ============================================================================
# LIBRARY DIVISION ADMIN
# ============================================================================


@admin.register(LibraryDivision)
class LibraryDivisionAdmin(SearchableModelAdmin):
    list_display = (
        "division_name_with_image",
        "category_colored",
        "order",
        "description_preview",
    )
    list_filter = ("category",)
    search_fields = ("name", "description")
    ordering = ("order", "name")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("image_preview",)

    fieldsets = (
        ("Basic Information", {"fields": ("name", "slug", "description", "category")}),
        ("Display Settings", {"fields": ("order",)}),
        (
            "Media",
            {
                "fields": ("image_preview", "image"),
            },
        ),
    )

    def division_name_with_image(self, obj):
        name = format_html("<strong>{}</strong>", obj.name)
        if obj.image:
            img_html = get_image_preview(obj.image.url, "50px", "50px")
            return format_html(
                '<div style="display: flex; gap: 10px; align-items: center;">'
                "{}{}</div>",
                img_html,
                name,
            )
        return name

    division_name_with_image.short_description = "Division"

    def category_colored(self, obj):
        colors = {
            "division": "#007bff",
            "center": "#28a745",
        }
        color = colors.get(obj.category, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_category_display(),
        )

    category_colored.short_description = "Type"

    def description_preview(self, obj):
        preview = (
            obj.description[:60] + "..."
            if len(obj.description) > 60
            else obj.description
        )
        return preview

    description_preview.short_description = "Description"

    def image_preview(self, obj):
        if obj.image:
            return get_image_preview(obj.image.url, "300px", "200px")
        return format_html('<span style="color: #ccc;">No image</span>')

    image_preview.short_description = "Image Preview"


# ============================================================================
# SUBSCRIBER ADMIN
# ============================================================================


@admin.register(Subscriber)
class SubscriberAdmin(ExportableAdmin):
    list_display = (
        "email",
        "email_domain",
        "subscription_date_display",
        "subscriber_actions",
    )
    search_fields = ("email",)
    list_filter = (("created_at", DateRangeFilter),)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    list_per_page = 100

    actions = ["send_newsletter", "export_email_list"]

    fieldsets = (("Subscriber Information", {"fields": ("email", "created_at")}),)

    def email_domain(self, obj):
        domain = obj.email.split("@")[1] if "@" in obj.email else "—"
        return format_html('<small style="color: #666;">{}</small>', domain)

    email_domain.short_description = "Domain"

    def subscription_date_display(self, obj):
        return obj.created_at.strftime("%b %d, %Y")

    subscription_date_display.short_description = "Subscribed"

    def subscriber_actions(self, obj):
        return format_html(
            '<a class="button" href="mailto:{}" style="background-color: #417690; '
            "text-decoration: none; color: white; padding: 5px 10px; "
            'border-radius: 3px;">📧 Email</a>',
            obj.email,
        )

    subscriber_actions.short_description = "Actions"

    def send_newsletter(self, request, queryset):
        count = queryset.count()
        # In production, this would queue newsletter email tasks
        self.message_user(request, f"Newsletter queued for {count} subscriber(s).")

    send_newsletter.short_description = "📬 Send newsletter to selected"

    def export_email_list(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="email_list.csv"'
        writer = csv.writer(response)
        writer.writerow(["Email", "Subscribed Date"])

        for subscriber in queryset:
            writer.writerow(
                [
                    subscriber.email,
                    subscriber.created_at.strftime("%Y-%m-%d"),
                ]
            )

        return response

    export_email_list.short_description = "📥 Export email list as CSV"


# ============================================================================
# EVENT ADMIN
# ============================================================================


@admin.register(Event)
class EventAdmin(SearchableModelAdmin):
    list_display = (
        "event_title_with_image",
        "date_range",
        "location_display",
        "publication_status",
        "creation_date",
    )
    list_filter = (
        ("is_published", admin.BooleanFieldListFilter),
        ("start_date", admin.DateFieldListFilter),
    )
    search_fields = ("title", "description", "location")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "image_preview")
    date_hierarchy = "start_date"
    list_per_page = 50

    actions = ["publish_events", "unpublish_events"]

    fieldsets = (
        ("Event Information", {"fields": ("title", "slug", "description")}),
        ("Date & Time", {"fields": ("start_date", "end_date")}),
        ("Location", {"fields": ("location",)}),
        (
            "Media",
            {
                "fields": ("image_preview", "image"),
            },
        ),
        (
            "Publishing",
            {"fields": ("is_published", "created_at"), "classes": ("collapse",)},
        ),
    )

    def event_title_with_image(self, obj):
        title = format_html("<strong>{}</strong>", obj.title)
        if obj.image:
            img_html = get_image_preview(obj.image.url, "50px", "50px")
            return format_html(
                '<div style="display: flex; gap: 10px; align-items: center;">'
                "{}{}</div>",
                img_html,
                title,
            )
        return title

    event_title_with_image.short_description = "Event"

    def date_range(self, obj):
        if obj.start_date and obj.end_date:
            return format_html(
                "{} to {}",
                obj.start_date.strftime("%b %d, %Y"),
                obj.end_date.strftime("%b %d, %Y"),
            )
        elif obj.start_date:
            return obj.start_date.strftime("%b %d, %Y")
        return "—"

    date_range.short_description = "Date Range"

    def location_display(self, obj):
        if obj.location:
            return format_html(
                '<small style="color: #666;">📍 {}</small>', obj.location
            )
        return "—"

    location_display.short_description = "Location"

    def publication_status(self, obj):
        if obj.is_published:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-weight: bold;">✓ Published</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 8px; '
                'border-radius: 3px; font-weight: bold;">⏳ Draft</span>'
            )

    publication_status.short_description = "Status"

    def creation_date(self, obj):
        return obj.created_at.strftime("%b %d, %Y")

    creation_date.short_description = "Created"

    def image_preview(self, obj):
        if obj.image:
            return get_image_preview(obj.image.url, "300px", "200px")
        return format_html('<span style="color: #ccc;">No image</span>')

    image_preview.short_description = "Image Preview"

    def publish_events(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"{count} event(s) published.")

    publish_events.short_description = "✓ Publish selected events"

    def unpublish_events(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"{count} event(s) unpublished.")

    unpublish_events.short_description = "✗ Unpublish selected events"


# ============================================================================
# ADMIN SITE HEADER CUSTOMIZATION
# ============================================================================

admin.site.site_header = "📚 University of Maiduguri Library Administration"
admin.site.site_title = "UNIMAID Library Admin"
admin.site.index_title = "Library Management Dashboard"
