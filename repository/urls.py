from django.urls import path
from . import views

app_name = "repository"

urlpatterns = [
    path("", views.document_list, name="doc_list"),
    path("download/<slug:slug>/", views.document_download, name="doc_download"),
    path("<slug:slug>/", views.document_detail, name="doc_detail"),
]
