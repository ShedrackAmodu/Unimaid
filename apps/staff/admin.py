from django.contrib import admin
from .models import StaffMember


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'email', 'phone', 'order']
    list_editable = ['order']
    search_fields = ['name', 'position', 'email']
    ordering = ['order', 'name']
