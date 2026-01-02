from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count, F, Avg
from django.utils import timezone
from datetime import timedelta
from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import (
    Book,
    BookCopy,
    Author,
    Publisher,
    Genre,
    Patron,
    Loan,
    Reservation,
    Fine,
    Visitor,
    ELibrarySession,
)
from .forms import (
    PatronRegistrationForm,
    BookForm,
    AuthorForm,
    PublisherForm,
    GenreForm,
    BookCopyForm,
    LoanForm,
    ReturnForm,
    ReservationForm,
    SearchForm,
    PatronProfileForm,
    FinePaymentForm,
    ELibraryCheckInForm,
    ELibraryCheckOutForm,
)
from .serializers import BookSerializer, LoanSerializer
from config.utils import paginate_queryset


def catalog_home(request):
    """Catalog home page - shows featured books and search"""
    featured_books = (
        Book.objects.filter(copies__status="available")
        .distinct()
        .order_by("-date_added")[:12]
    )

    recent_books = Book.objects.order_by("-date_added")[:8]
    popular_genres = Genre.objects.annotate(book_count=Count("books")).order_by(
        "-book_count"
    )[:6]

    context = {
        "featured_books": featured_books,
        "recent_books": recent_books,
        "popular_genres": popular_genres,
    }
    return render(request, "catalog/home.html", context)


def search(request):
    """Enhanced advanced search functionality with faceted filters"""
    form = SearchForm(request.GET or None)
    books = Book.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get("query")
        author = form.cleaned_data.get("author")
        genre = form.cleaned_data.get("genre")
        publisher = form.cleaned_data.get("publisher")
        language = form.cleaned_data.get("language")
        availability = form.cleaned_data.get("availability")
        pub_year_from = form.cleaned_data.get("pub_year_from")
        pub_year_to = form.cleaned_data.get("pub_year_to")
        pages_from = form.cleaned_data.get("pages_from")
        pages_to = form.cleaned_data.get("pages_to")
        format_type = form.cleaned_data.get("format_type")
        sort_by = form.cleaned_data.get("sort_by")

        # Text search with relevance scoring
        if query:
            books = books.filter(
                Q(title__icontains=query)
                | Q(isbn__icontains=query)
                | Q(isbn13__icontains=query)
                | Q(authors__first_name__icontains=query)
                | Q(authors__last_name__icontains=query)
                | Q(description__icontains=query)
                | Q(publisher__name__icontains=query)
                | Q(genres__name__icontains=query)
            ).distinct()

        # Faceted filters
        if author:
            books = books.filter(authors=author)

        if genre:
            books = books.filter(genres=genre)

        if publisher:
            books = books.filter(publisher=publisher)

        if language:
            books = books.filter(language=language)

        # Publication year range
        if pub_year_from:
            books = books.filter(publication_date__year__gte=pub_year_from)
        if pub_year_to:
            books = books.filter(publication_date__year__lte=pub_year_to)

        # Page count range
        if pages_from:
            books = books.filter(pages__gte=pages_from)
        if pages_to:
            books = books.filter(pages__lte=pages_to)

        # Availability filter
        if availability:
            if availability == "available":
                books = books.filter(copies__status="available").distinct()
            elif availability == "checked_out":
                books = books.filter(copies__status="checked_out").distinct()
            elif availability == "reserved":
                books = books.filter(copies__status="reserved").distinct()

        # Format filter (for future digital content)
        if format_type == "physical":
            books = books.filter(copies__isnull=False).distinct()
        elif format_type == "digital":
            # For future digital content - currently no digital books
            books = books.none()

        # Enhanced sorting options
        if sort_by == "relevance":
            # For now, sort by title for relevance (could be enhanced with search scoring)
            books = books.order_by("title")
        elif sort_by == "title":
            books = books.order_by("title")
        elif sort_by == "title_desc":
            books = books.order_by("-title")
        elif sort_by == "date_added":
            books = books.order_by("-date_added")
        elif sort_by == "publication_date":
            books = books.order_by("publication_date")
        elif sort_by == "publication_date_desc":
            books = books.order_by("-publication_date")
        elif sort_by == "author":
            books = books.order_by("authors__last_name", "authors__first_name")
        elif sort_by == "author_desc":
            books = books.order_by("-authors__last_name", "-authors__first_name")
        elif sort_by == "pages":
            books = books.order_by("pages")
        elif sort_by == "pages_desc":
            books = books.order_by("-pages")
        else:
            books = books.order_by("title")

    # Get search statistics for faceted navigation
    total_results = books.count()

    # Availability counts
    availability_stats = {
        "available": Book.objects.filter(
            id__in=books.values_list("id", flat=True), copies__status="available"
        )
        .distinct()
        .count(),
        "checked_out": Book.objects.filter(
            id__in=books.values_list("id", flat=True), copies__status="checked_out"
        )
        .distinct()
        .count(),
        "reserved": Book.objects.filter(
            id__in=books.values_list("id", flat=True), copies__status="reserved"
        )
        .distinct()
        .count(),
    }

    books_page = paginate_queryset(books, request.GET.get("page"))

    context = {
        "form": form,
        "books": books_page,
        "total_results": total_results,
        "availability_stats": availability_stats,
        "query": request.GET.get("query", ""),
    }
    return render(request, "catalog/search.html", context)


