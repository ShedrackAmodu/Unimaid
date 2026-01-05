from django.contrib import admin
from .models import Genre, Publisher, Author, Book, Copy


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'website', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'middle_name', 'nationality', 'date_of_birth']
    list_filter = ['nationality', 'date_of_birth']
    search_fields = ['first_name', 'last_name', 'middle_name']
    ordering = ['last_name', 'first_name']


class CopyInline(admin.TabularInline):
    model = Copy
    extra = 0
    fields = ['barcode', 'status', 'location', 'condition']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'isbn', 'publisher', 'genre', 'total_copies', 'available_copies', 'is_featured', 'is_active', 'created_at']
    list_filter = ['genre', 'publisher', 'is_featured', 'is_active', 'language', 'created_at']
    search_fields = ['title', 'isbn', 'isbn13', 'authors__first_name', 'authors__last_name', 'description']
    filter_horizontal = ['authors']
    prepopulated_fields = {}
    inlines = [CopyInline]
    readonly_fields = ['total_copies', 'available_copies', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'isbn', 'isbn13', 'authors', 'publisher', 'genre')
        }),
        ('Publication Details', {
            'fields': ('publication_date', 'edition', 'language', 'pages', 'description')
        }),
        ('Cataloging', {
            'fields': ('location', 'call_number', 'subject_heading', 'keywords')
        }),
        ('Media', {
            'fields': ('cover_image', 'qr_code')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active', 'total_copies', 'available_copies')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Copy)
class CopyAdmin(admin.ModelAdmin):
    list_display = ['book', 'barcode', 'status', 'location', 'condition', 'created_at']
    list_filter = ['status', 'condition', 'created_at']
    search_fields = ['barcode', 'book__title', 'book__isbn']
    raw_id_fields = ['book']
