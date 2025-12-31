from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from library.utils import paginate_queryset
from .models import Post, Category, Comment


def post_list(request):
    """Display list of blog posts with pagination"""
    posts = Post.objects.filter(is_featured=False).order_by("-published_date")
    featured_posts = Post.objects.filter(is_featured=True).order_by("-published_date")[
        :3
    ]
    categories = Category.objects.all()

    posts_page = paginate_queryset(posts, request.GET.get("page"), per_page=6)

    context = {
        "posts": posts_page,
        "featured_posts": featured_posts,
        "categories": categories,
        "page_title": "Library News & Announcements",
    }
    return render(request, "blog/post_list.html", context)


def post_detail(request, slug):
    """Display individual blog post with comments"""
    post = get_object_or_404(Post, slug=slug)
    categories = Category.objects.all()
    recent_posts = Post.objects.exclude(id=post.id).order_by("-published_date")[:5]

    # Get related posts (same category, excluding current post)
    related_posts = (
        Post.objects.filter(category=post.category)
        .exclude(id=post.id)
        .order_by("-published_date")[:3]
    )

    context = {
        "post": post,
        "related_posts": related_posts,
        "comments": post.comments.all(),
        "categories": categories,
        "recent_posts": recent_posts,
        "page_title": post.title,
    }
    return render(request, "blog/post_detail.html", context)


def category_posts(request, slug):
    """Display posts for a specific category"""
    category = get_object_or_404(Category, slug=slug)
    posts = category.posts.all().order_by("-published_date")
    categories = Category.objects.all()

    posts_page = paginate_queryset(posts, request.GET.get("page"), per_page=6)

    context = {
        "category": category,
        "posts": posts_page,
        "categories": categories,
        "page_title": f"{category.name} - Library News",
    }
    return render(request, "blog/category_posts.html", context)


def blog_search(request):
    """Search blog posts"""
    query = request.GET.get("q", "")
    posts = Post.objects.all().order_by("-published_date")
    categories = Category.objects.all()

    if query:
        posts = posts.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(author__icontains=query)
        )

    posts_page = paginate_queryset(posts, request.GET.get("page"), per_page=6)

    context = {
        "posts": posts_page,
        "query": query,
        "categories": categories,
        "page_title": f"Search Results: {query}" if query else "Blog Search",
    }
    return render(request, "blog/search.html", context)