def book_detail(request, slug):
    """Book detail page"""
    book = get_object_or_404(Book, slug=slug)
    available_copies = book.copies.filter(status="available").count()

    # Check if user can reserve this book
    can_reserve = False
    if request.user.is_authenticated:
        try:
            patron = request.user.patron
            can_reserve = (
                patron.can_reserve
                and not Reservation.objects.filter(
                    patron=patron, book=book, status__in=["active", "ready"]
                ).exists()
            )
        except Patron.DoesNotExist:
            pass

    context = {
        "book": book,
        "available_copies": available_copies,
        "can_reserve": can_reserve,
    }
    return render(request, "catalog/book_detail.html", context)


def author_detail(request, pk):
    """Author detail page"""
    author = get_object_or_404(Author, pk=pk)
    books = author.books.all().order_by("title")
    books_page = paginate_queryset(books, request.GET.get("page"))

    context = {
        "author": author,
        "books": books_page,
    }
    return render(request, "catalog/author_detail.html", context)


def genre_detail(request, slug):
    """Genre detail page"""
    genre = get_object_or_404(Genre, slug=slug)
    books = genre.books.all().order_by("title")
    books_page = paginate_queryset(books, request.GET.get("page"))

    context = {
        "genre": genre,
        "books": books_page,
    }
    return render(request, "catalog/genre_detail.html", context)


# Authentication views
def patron_register(request):
    """Patron registration"""
    if request.method == "POST":
        form = PatronRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, "Registration successful! Welcome to the library."
            )
            return redirect("catalog:dashboard")
    else:
        form = PatronRegistrationForm()

    return render(request, "catalog/register.html", {"form": form})


def patron_login(request):
    """Patron login"""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get("next", "catalog:dashboard")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "catalog/login.html")


def patron_logout(request):
    """Patron logout"""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("core:home")


# Patron dashboard and profile
@login_required
def patron_dashboard(request):
    """Patron dashboard"""
    try:
        patron = request.user.patron
    except Patron.DoesNotExist:
        messages.error(
            request, "Your patron profile is not set up. Please contact library staff."
        )
        return redirect("core:home")

    current_loans = patron.loans.filter(
        status="active", returned_date__isnull=True
    ).select_related("book_copy__book")

    overdue_loans = current_loans.filter(due_date__lt=timezone.now())

    active_reservations = patron.reservations.filter(
        status__in=["active", "ready"]
    ).select_related("book")

    recent_history = (
        patron.loans.filter(returned_date__isnull=False)
        .select_related("book_copy__book")
        .order_by("-returned_date")[:5]
    )

    context = {
        "patron": patron,
        "current_loans": current_loans,
        "overdue_loans": overdue_loans,
        "active_reservations": active_reservations,
        "recent_history": recent_history,
    }
    return render(request, "catalog/dashboard.html", context)


@login_required
def patron_profile(request):
    """Patron profile management"""
    try:
        patron = request.user.patron
    except Patron.DoesNotExist:
        messages.error(request, "Your patron profile is not set up.")
        return redirect("catalog:profile")

    if request.method == "POST":
        form = PatronProfileForm(request.POST, instance=patron)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("catalog:profile")
    else:
        form = PatronProfileForm(instance=patron)

    return render(request, "catalog/profile.html", {"form": form})


