from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("contact/", views.contact, name="contact"),
    path("about/", views.about, name="about"),
    path(
        "library-organization/", views.library_organization, name="library_organization"
    ),
    path("search/", views.search, name="search"),
    path("admissions/", views.admissions, name="admissions"),
    path("courses/", views.courses, name="courses"),
    path("events/", views.events, name="events"),
    path("events/<int:pk>/", views.event_detail, name="event_detail"),
    path("events/create/", views.event_create, name="event_create"),
    path("events/<int:pk>/edit/", views.event_update, name="event_update"),
    path("events/<int:pk>/delete/", views.event_delete, name="event_delete"),
    path("history/", views.history, name="history"),
    path("divisions/<slug:slug>/", views.division_detail, name="division_detail"),
]
