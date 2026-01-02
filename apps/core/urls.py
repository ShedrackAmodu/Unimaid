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
    path("letitbe/", views.letitbe_admin, name="letitbe_admin"),
    path("letitbe/content/", views.letitbe_content, name="letitbe_content"),
    path("letitbe/repository/", views.letitbe_repository, name="letitbe_repository"),
    path("letitbe/events/", views.letitbe_events, name="letitbe_events"),
    path("letitbe/divisions/", views.letitbe_divisions, name="letitbe_divisions"),
    path("letitbe/users/", views.letitbe_users, name="letitbe_users"),
    path("letitbe/staff/", views.letitbe_staff, name="letitbe_staff"),
    path("letitbe/contacts/", views.letitbe_contacts, name="letitbe_contacts"),
    path("letitbe/subscribers/", views.letitbe_subscribers, name="letitbe_subscribers"),
]