@login_required
def borrowed_items(request):
    """List all borrowed items for the patron"""
    try:
        patron = request.user.patron
    except Patron.DoesNotExist:
        messages.error(
            request, "Your patron profile is not set up. Please contact library staff."
        )
        return redirect("core:home")

    # Get all loans for this patron
    loans = patron.loans.select_related("book_copy__book").order_by("-loan_date")

    # Separate current and historical loans
    current_loans = loans.filter(status="active", returned_date__isnull=True)
    historical_loans = loans.filter(status="returned")

    context = {
        "patron": patron,
        "current_loans": current_loans,
        "historical_loans": historical_loans,
        "total_loans": loans.count(),
    }
    return render(request, "catalog/borrowed.html", context)


@login_required
def patron_reservations(request):
    """List all reservations for the patron"""
    try:
        patron = request.user.patron
    except Patron.DoesNotExist:
        messages.error(
            request, "Your patron profile is not set up. Please contact library staff."
        )
        return redirect("core:home")

    # Get all reservations for this patron
    reservations = patron.reservations.select_related("book").order_by("-reservation_date")

    # Separate active and historical reservations
    active_reservations = reservations.filter(status__in=["active", "ready"])
    historical_reservations = reservations.filter(status__in=["completed", "cancelled", "expired"])

    context = {
        "patron": patron,
        "active_reservations": active_reservations,
        "historical_reservations": historical_reservations,
        "total_reservations": reservations.count(),
    }
    return render(request, "catalog/reservations.html", context)


# Circulation views
@login_required
def create_loan(request, book_copy_id):
    """Create a new loan"""
    book_copy = get_object_or_404(BookCopy, pk=book_copy_id, status="available")

    try:
        patron = request.user.patron
    except Patron.DoesNotExist:
        messages.error(request, "Your patron profile is not set up.")
        return redirect("catalog:book_detail", slug=book_copy.book.slug)

    # Check if patron can borrow more books
    current_loans = patron.loans.filter(
        status="active", returned_date__isnull=True
    ).count()
    if current_loans >= patron.max_books:
        messages.error(
            request,
            f"You have reached your maximum loan limit of {patron.max_books} books.",
        )
        return redirect("catalog:book_detail", slug=book_copy.book.slug)

    if request.method == "POST":
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.patron = patron
            loan.book_copy = book_copy
            loan.issued_by = request.user
            loan.save()

            # Update book copy status
            book_copy.status = "checked_out"
            book_copy.save()

            messages.success(
                request, f'Successfully borrowed "{book_copy.book.title}".'
            )
            return redirect("catalog:dashboard")
    else:
        form = LoanForm(initial={"patron": patron, "book_copy": book_copy})

    return render(
        request, "catalog/create_loan.html", {"form": form, "book_copy": book_copy}
    )


@login_required
def bulk_checkout(request):
    """Bulk checkout multiple books for a patron"""
    if not request.user.is_staff:
        messages.error(request, "Access denied. Staff privileges required.")
        return redirect("core:home")

    if request.method == "POST":
        patron_id = request.POST.get("patron")
        book_copy_ids = request.POST.getlist("book_copies")

        try:
            patron = Patron.objects.get(pk=patron_id)
        except Patron.DoesNotExist:
            messages.error(request, "Invalid patron selected.")
            return redirect("catalog:bulk_checkout")

        # Validate books
        book_copies = BookCopy.objects.filter(pk__in=book_copy_ids, status="available")

        if not book_copies.exists():
            messages.error(request, "No valid books selected for checkout.")
            return redirect("catalog:bulk_checkout")

        # Check patron limits
        current_loans = patron.loans.filter(
            status="active", returned_date__isnull=True
        ).count()

        if current_loans + len(book_copies) > patron.max_books:
            messages.error(
                request,
                f"Patron would exceed their limit of {patron.max_books} books. "
                f"Currently has {current_loans}, trying to add {len(book_copies)}.",
            )
            return redirect("catalog:bulk_checkout")

        # Process checkouts
        successful_checkouts = 0
        failed_checkouts = []

        for book_copy in book_copies:
            try:
                loan = Loan.objects.create(
                    patron=patron,
                    book_copy=book_copy,
                    issued_by=request.user,
                    status="active",
                )
                book_copy.status = "checked_out"
                book_copy.save()
                successful_checkouts += 1
            except Exception as e:
                failed_checkouts.append(f"{book_copy.book.title}: {str(e)}")

        if successful_checkouts > 0:
            messages.success(
                request,
                f"Successfully checked out {successful_checkouts} book(s) to {patron}.",
            )

        if failed_checkouts:
            messages.warning(
                request,
                f"Failed to checkout {len(failed_checkouts)} book(s): {', '.join(failed_checkouts)}",
            )

        return redirect("catalog:staff_dashboard")

    # GET request - show form
    patrons = Patron.objects.all().order_by("user__last_name")
    available_books = BookCopy.objects.filter(status="available").select_related(
        "book"
    )[
        :50
    ]  # Limit for performance

    context = {
        "patrons": patrons,
        "available_books": available_books,
    }
    return render(request, "catalog/bulk_checkout.html", context)


