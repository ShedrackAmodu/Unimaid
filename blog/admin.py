from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from library.admin_config import (
    SearchableModelAdmin,
    FilteredModelAdmin,
    colored_status,
    count_badge,
    get_image_preview,
    DateRangeFilter,
    ExportableAdmin,
    mark_as_published,
    mark_as_draft,
    mark_as_featured,
    mark_as_not_featured,
)
from .models import Category, Post, Comment


# ============================================================================
# CATEGORY ADMIN
# ============================================================================


@admin.register(Category)
class CategoryAdmin(SearchableModelAdmin):
    list_display = ("name", "post_count_badge", "description_preview")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)

    fieldsets = (("Basic Information", {"fields": ("name", "slug", "description")}),)

    def post_count_badge(self, obj):
        count = obj.posts.count()
        return count_badge(count, "posts")

    post_count_badge.short_description = "Posts"

    def description_preview(self, obj):
        if obj.description and len(obj.description) > 50:
            return obj.description[:50] + "..."
        return obj.description or "—"

    description_preview.short_description = "Description"


# ============================================================================
# COMMENT INLINE
# ============================================================================


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("author_name", "created_date", "comment_text_preview")
    can_delete = True
    fields = ("author_name", "comment_text_preview", "created_date", "is_approved")

    def comment_text_preview(self, obj):
        text = obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
        return text

    comment_text_preview.short_description = "Comment"


# ============================================================================
# POST ADMIN
# ============================================================================


@admin.register(Post)
class PostAdmin(ExportableAdmin):
    list_display = (
        "post_title_with_image",
        "category",
        "author",
        "status_with_featured",
        "comment_count_badge",
        "published_date_display",
    )
    list_filter = (
        "category",
        ("is_featured", admin.BooleanFieldListFilter),
        ("published_date", DateRangeFilter),
        "author",
    )
    search_fields = ("title", "content", "excerpt", "author")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-published_date",)
    list_editable = ("author",)
    date_hierarchy = "published_date"
    list_per_page = 50

    inlines = [CommentInline]

    readonly_fields = (
        "published_date",
        "featured_image_preview",
        "content_preview",
    )

    fieldsets = (
        ("Post Information", {"fields": ("title", "slug", "category", "author")}),
        (
            "Content",
            {"fields": ("excerpt", "content", "content_preview"), "classes": ("wide",)},
        ),
        (
            "Media",
            {
                "fields": ("featured_image_preview", "featured_image"),
                "classes": ("collapse",),
            },
        ),
        (
            "Publishing",
            {
                "fields": ("is_featured", "published_date"),
            },
        ),
    )

    actions = [
        mark_as_featured,
        mark_as_not_featured,
        "export_as_csv",
    ]

    def post_title_with_image(self, obj):
        title = format_html("<strong>{}</strong>", obj.title)
        if obj.featured_image:
            img_html = get_image_preview(obj.featured_image.url, "60px", "40px")
            return format_html(
                '<div style="display: flex; gap: 10px; align-items: center;">'
                "{}{}</div>",
                img_html,
                title,
            )
        return title

    post_title_with_image.short_description = "Post"

    def status_with_featured(self, obj):
        if obj.is_featured:
            return format_html(
                '<span style="background-color: #FFD700; color: black; padding: 5px 10px; '
                'border-radius: 3px; font-weight: bold;">⭐ Featured</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 5px 10px; '
                'border-radius: 3px; font-weight: bold;">✓ Published</span>'
            )

    status_with_featured.short_description = "Status"

    def comment_count_badge(self, obj):
        count = obj.comments.count()
        return count_badge(count, "comments")

    comment_count_badge.short_description = "Comments"

    def published_date_display(self, obj):
        return obj.published_date.strftime("%b %d, %Y %H:%M")

    published_date_display.short_description = "Published"

    def featured_image_preview(self, obj):
        if obj.featured_image:
            return get_image_preview(obj.featured_image.url, "300px", "200px")
        return format_html('<span style="color: #ccc;">No featured image</span>')

    featured_image_preview.short_description = "Featured Image Preview"

    def content_preview(self, obj):
        content = obj.content[:200] + "..." if len(obj.content) > 200 else obj.content
        return format_html(
            '<div style="background: #f5f5f5; padding: 10px; border-radius: 3px; '
            'max-height: 150px; overflow-y: auto;">{}</div>',
            content,
        )

    content_preview.short_description = "Content Preview"

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="blog_posts.csv"'
        writer = csv.writer(response)
        writer.writerow(
            ["Title", "Category", "Author", "Featured", "Comments", "Published"]
        )

        for post in queryset:
            writer.writerow(
                [
                    post.title,
                    post.category.name,
                    post.author,
                    "Yes" if post.is_featured else "No",
                    post.comments.count(),
                    post.published_date.strftime("%Y-%m-%d %H:%M"),
                ]
            )

        return response

    export_as_csv.short_description = "📥 Export selected posts as CSV"


# ============================================================================
# COMMENT ADMIN
# ============================================================================


@admin.register(Comment)
class CommentAdmin(FilteredModelAdmin):
    list_display = (
        "author_name",
        "post_link",
        "comment_preview",
        "is_approved",
        "approval_status",
        "created_date_display",
    )
    search_fields = ("author_name", "content", "post__title")
    list_filter = (
        ("is_approved", admin.BooleanFieldListFilter),
        ("created_date", DateRangeFilter),
    )
    readonly_fields = ("created_date", "author_name", "post", "full_comment_display")
    date_hierarchy = "created_date"
    list_per_page = 100
    list_editable = ("is_approved",)

    actions = ["approve_comments", "reject_comments"]

    fieldsets = (
        (
            "Comment Information",
            {"fields": ("post", "author_name", "full_comment_display")},
        ),
        (
            "Status",
            {
                "fields": ("is_approved", "created_date"),
            },
        ),
    )

    def post_link(self, obj):
        return format_html(
            '<a href="/admin/blog/post/{}/change/">{}</a>',
            obj.post.id,
            obj.post.title[:40],
        )

    post_link.short_description = "Post"

    def comment_preview(self, obj):
        text = obj.content[:60] + "..." if len(obj.content) > 60 else obj.content
        return format_html(
            '<div style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">{}</div>',
            text,
        )

    comment_preview.short_description = "Comment"

    def approval_status(self, obj):
        if obj.is_approved:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-weight: bold;">✓ Approved</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 8px; '
                'border-radius: 3px; font-weight: bold;">⏳ Pending</span>'
            )

    approval_status.short_description = "Status"

    def created_date_display(self, obj):
        return obj.created_date.strftime("%b %d, %Y %H:%M")

    created_date_display.short_description = "Created"

    def full_comment_display(self, obj):
        return format_html(
            '<div style="background: #f5f5f5; padding: 10px; border-radius: 3px; '
            'max-height: 200px; overflow-y: auto;">{}</div>',
            obj.content,
        )

    full_comment_display.short_description = "Full Comment"

    def approve_comments(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f"{count} comment(s) approved.")

    approve_comments.short_description = "✓ Approve selected comments"

    def reject_comments(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f"{count} comment(s) rejected.")

    reject_comments.short_description = "✗ Reject selected comments"
