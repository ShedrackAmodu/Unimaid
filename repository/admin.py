from django.contrib import admin
from .models import Collection, Document


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'display_order', 'created_at']
    list_filter = ['is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'display_order']
    search_fields = ['name', 'description']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'author', 'department', 'year', 'access_level', 'is_approved', 'is_active', 'submission_date']
    list_filter = ['document_type', 'access_level', 'is_approved', 'is_active', 'is_featured', 'year', 'department', 'submission_date']
    search_fields = ['title', 'author', 'abstract', 'keywords', 'doi', 'isbn']
    raw_id_fields = ['submitted_by', 'reviewed_by', 'authors']
    filter_horizontal = ['authors']
    readonly_fields = ['submission_date', 'download_count', 'view_count', 'created_at', 'updated_at']
    date_hierarchy = 'submission_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'document_type', 'collection')
        }),
        ('Authorship', {
            'fields': ('author', 'authors', 'department', 'faculty', 'supervisor')
        }),
        ('Publication Information', {
            'fields': ('publication_date', 'year', 'publisher', 'journal_name', 'volume', 'issue', 'pages')
        }),
        ('File and Access', {
            'fields': ('file', 'file_size', 'thumbnail', 'access_level', 'embargo_date')
        }),
        ('Metadata (Dublin Core)', {
            'fields': ('abstract', 'keywords', 'subject', 'language', 'doi', 'isbn', 'issn')
        }),
        ('Rights and Licensing', {
            'fields': ('license', 'copyright_holder', 'rights_statement')
        }),
        ('Submission Information', {
            'fields': ('submitted_by', 'submission_date', 'reviewed_by', 'review_date', 'is_approved')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
        ('Statistics', {
            'fields': ('download_count', 'view_count')
        }),
        ('Additional', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