@login_required
def bulk_checkin(request):
    """Bulk check-in multiple books"""
    if not request.user.is_staff:
        messages.error(request, "Access denied. Staff privileges required.")
        return redirect("core:home")

    if request.method == "POST":
        book_copy_ids = request.POST.getlist("book_copies")
        condition = request.POST.get("condition", "good")

        book_copies = BookCopy.objects.filter(
            pk__in=book_copy_ids, status="checked_out"
        ).select_related("book")

        if not book_copies.exists():
            messages.error(request, "No valid books selected for check-in.")
            return redirect("catalog:bulk_checkin")

        # Process check-ins
        successful_checkins = 0
        failed_checkins = []

        for book_copy in book_copies:
            try:
                # Find active loan
                loan = Loan.objects.get(
                    book_copy=book_copy, status="active", returned_date__isnull=True
                )

                # Update loan
                loan.returned_date = timezone.now()
                loan.returned_to = request.user
                loan.status = "returned"
                loan.save()

                # Update book copy
                book_copy.status = "available"
                book_copy.condition = condition
                book_copy.save()

                successful_checkins += 1

            except Loan.DoesNotExist:
                failed_checkins.append(f"{book_copy.book.title} - No active loan found")
            except Exception as e:
                failed_checkins.append(f"{book_copy.book.title}: {str(e)}")

        if successful_checkins > 0:
            messages.success(
                request, f"Successfully checked in {successful_checkins} book(s)."
            )

        if failed_checkins:
            messages.warning(
                request,
                f"Failed to check-in {len(failed_checkins)} book(s): {', '.join(failed_checkins)}",
            )

        return redirect("catalog:staff_dashboard")

    # GET request - show form
    checked_out_books = BookCopy.objects.filter(status="checked_out").select_related(
        "book"
    )[
        :50
    ]  # Limit for performance

    context = {
        "checked_out_books": checked_out_books,
    }
    return render(request, "catalog/bulk_checkin.html", context)


@login_required
def return_book(request, book_copy_id):
    """Return a borrowed book"""
    book_copy = get_object_or_404(BookCopy, pk=book_copy_id)

    try:
        loan = Loan.objects.get(
            patron=request.user.patron,
            book_copy=book_copy,
            status="active",
            returned_date__isnull=True,
        )
    except Loan.DoesNotExist:
        messages.error(request, "You do not have this book checked out.")
        return redirect("catalog:dashboard")

    if request.method == "POST":
        form = ReturnForm(request.POST)
        if form.is_valid():
            # Update loan
            loan.returned_date = timezone.now()
            loan.returned_to = request.user
            loan.status = "returned"
            loan.save()

            # Update book copy
            book_copy.status = "available"
            book_copy.condition = form.cleaned_data["condition"]
            book_copy.save()

            messages.success(
                request, f'Successfully returned "{book_copy.book.title}".'
            )
            return redirect("catalog:dashboard")
    else:
        form = ReturnForm()

    return render(request, "catalog/return_book.html", {"form": form, "loan": loan})


@login_required
def create_reservation(request, book_id):
    """Create a book reservation"""
    book = get_object_or_404(Book, pk=book_id)

    try:
        patron = request.user.patron
    except Patron.DoesNotExist:
        messages.error(request, "Your patron profile is not set up.")
        return redirect("catalog:book_detail", slug=book.slug)

    # Check if patron already has active reservation for this book
    existing_reservation = Reservation.objects.filter(
        patron=patron, book=book, status__in=["active", "ready"]
    ).exists()

    if existing_reservation:
        messages.error(request, "You already have an active reservation for this book.")
        return redirect("catalog:book_detail", slug=book.slug)

    # Check reservation limit
    active_reservations = patron.reservations.filter(status="active").count()
    if active_reservations >= 3:  # Using default from settings
        messages.error(request, "You have reached your maximum reservation limit.")
        return redirect("catalog:book_detail", slug=book.slug)

    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.patron = patron
            reservation.book = book
            reservation.save()

            messages.success(request, f'Reservation created for "{book.title}".')
            return redirect("catalog:dashboard")
    else:
        form = ReservationForm()

    return render(
        request, "catalog/create_reservation.html", {"form": form, "book": book}
    )


