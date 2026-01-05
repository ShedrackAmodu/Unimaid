from django.contrib import admin
from .models import Category, Tag, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'is_featured', 'published_date', 'view_count', 'created_at']
    list_filter = ['is_published', 'is_featured', 'category', 'published_date', 'created_at']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    filter_horizontal = ['tags']
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'author', 'category', 'tags', 'content', 'excerpt', 'featured_image')
        }),
        ('Status', {
            'fields': ('is_published', 'is_featured', 'published_date')
        }),
        ('Statistics', {
            'fields': ('view_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'is_approved', 'is_moderated', 'created_at']
    list_filter = ['is_approved', 'is_moderated', 'created_at']
    search_fields = ['content', 'author__username', 'post__title']
    raw_id_fields = ['post', 'author', 'parent']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
