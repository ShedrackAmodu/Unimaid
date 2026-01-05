from django.contrib import admin
from .models import Metric, Report, UserActivity, SearchQuery


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ['name', 'metric_type', 'value', 'unit', 'date', 'created_at']
    list_filter = ['metric_type', 'date', 'created_at']
    search_fields = ['name']
    date_hierarchy = 'date'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'generated_by', 'generated_date', 'is_archived']
    list_filter = ['report_type', 'is_archived', 'generated_date']
    search_fields = ['title', 'description']
    raw_id_fields = ['generated_by']
    readonly_fields = ['generated_date']
    date_hierarchy = 'generated_date'


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'description', 'ip_address', 'created_at']
    list_filter = ['action_type', 'created_at']
    search_fields = ['user__username', 'description', 'ip_address']
    raw_id_fields = ['user']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'user', 'search_type', 'result_count', 'created_at']
    list_filter = ['search_type', 'created_at']
    search_fields = ['query', 'user__username']
    raw_id_fields = ['user']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