@login_required
def cancel_reservation(request, pk):
    """Cancel a reservation"""
    reservation = get_object_or_404(
        Reservation, pk=pk, patron=request.user.patron, status="active"
    )

    if request.method == "POST":
        reservation.status = "cancelled"
        reservation.save()
        messages.success(request, "Reservation cancelled successfully.")
        return redirect("catalog:dashboard")

    return render(
        request, "catalog/cancel_reservation.html", {"reservation": reservation}
    )


# Staff views
@login_required
def staff_dashboard(request):
    """Staff dashboard"""
    if not request.user.is_staff:
        messages.error(request, "Access denied. Staff privileges required.")
        return redirect("core:home")

    # Statistics
    total_books = Book.objects.count()
    total_copies = BookCopy.objects.count()
    available_copies = BookCopy.objects.filter(status="available").count()
    active_loans = Loan.objects.filter(
        status="active", returned_date__isnull=True
    ).count()
    overdue_loans = Loan.objects.filter(
        status="active", due_date__lt=timezone.now(), returned_date__isnull=True
    ).count()
    active_reservations = Reservation.objects.filter(status="active").count()

    recent_loans = Loan.objects.select_related(
        "patron__user", "book_copy__book"
    ).order_by("-loan_date")[:10]

    context = {
        "total_books": total_books,
        "total_copies": total_copies,
        "available_copies": available_copies,
        "active_loans": active_loans,
        "overdue_loans": overdue_loans,
        "active_reservations": active_reservations,
        "recent_loans": recent_loans,
    }
    return render(request, "catalog/staff_dashboard.html", context)


@login_required
def add_book(request):
    """Add a new book (staff only)"""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect("core:home")

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" added successfully.')
            return redirect("catalog:add_book_copy", pk=book.pk)
    else:
        form = BookForm()

    return render(request, "catalog/add_book.html", {"form": form})


@login_required
def edit_book(request, pk):
    """Edit book (staff only)"""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect("core:home")

    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'Book "{book.title}" updated successfully.')
            return redirect("catalog:staff_dashboard")
    else:
        form = BookForm(instance=book)

    return render(request, "catalog/edit_book.html", {"form": form, "book": book})


@login_required
def add_book_copy(request, pk):
    """Add copies to a book (staff only)"""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect("core:home")

    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        form = BookCopyForm(request.POST)
        if form.is_valid():
            copy = form.save(commit=False)
            copy.book = book
            copy.save()
            messages.success(request, f'Copy added to "{book.title}".')
            return redirect("catalog:add_book_copy", pk=book.pk)
    else:
        form = BookCopyForm()

    existing_copies = book.copies.all()

    return render(
        request,
        "catalog/add_book_copy.html",
        {"form": form, "book": book, "existing_copies": existing_copies},
    )


@login_required
def add_author(request):
    """Add a new author (staff only)"""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect("core:home")

    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            messages.success(
                request, f'Author "{author.full_name}" added successfully.'
            )
            return redirect("catalog:add_author")
    else:
        form = AuthorForm()

    return render(request, "catalog/add_author.html", {"form": form})


@login_required
def add_publisher(request):
    """Add a new publisher (staff only)"""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect("core:home")

    if request.method == "POST":
        form = PublisherForm(request.POST)
        if form.is_valid():
            publisher = form.save()
            messages.success(
                request, f'Publisher "{publisher.name}" added successfully.'
            )
            return redirect("catalog:add_publisher")
    else:
        form = PublisherForm()

    return render(request, "catalog/add_publisher.html", {"form": form})


@login_required
def add_genre(request):
    """Add a new genre (staff only)"""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect("core:home")

    if request.method == "POST":
        form = GenreForm(request.POST)
        if form.is_valid():
            genre = form.save()
            messages.success(request, f'Genre "{genre.name}" added successfully.')
            return redirect("catalog:add_genre")
    else:
        form = GenreForm()

    return render(request, "catalog/add_genre.html", {"form": form})


