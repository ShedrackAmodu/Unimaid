from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Post, Category, Tag, Comment
from analytics.models import UserActivity


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(is_published=True).order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_posts'] = Post.objects.filter(is_published=True, is_featured=True)[:3]
        context['categories'] = Category.objects.filter(is_active=True)
        context['recent_posts'] = Post.objects.filter(is_published=True)[:5]
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Post.objects.filter(is_published=True)
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        post = self.get_object()
        
        # Increment view count
        post.increment_view_count()
        
        # Log activity
        if request.user.is_authenticated:
            UserActivity.objects.create(
                user=request.user,
                action_type='view_book',
                description=f'Viewed blog post: {post.title}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comments'] = Comment.objects.filter(post=post, is_approved=True, parent=None).order_by('-created_at')
        context['related_posts'] = Post.objects.filter(
            category=post.category,
            is_published=True
        ).exclude(pk=post.pk)[:3]
        return context


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'blog/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(
            category=self.object,
            is_published=True
        ).order_by('-published_date')
        return context


class TagDetailView(DetailView):
    model = Tag
    template_name = 'blog/tag_detail.html'
    context_object_name = 'tag'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object.posts.filter(is_published=True).order_by('-published_date')
        return context
