from django.contrib import admin
from .models import Loan, Reservation, Fine


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'copy', 'checkout_date', 'due_date', 'return_date', 'status', 'renewed_count']
    list_filter = ['status', 'checkout_date', 'due_date', 'return_date']
    search_fields = ['user__username', 'book__title', 'book__isbn', 'copy__barcode']
    raw_id_fields = ['user', 'copy', 'book', 'checked_out_by', 'returned_to']
    readonly_fields = ['checkout_date', 'created_at', 'updated_at']
    date_hierarchy = 'checkout_date'
    
    fieldsets = (
        ('Loan Information', {
            'fields': ('user', 'book', 'copy', 'status')
        }),
        ('Dates', {
            'fields': ('checkout_date', 'due_date', 'return_date')
        }),
        ('Renewal Information', {
            'fields': ('renewed_count', 'max_renewals')
        }),
        ('Staff Information', {
            'fields': ('checked_out_by', 'returned_to')
        }),
        ('Additional', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'status', 'queue_position', 'reserved_date', 'notification_sent']
    list_filter = ['status', 'reserved_date', 'notification_sent']
    search_fields = ['user__username', 'book__title', 'book__isbn']
    raw_id_fields = ['user', 'book']
    readonly_fields = ['reserved_date', 'created_at', 'updated_at']
    date_hierarchy = 'reserved_date'


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ['user', 'loan', 'amount', 'status', 'due_date', 'paid_date']
    list_filter = ['status', 'due_date', 'paid_date']
    search_fields = ['user__username', 'loan__book__title', 'transaction_id']
    raw_id_fields = ['user', 'loan', 'waived_by']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'due_date'