# Circulation management views (staff)
@login_required
def circulation_dashboard(request):
    """Circulation management dashboard (staff only)"""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect("core:home")

    # Today's statistics
    today = timezone.now().date()
    today_loans = Loan.objects.filter(loan_date__date=today).count()
    today_returns = Loan.objects.filter(returned_date__date=today).count()

    context = {
        "today_loans": today_loans,
        "today_returns": today_returns,
    }
    return render(request, "catalog/circulation_dashboard.html", context)


@login_required
def loan_list(request):
    """List all loans (staff only)"""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect("core:home")

    loans = Loan.objects.select_related(
        "patron__user", "book_copy__book", "issued_by"
    ).order_by("-loan_date")

    status_filter = request.GET.get("status")
    if status_filter:
        loans = loans.filter(status=status_filter)

    loans_page = paginate_queryset(loans, request.GET.get("page"))

    return render(
        request,
        "catalog/loan_list.html",
        {"loans": loans_page, "status_filter": status_filter},
    )


@login_required
def overdue_loans(request):
    """List overdue loans (staff only)"""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect("core:home")

    overdue_loans = Loan.objects.filter(
        status="active", due_date__lt=timezone.now(), returned_date__isnull=True
    ).select_related("patron__user", "book_copy__book")

    overdue_loans_page = paginate_queryset(overdue_loans, request.GET.get("page"))

    return render(
        request, "catalog/overdue_loans.html", {"overdue_loans": overdue_loans_page}
    )


@login_required
def reservation_list(request):
    """List all reservations (staff only)"""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect("core:home")

    reservations = Reservation.objects.select_related("patron__user", "book").order_by(
        "-reservation_date"
    )

    status_filter = request.GET.get("status")
    if status_filter:
        reservations = reservations.filter(status=status_filter)

    reservations_page = paginate_queryset(reservations, request.GET.get("page"))

    return render(
        request,
        "catalog/reservation_list.html",
        {"reservations": reservations_page, "status_filter": status_filter},
    )


# API Views
class BookListAPIView(generics.ListCreateAPIView):
    """API endpoint for books"""

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class BookDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for book details"""

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class LoanListAPIView(generics.ListCreateAPIView):
    """API endpoint for loans"""

    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter loans by current user if not staff"""
        if not self.request.user.is_staff:
            return self.queryset.filter(patron=self.request.user.patron)
        return self.queryset


# Autocomplete API endpoints
@api_view(["GET"])
def book_autocomplete(request):
    """Autocomplete API for book titles"""
    query = request.GET.get("q", "").strip()
    if not query or len(query) < 2:
        return Response([])

    books = Book.objects.filter(
        Q(title__icontains=query)
        | Q(authors__first_name__icontains=query)
        | Q(authors__last_name__icontains=query)
        | Q(isbn__icontains=query)
    ).distinct()[:10]

    results = []
    for book in books:
        results.append(
            {
                "id": book.id,
                "text": f"{book.title} by {', '.join([author.full_name for author in book.authors.all()])}",
                "title": book.title,
                "authors": [author.full_name for author in book.authors.all()],
                "isbn": book.isbn,
            }
        )

    return Response(results)


# E-Library Session Management Views
@login_required
def elibrary_checkin(request):
    """E-Library check-in for students/visitors"""
    if request.method == "POST":
        form = ELibraryCheckInForm(request.POST)
        if form.is_valid():
            # Create or get visitor
            registration_number = form.cleaned_data['registration_number']
            visitor, created = Visitor.objects.get_or_create(
                registration_number=registration_number,
                defaults={
                    "full_name": form.cleaned_data['full_name'],
                    "department": form.cleaned_data['department'],
                    "level": form.cleaned_data['level'],
                    "active_phone_number": form.cleaned_data['active_phone_number'],
                }
            )

            # Update visitor info if not created
            if not created:
                visitor.full_name = form.cleaned_data['full_name']
                visitor.department = form.cleaned_data['department']
                visitor.level = form.cleaned_data['level']
                visitor.active_phone_number = form.cleaned_data['active_phone_number']
                visitor.save()

            # Create new session (validation ensures no active session exists)
            session = ELibrarySession.objects.create(
                visitor=visitor,
                items_brought_in=form.cleaned_data.get('items_brought_in', ''),
                checked_in_by=request.user,
            )

            messages.success(
                request,
                f"Check-in successful for {visitor.full_name}. Session started at {session.entry_time.strftime('%H:%M')}."
            )
            return redirect("catalog:elibrary_dashboard")
    else:
        form = ELibraryCheckInForm()

    return render(request, "catalog/elibrary_checkin.html", {"form": form})


