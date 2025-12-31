from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Blog post categories"""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"slug": self.slug})


class Post(models.Model):
    """Blog posts"""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    author = models.CharField(max_length=100, default="Library Staff")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="posts"
    )
    featured_image = models.ImageField(upload_to="blog/", blank=True, null=True)
    published_date = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["-published_date"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.slug})


class Comment(models.Model):
    """Blog post comments"""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ["created_date"]

    def __str__(self):
        return f"Comment by {self.author_name} on {self.post.title}"
