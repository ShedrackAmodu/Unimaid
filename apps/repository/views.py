from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.conf import settings
import os
from config.utils import paginate_queryset

from .models import Document


def document_list(request):
    """List documents with optional search and pagination."""
    q = request.GET.get("q", "").strip()
    docs = Document.objects.filter(is_public=True).order_by("-uploaded_at")

    if q:
        docs = docs.filter(title__icontains=q) | docs.filter(description__icontains=q)

    documents = paginate_queryset(docs, request.GET.get("page"), per_page=10)

    context = {"documents": documents, "query": q}
    return render(request, "repository/list.html", context)


def document_detail(request, slug):
    doc = get_object_or_404(Document, slug=slug, is_public=True)
    context = {"doc": doc}
    return render(request, "repository/detail.html", context)


def document_download(request, slug):
    """Serve file through Django after permission checks.

    - Only serves files for documents marked `is_public=True`.
    - In future this can be extended to require login or signed URLs.
    """
    doc = get_object_or_404(Document, slug=slug)

    # Only allow download if public (change to request.user.has_perm... to restrict)
    if not doc.is_public:
        return HttpResponseForbidden("You don't have permission to download this file.")

    file_path = doc.file.path
    if not os.path.exists(file_path):
        raise Http404("File not found")

    filename = os.path.basename(file_path)
    response = FileResponse(
        open(file_path, "rb"), as_attachment=True, filename=filename
    )
    return response