@login_required
def elibrary_checkout(request):
    """E-Library check-out for students/visitors"""
    if request.method == "POST":
        form = ELibraryCheckOutForm(request.POST)
        if form.is_valid():
            registration_number = form.cleaned_data['registration_number']

            # Get visitor (validation ensures they exist and have active session)
            visitor = Visitor.objects.get(registration_number=registration_number)

            # Find active session (validation ensures it exists)
            active_session = ELibrarySession.objects.filter(
                visitor=visitor, status="active"
            ).first()

            # Complete the session
            active_session.complete_session(
                items_taken_out=form.cleaned_data.get('items_taken_out', ''),
                checked_out_by=request.user
            )

            duration = active_session.duration
            duration_str = f"{duration.total_seconds() // 3600:.0f}h {(duration.total_seconds() % 3600) // 60:.0f}m" if duration else "N/A"

            messages.success(
                request,
                f"Check-out successful for {visitor.full_name}. "
                f"Session duration: {duration_str}."
            )
            return redirect("catalog:elibrary_dashboard")
    else:
        form = ELibraryCheckOutForm()

    return render(request, "catalog/elibrary_checkout.html", {"form": form})


@login_required
def elibrary_dashboard(request):
    """E-Library monitoring dashboard (staff only)"""
    if not request.user.is_staff:
        messages.error(request, "Access denied. Staff privileges required.")
        return redirect("core:home")

    # Active sessions
    active_sessions = ELibrarySession.objects.filter(
        status="active"
    ).select_related("visitor").order_by("-entry_time")

    # Today's completed sessions
    today = timezone.now().date()
    today_sessions = ELibrarySession.objects.filter(
        entry_time__date=today
    ).select_related("visitor").order_by("-entry_time")

    # Statistics
    total_active = active_sessions.count()
    total_today = today_sessions.count()
    completed_today = today_sessions.filter(status="completed").count()

    context = {
        "active_sessions": active_sessions,
        "today_sessions": today_sessions,
        "total_active": total_active,
        "total_today": total_today,
        "completed_today": completed_today,
    }
    return render(request, "catalog/elibrary_dashboard.html", context)


@login_required
def elibrary_session_detail(request, session_id):
    """View details of a specific E-Library session"""
    if not request.user.is_staff:
        messages.error(request, "Access denied. Staff privileges required.")
        return redirect("core:home")

    session = get_object_or_404(
        ELibrarySession.objects.select_related("visitor"),
        pk=session_id
    )

    context = {
        "session": session,
    }
    return render(request, "catalog/elibrary_session_detail.html", context)


@login_required
def elibrary_reports(request):
    """E-Library reports and analytics (staff only)"""
    if not request.user.is_staff:
        messages.error(request, "Access denied. Staff privileges required.")
        return redirect("core:home")

    # Handle CSV export
    if request.GET.get('export') == 'csv':
        return export_sessions_csv(request)

    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date:
        start_date = timezone.now().date() - timedelta(days=30)
    else:
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()

    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

    # Filter sessions by date range
    sessions = ELibrarySession.objects.filter(
        entry_time__date__gte=start_date,
        entry_time__date__lte=end_date
    ).select_related('visitor', 'checked_in_by', 'checked_out_by')

    # Overall statistics
    total_sessions = sessions.count()
    completed_sessions = sessions.filter(status='completed').count()
    active_sessions = sessions.filter(status='active').count()
    terminated_sessions = sessions.filter(status='terminated').count()

    # Calculate average session duration for completed sessions
    completed_sessions_queryset = sessions.filter(status='completed')
    avg_duration = None
    total_duration_hours = 0

    if completed_sessions_queryset.exists():
        durations = []
        for session in completed_sessions_queryset:
            if session.duration:
                duration_hours = session.duration.total_seconds() / 3600
                durations.append(duration_hours)
                total_duration_hours += duration_hours

        if durations:
            avg_duration = sum(durations) / len(durations)

    # Department-wise statistics
    department_stats = sessions.values('visitor__department').annotate(
        total_sessions=Count('id'),
        completed_sessions=Count('id', filter=Q(status='completed')),
        avg_duration_hours=Avg(
            (F('exit_time') - F('entry_time')),
            filter=Q(status='completed')
        )
    ).order_by('-total_sessions')

    # Level-wise statistics
    level_stats = sessions.values('visitor__level').annotate(
        total_sessions=Count('id'),
        completed_sessions=Count('id', filter=Q(status='completed'))
    ).order_by('-total_sessions')

    # Daily usage statistics
    daily_stats = sessions.extra(
        select={'date': 'DATE(entry_time)'}
    ).values('date').annotate(
        total_sessions=Count('id'),
        completed_sessions=Count('id', filter=Q(status='completed')),
        active_sessions=Count('id', filter=Q(status='active'))
    ).order_by('date')

    # Peak hours analysis
    peak_hours = sessions.extra(
        select={'hour': 'EXTRACT(hour FROM entry_time)'}
    ).values('hour').annotate(
        session_count=Count('id')
    ).order_by('-session_count')[:5]

    # Items tracking summary
    items_brought_in = sessions.exclude(items_brought_in='').count()
    items_taken_out = sessions.filter(status='completed').exclude(items_taken_out='').count()

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'active_sessions': active_sessions,
        'terminated_sessions': terminated_sessions,
        'avg_duration': avg_duration,
        'department_stats': department_stats,
        'level_stats': level_stats,
        'daily_stats': daily_stats,
        'peak_hours': peak_hours,
        'items_brought_in': items_brought_in,
        'items_taken_out': items_taken_out,
    }

    return render(request, 'catalog/elibrary_reports.html', context)


