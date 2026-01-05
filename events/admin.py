from django.contrib import admin
from .models import Event, EventRegistration


class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0
    readonly_fields = ['registration_date', 'confirmation_date']
    fields = ['user', 'is_confirmed', 'is_attended', 'payment_status', 'registration_date']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_date', 'end_date', 'location', 'is_published', 'is_featured', 'is_cancelled', 'capacity']
    list_filter = ['event_type', 'is_published', 'is_featured', 'is_cancelled', 'requires_registration', 'start_date']
    search_fields = ['title', 'description', 'location', 'organizer_name']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['organizer']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
    inlines = [EventRegistrationInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'event_type', 'featured_image')
        }),
        ('Date and Time', {
            'fields': ('start_date', 'end_date', 'registration_deadline')
        }),
        ('Location', {
            'fields': ('location', 'venue', 'is_online', 'online_link')
        }),
        ('Registration', {
            'fields': ('requires_registration', 'capacity', 'registration_fee')
        }),
        ('Organizer', {
            'fields': ('organizer', 'organizer_name', 'contact_email', 'contact_phone')
        }),
        ('Status', {
            'fields': ('is_published', 'is_featured', 'is_cancelled')
        }),
        ('Additional', {
            'fields': ('tags', 'created_at', 'updated_at')
        }),
    )


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'is_confirmed', 'is_attended', 'payment_status', 'registration_date']
    list_filter = ['is_confirmed', 'is_attended', 'payment_status', 'registration_date']
    search_fields = ['user__username', 'event__title', 'payment_reference']
    raw_id_fields = ['event', 'user']
    readonly_fields = ['registration_date', 'confirmation_date', 'attendance_date', 'created_at', 'updated_at']
    date_hierarchy = 'registration_date'
