from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import Document, Collection
from analytics.models import UserActivity


class DocumentListView(ListView):
    model = Document
    template_name = 'repository/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Document.objects.filter(is_active=True, is_approved=True)
        
        # Filter by document type
        doc_type = self.request.GET.get('type')
        if doc_type:
            queryset = queryset.filter(document_type=doc_type)
        
        # Filter by collection
        collection_slug = self.request.GET.get('collection')
        if collection_slug:
            queryset = queryset.filter(collection__slug=collection_slug)
        
        # Filter by department
        department = self.request.GET.get('department')
        if department:
            queryset = queryset.filter(department=department)
        
        # Filter by year
        year = self.request.GET.get('year')
        if year:
            queryset = queryset.filter(year=year)
        
        return queryset.order_by('-submission_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collections'] = Collection.objects.filter(is_active=True)
        context['document_types'] = Document.DOCUMENT_TYPES
        # Get unique years from documents
        years = Document.objects.filter(is_active=True, is_approved=True, year__isnull=False).values_list('year', flat=True).distinct().order_by('-year')
        context['years'] = sorted(set(years), reverse=True)[:10]  # Last 10 years
        return context


class DocumentDetailView(DetailView):
    model = Document
    template_name = 'repository/document_detail.html'
    context_object_name = 'document'
    
    def get_queryset(self):
        return Document.objects.filter(is_active=True, is_approved=True)
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        document = self.get_object()
        
        # Check access
        if not document.is_accessible(request.user):
            from django.contrib import messages
            messages.error(request, 'You do not have access to this document.')
            from django.shortcuts import redirect
            return redirect('repository:document_list')
        
        # Increment view count
        document.increment_view_count()
        
        # Log activity
        if request.user.is_authenticated:
            UserActivity.objects.create(
                user=request.user,
                action_type='view_document',
                description=f'Viewed document: {document.title}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_documents'] = Document.objects.filter(
            collection=self.object.collection,
            is_active=True,
            is_approved=True
        ).exclude(pk=self.object.pk)[:5]
        return context


class CollectionDetailView(DetailView):
    model = Collection
    template_name = 'repository/collection_detail.html'
    context_object_name = 'collection'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = Document.objects.filter(
            collection=self.object,
            is_active=True,
            is_approved=True
        ).order_by('-submission_date')
        return context


class DocumentSearchView(ListView):
    model = Document
    template_name = 'repository/document_search.html'
    context_object_name = 'documents'
    paginate_by = 20
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Document.objects.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(abstract__icontains=query) |
                Q(keywords__icontains=query) |
                Q(subject__icontains=query)
            ).filter(is_active=True, is_approved=True).distinct()
        return Document.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context
