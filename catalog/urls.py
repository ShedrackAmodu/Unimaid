from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    # Public catalog views
    path("", views.catalog_home, name="home"),
    path("search/", views.search, name="search"),
    path("book/<slug:slug>/", views.book_detail, name="book_detail"),
    path("author/<int:pk>/", views.author_detail, name="author_detail"),
    path("genre/<slug:slug>/", views.genre_detail, name="genre_detail"),
    # Patron registration and authentication
    path("register/", views.patron_register, name="register"),
    path("login/", views.patron_login, name="login"),
    path("logout/", views.patron_logout, name="logout"),
    # Patron dashboard and profile
    path("dashboard/", views.patron_dashboard, name="dashboard"),
    path("profile/", views.patron_profile, name="profile"),
    # Circulation (requires login)
    path("loan/<int:book_copy_id>/", views.create_loan, name="create_loan"),
    path("return/<int:book_copy_id>/", views.return_book, name="return_book"),
    path("reserve/<int:book_id>/", views.create_reservation, name="create_reservation"),
    path(
        "reservation/<int:pk>/cancel/",
        views.cancel_reservation,
        name="cancel_reservation",
    ),
    # Bulk operations (staff only)
    path("bulk-checkout/", views.bulk_checkout, name="bulk_checkout"),
    path("bulk-checkin/", views.bulk_checkin, name="bulk_checkin"),
    # Staff-only views (require staff permission)
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
    path("staff/books/add/", views.add_book, name="add_book"),
    path("staff/books/<int:pk>/edit/", views.edit_book, name="edit_book"),
    path("staff/books/<int:pk>/copies/add/", views.add_book_copy, name="add_book_copy"),
    path("staff/authors/add/", views.add_author, name="add_author"),
    path("staff/publishers/add/", views.add_publisher, name="add_publisher"),
    path("staff/genres/add/", views.add_genre, name="add_genre"),
    # Circulation management (staff)
    path(
        "staff/circulation/", views.circulation_dashboard, name="circulation_dashboard"
    ),
    path("staff/loans/", views.loan_list, name="loan_list"),
    path("staff/loans/overdue/", views.overdue_loans, name="overdue_loans"),
    path("staff/reservations/", views.reservation_list, name="reservation_list"),
    # API endpoints
    path("api/books/", views.BookListAPIView.as_view(), name="api_book_list"),
    path(
        "api/books/<int:pk>/", views.BookDetailAPIView.as_view(), name="api_book_detail"
    ),
    path("api/loans/", views.LoanListAPIView.as_view(), name="api_loan_list"),
    # Autocomplete endpoints
    path("api/autocomplete/books/", views.book_autocomplete, name="book_autocomplete"),
    path(
        "api/autocomplete/authors/",
        views.author_autocomplete,
        name="author_autocomplete",
    ),
    path(
        "api/autocomplete/genres/", views.genre_autocomplete, name="genre_autocomplete"
    ),
    path(
        "api/autocomplete/publishers/",
        views.publisher_autocomplete,
        name="publisher_autocomplete",
    ),
]
