"""
Centralized Django Admin Configuration
Provides custom admin classes, filters, and actions for all models
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from django import forms


# ============================================================================
# CUSTOM FILTERS
# ============================================================================


class DateRangeFilter(admin.FieldListFilter):
    """Filter for date range - Last 7 days, 30 days, etc."""

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.field = field
        self.field_path = field_path
        super().__init__(field, request, params, model, model_admin, field_path)
        self.title = "Date Range"

    def expected_parameters(self):
        return [f"{self.field_path}__gte", f"{self.field_path}__lte"]

    def choices(self, cl):
        return [
            {
                "selected": False,
                "query_string": cl.get_query_string({}, [self.field_path]),
                "display": "All",
            },
            {
                "selected": False,
                "query_string": cl.get_query_string(
                    {f"{self.field_path}__gte": timezone.now().date()}
                ),
                "display": "Today",
            },
            {
                "selected": False,
                "query_string": cl.get_query_string(
                    {
                        f"{self.field_path}__gte": (
                            timezone.now() - timedelta(days=7)
                        ).date()
                    }
                ),
                "display": "Last 7 Days",
            },
            {
                "selected": False,
                "query_string": cl.get_query_string(
                    {
                        f"{self.field_path}__gte": (
                            timezone.now() - timedelta(days=30)
                        ).date()
                    }
                ),
                "display": "Last 30 Days",
            },
            {
                "selected": False,
                "query_string": cl.get_query_string(
                    {
                        f"{self.field_path}__gte": (
                            timezone.now() - timedelta(days=90)
                        ).date()
                    }
                ),
                "display": "Last 90 Days",
            },
        ]


class PublishedFilter(admin.SimpleListFilter):
    """Filter for published/unpublished status"""

    title = "Publication Status"
    parameter_name = "published_status"

    def lookups(self, request, model_admin):
        return (
            ("published", "Published"),
            ("draft", "Draft"),
            ("archived", "Archived"),
        )

    def queryset(self, request, queryset):
        if self.value() == "published":
            return queryset.filter(is_published=True)
        elif self.value() == "draft":
            return queryset.filter(is_published=False)


class StatusFilter(admin.SimpleListFilter):
    """Generic status filter"""

    title = "Status"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            ("available", "Available"),
            ("checked_out", "Checked Out"),
            ("reserved", "Reserved"),
            ("lost", "Lost"),
            ("damaged", "Damaged"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())


# ============================================================================
# CUSTOM ADMIN ACTIONS
# ============================================================================


def mark_as_published(modeladmin, request, queryset):
    """Action to mark posts as published"""
    updated = queryset.update(is_published=True)
    modeladmin.message_user(request, f"{updated} items marked as published.")


mark_as_published.short_description = "✓ Mark selected as published"


def mark_as_draft(modeladmin, request, queryset):
    """Action to mark posts as draft"""
    updated = queryset.update(is_published=False)
    modeladmin.message_user(request, f"{updated} items marked as draft.")


mark_as_draft.short_description = "✗ Mark selected as draft"


def mark_as_featured(modeladmin, request, queryset):
    """Action to mark posts as featured"""
    updated = queryset.update(is_featured=True)
    modeladmin.message_user(request, f"{updated} items marked as featured.")


mark_as_featured.short_description = "⭐ Mark selected as featured"


def mark_as_not_featured(modeladmin, request, queryset):
    """Action to unmark posts as featured"""
    updated = queryset.update(is_featured=False)
    modeladmin.message_user(request, f"{updated} items unmarked as featured.")


mark_as_not_featured.short_description = "☆ Mark selected as not featured"


# ============================================================================
# BASE CUSTOM ADMIN CLASSES
# ============================================================================


class RobustModelAdmin(admin.ModelAdmin):
    """
    Enhanced base admin class with common features:
    - Date filtering
    - Better search
    - Pagination
    - Read-only timestamps
    """

    date_hierarchy = None
    list_per_page = 50
    empty_value_display = "—"

    def get_readonly_fields(self, request, obj=None):
        """Make timestamp fields read-only"""
        readonly = list(self.readonly_fields) if self.readonly_fields else []
        # Add common timestamp fields
        for field in [
            "created_at",
            "updated_at",
            "created_date",
            "modified_date",
            "last_updated",
            "timestamp",
            "published_date",
        ]:
            if (
                field in [f.name for f in self.model._meta.get_fields()]
                and field not in readonly
            ):
                readonly.append(field)
        return readonly

    def get_list_display(self, request):
        """Enhanced list display"""
        list_display = super().get_list_display(request)
        if isinstance(list_display, tuple):
            list_display = list(list_display)
        return list_display


class SearchableModelAdmin(RobustModelAdmin):
    """Admin with enhanced search functionality"""

    def get_search_fields(self, request):
        return self.search_fields if self.search_fields else []


class FilteredModelAdmin(RobustModelAdmin):
    """Admin with standard filtering"""

    def get_list_filter(self, request):
        filters = super().get_list_filter(request) or []
        return list(filters) if not isinstance(filters, list) else filters


# ============================================================================
# DISPLAY HELPERS
# ============================================================================


def colored_status(status_value, status_map=None):
    """
    Return colored status display
    status_map: dict like {'available': 'green', 'checked_out': 'orange'}
    """
    if status_map is None:
        status_map = {
            "available": "#28a745",
            "checked_out": "#ffc107",
            "reserved": "#17a2b8",
            "lost": "#dc3545",
            "damaged": "#dc3545",
            "published": "#28a745",
            "draft": "#ffc107",
        }

    color = status_map.get(status_value, "#6c757d")
    return format_html(
        '<span style="background-color: {}; color: white; padding: 5px 10px; '
        'border-radius: 3px; font-weight: bold;">{}</span>',
        color,
        status_value.replace("_", " ").title(),
    )


def get_image_preview(image_url, max_width="100px", max_height="100px"):
    """Return formatted image preview"""
    if image_url:
        return format_html(
            '<img src="{}" style="max-width: {}; max-height: {}; border-radius: 5px; '
            'border: 1px solid #ddd; padding: 3px;" />',
            image_url,
            max_width,
            max_height,
        )
    return format_html('<span style="color: #ccc;">No image</span>')


def count_badge(count, label="items"):
    """Return formatted count badge"""
    return format_html(
        '<span style="background-color: #007bff; color: white; padding: 5px 10px; '
        'border-radius: 20px; font-weight: bold; display: inline-block;">{} {}</span>',
        count,
        label,
    )


# ============================================================================
# INLINES FOR NESTED EDITING
# ============================================================================


class ReadOnlyInline(admin.TabularInline):
    """Read-only inline for viewing related objects"""

    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class EditableInline(admin.TabularInline):
    """Editable inline for related objects"""

    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


# ============================================================================
# CUSTOM FIELDSETS FOR ORGANIZATION
# ============================================================================


def get_base_fieldsets(model_name):
    """Get standard fieldsets for common models"""
    fieldsets = {
        "book": (
            ("Basic Information", {"fields": ("title", "slug", "isbn", "isbn13")}),
            ("Metadata", {"fields": ("authors", "publisher", "genres", "language")}),
            (
                "Details",
                {
                    "fields": ("description", "publication_date", "edition", "pages"),
                    "classes": ("collapse",),
                },
            ),
            (
                "Media",
                {"fields": ("cover_image", "sample_pages"), "classes": ("collapse",)},
            ),
        ),
        "blog_post": (
            ("Basic Information", {"fields": ("title", "slug", "category", "author")}),
            ("Content", {"fields": ("excerpt", "content")}),
            ("Media", {"fields": ("featured_image",), "classes": ("collapse",)}),
            ("Settings", {"fields": ("is_featured", "is_published", "published_date")}),
        ),
    }
    return fieldsets.get(model_name, ())


# ============================================================================
# EXPORT/IMPORT SUPPORT (requires django-import-export)
# ============================================================================

try:
    from import_export.admin import ImportExportModelAdmin

    class ExportableAdmin(ImportExportModelAdmin, RobustModelAdmin):
        """Admin class with import/export functionality"""

        pass

except ImportError:

    class ExportableAdmin(RobustModelAdmin):
        """Fallback if import_export not installed"""

        pass


# ============================================================================
# NESTED ADMIN SUPPORT
# ============================================================================

try:
    import nested_admin

    class NestedTabularInline(nested_admin.NestedTabularInline):
        """Nested tabular inline"""

        extra = 0

    class NestedAdmin(nested_admin.NestedModelAdmin):
        """Admin with nested inline support"""

        pass

except ImportError:
    NestedAdmin = admin.ModelAdmin
    NestedTabularInline = admin.TabularInline


# ============================================================================
# DASHBOARD STATS MIXIN
# ============================================================================


class DashboardStatsMixin:
    """Mixin to add dashboard statistics to admin changeform"""

    def get_context_data(self, **kwargs):
        """Add stats to context"""
        context = super().get_context_data(**kwargs)
        context["stats"] = self.get_stats()
        return context

    def get_stats(self):
        """Override to provide custom stats"""
        return {}


# ============================================================================
# ADMIN SITE CUSTOMIZATION
# ============================================================================


class LibraryAdminSite(admin.AdminSite):
    """Custom admin site for Library Management"""

    site_header = "📚 University of Maiduguri Library Administration"
    site_title = "UNIMAID Library Admin"
    index_title = "Library Management Dashboard"

    def get_app_list(self, request):
        """Customize app order and appearance"""
        app_list = super().get_app_list(request)

        # Define desired order
        app_order = ["catalog", "core", "blog", "staff", "auth"]
        app_labels = [app["app_label"] for app in app_list]

        # Reorder
        new_list = []
        for app_label in app_order:
            if app_label in app_labels:
                app = next(a for a in app_list if a["app_label"] == app_label)
                new_list.append(app)

        # Add remaining apps
        for app in app_list:
            if app["app_label"] not in new_list:
                new_list.append(app)

        return new_list


# Create custom admin site instance
admin_site = LibraryAdminSite(name="librarian_admin")
