from django.urls import path
from . import views

app_name = "staff"

urlpatterns = [
    path("", views.staff_list, name="staff_list"),
    path("<int:pk>/", views.staff_detail, name="staff_detail"),
]