def export_sessions_csv(request):
    """Export E-Library sessions to CSV"""
    if not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access denied")

    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date:
        start_date = timezone.now().date() - timedelta(days=30)
    else:
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()

    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

    # Get sessions
    sessions = ELibrarySession.objects.filter(
        entry_time__date__gte=start_date,
        entry_time__date__lte=end_date
    ).select_related('visitor', 'checked_in_by', 'checked_out_by').order_by('-entry_time')

    # Create CSV response
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="elibrary_sessions_{start_date}_{end_date}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Session ID', 'Visitor Name', 'Registration Number', 'Department', 'Level',
        'Entry Time', 'Exit Time', 'Duration (hours)', 'Status',
        'Items Brought In', 'Items Taken Out',
        'Checked In By', 'Checked Out By'
    ])

    for session in sessions:
        duration_hours = ''
        if session.duration:
            duration_hours = f"{session.duration.total_seconds() / 3600:.2f}"

        writer.writerow([
            session.id,
            session.visitor.full_name,
            session.visitor.registration_number,
            session.visitor.department,
            session.visitor.level,
            session.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
            session.exit_time.strftime('%Y-%m-%d %H:%M:%S') if session.exit_time else '',
            duration_hours,
            session.status,
            session.items_brought_in,
            session.items_taken_out,
            session.checked_in_by.get_full_name() if session.checked_in_by else '',
            session.checked_out_by.get_full_name() if session.checked_out_by else '',
        ])

    return response


@api_view(["GET"])
def author_autocomplete(request):
    """Autocomplete API for authors"""
    query = request.GET.get("q", "").strip()
    if not query or len(query) < 2:
        return Response([])

    authors = Author.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query)
    ).order_by("last_name", "first_name")[:10]

    results = []
    for author in authors:
        results.append(
            {
                "id": author.id,
                "text": author.full_name,
                "first_name": author.first_name,
                "last_name": author.last_name,
            }
        )

    return Response(results)


@api_view(["GET"])
def genre_autocomplete(request):
    """Autocomplete API for genres"""
    query = request.GET.get("q", "").strip()
    if not query or len(query) < 1:
        return Response([])

    genres = Genre.objects.filter(name__icontains=query).order_by("name")[:10]

    results = []
    for genre in genres:
        results.append(
            {
                "id": genre.id,
                "text": genre.name,
                "name": genre.name,
            }
        )

    return Response(results)


@api_view(["GET"])
def publisher_autocomplete(request):
    """Autocomplete API for publishers"""
    query = request.GET.get("q", "").strip()
    if not query or len(query) < 2:
        return Response([])

    publishers = Publisher.objects.filter(name__icontains=query).order_by("name")[:10]

    results = []
    for publisher in publishers:
        results.append(
            {
                "id": publisher.id,
                "text": publisher.name,
                "name": publisher.name,
            }
        )

    return Response(results)
