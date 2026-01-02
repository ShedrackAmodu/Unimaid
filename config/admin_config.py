from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.contrib.admin import SimpleListFilter, FieldListFilter
from django.utils.translation import gettext_lazy as _
import csv
from django.http import HttpResponse


class SearchableModelAdmin(admin.ModelAdmin):
    """Base admin with sensible defaults for searchable models."""

    def get_search_fields(self, request):
        return getattr(self, "search_fields", ())


class FilteredModelAdmin(admin.ModelAdmin):
    """Base admin that expects list_filter to be provided."""

    pass


class EditableInline(admin.TabularInline):
    """Enhanced inline with sensible defaults for editable inlines."""

    extra = 0
    can_delete = True
    show_change_link = True


class StatusFilter(SimpleListFilter):
    """Filter by status field with common status values."""

    title = _("Status")
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            ("active", _("Active")),
            ("inactive", _("Inactive")),
            ("pending", _("Pending")),
            ("completed", _("Completed")),
            ("cancelled", _("Cancelled")),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class RobustModelAdmin(admin.ModelAdmin):
    """Enhanced admin with export and date filtering capabilities."""

    def get_list_filter(self, request):
        return getattr(self, "list_filter", ())


class ExportableAdmin(admin.ModelAdmin):
    """Adds a generic CSV export action to an admin model."""

    actions = ["export_as_csv"]

    def export_as_csv(self, request, queryset):
        model = self.model
        meta = model._meta
        field_names = [f.name for f in meta.fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={meta.verbose_name_plural}.csv"

        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            row = [getattr(obj, f) for f in field_names]
            writer.writerow(row)

        return response

    export_as_csv.short_description = "Export selected as CSV"


def count_badge(count):
    return format_html('<span class="badge">{}</span>', count)


def get_image_preview(url, width="100px", height="100px"):
    if not url:
        return format_html('<span style="color: #ccc;">No image</span>')
    return format_html(
        '<img src="{}" style="width: {}; height: {}; object-fit: cover; border-radius: 4px;"/>'
        , url, width, height
    )


class DateRangeFilter(FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.field = field
        self.field_path = field_path
        super().__init__(field, request, params, model, model_admin, field_path)

        if self.field_path:
            self.parameter_name = f"{self.field_path}__daterange"
        else:
            self.parameter_name = "daterange"

    def expected_parameters(self):
        return [self.parameter_name]

    def choices(self, changelist):
        yield {
            'selected': self.lookup_val is None,
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
            'display': 'All',
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.lookup_val == lookup,
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'display': title,
            }

    @property
    def lookup_choices(self):
        return (
            ("today", "Today"),
            ("this_week", "This week"),
            ("this_month", "This month"),
            ("past", "Past"),
        )

    def queryset(self, request, queryset):
        value = self.lookup_val
        if not value:
            return queryset

        now = timezone.now()
        if value == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif value == "this_week":
            start = now - timezone.timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif value == "this_month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        else:
            # Past: anything older than this month
            start = None
            end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if start and end:
            return queryset.filter(**{f"{self.field_path}__range": (start, end)})
        elif end and not start:
            return queryset.filter(**{f"{self.field_path}__lt": end})

        return queryset


def colored_status(status, colors=None):
    """Helper function to create colored status badges."""
    if colors is None:
        colors = {
            'published': '#28a745',
            'draft': '#ffc107',
            'pending': '#17a2b8',
            'approved': '#28a745',
            'rejected': '#dc3545',
        }

    color = colors.get(status.lower(), '#6c757d')
    return format_html(
        '<span style="background-color: {}; color: white; padding: 3px 8px; '
        'border-radius: 3px; font-weight: bold; text-transform: capitalize;">{}</span>',
        color, status
    )


def mark_as_published(modeladmin, request, queryset):
    """Mark selected items as published."""
    count = queryset.update(status='published')
    modeladmin.message_user(request, f"{count} item(s) marked as published.")


def mark_as_draft(modeladmin, request, queryset):
    """Mark selected items as draft."""
    count = queryset.update(status='draft')
    modeladmin.message_user(request, f"{count} item(s) marked as draft.")


def mark_as_featured(modeladmin, request, queryset):
    """Mark selected posts as featured."""
    count = queryset.update(is_featured=True)
    modeladmin.message_user(request, f"{count} post(s) marked as featured.")


def mark_as_not_featured(modeladmin, request, queryset):
    """Remove featured status from selected posts."""
    count = queryset.update(is_featured=False)
    modeladmin.message_user(request, f"{count} post(s) removed from featured.")
