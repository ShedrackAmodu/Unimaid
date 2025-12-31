from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta

from library.admin_config import (
    RobustModelAdmin,
    SearchableModelAdmin,
    FilteredModelAdmin,
    colored_status,
    count_badge,
    get_image_preview,
    DateRangeFilter,
    StatusFilter,
    ExportableAdmin,
    EditableInline,
)

from .models import (
    Genre,
    Author,
    Publisher,
    Book,
    BookCopy,
    Patron,
    Loan,
    Reservation,
    Fine,
    AnalyticsEvent,
    PopularBook,
    SearchAnalytics,
    SystemMetrics,
    NotificationTemplate,
    Notification,
)


# ============================================================================
# GENRE ADMIN
# ============================================================================


@admin.register(Genre)
class GenreAdmin(SearchableModelAdmin):
    list_display = ("name", "book_count", "description_preview")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)

    def book_count(self, obj):
        count = obj.books.count()
        return count_badge(count, "books")

    book_count.short_description = "Books in Genre"

    def description_preview(self, obj):
        desc = (
            obj.description[:50] + "..."
            if obj.description and len(obj.description) > 50
            else obj.description or "—"
        )
        return desc

    description_preview.short_description = "Description"


# ============================================================================
# AUTHOR ADMIN
# ============================================================================


@admin.register(Author)
class AuthorAdmin(SearchableModelAdmin):
    list_display = (
        "full_name",
        "birth_year",
        "death_year",
        "book_count",
        "website_link",
    )
    search_fields = ("first_name", "last_name", "bio")
    list_filter = ("birth_date", "death_date", "books__genres")
    date_hierarchy = "birth_date"
    readonly_fields = ("full_name", "book_list")

    fieldsets = (
        (
            "Personal Information",
            {"fields": ("first_name", "last_name", "full_name", "bio")},
        ),
        ("Dates", {"fields": ("birth_date", "death_date")}),
        ("Contact & Web", {"fields": ("website",)}),
        ("Related Books", {"fields": ("book_list",), "classes": ("collapse",)}),
    )

    def birth_year(self, obj):
        return obj.birth_date.year if obj.birth_date else "—"

    birth_year.short_description = "Birth Year"

    def death_year(self, obj):
        return obj.death_date.year if obj.death_date else "—"

    death_year.short_description = "Death Year"

    def book_count(self, obj):
        count = obj.books.count()
        return count_badge(count, "books")

    book_count.short_description = "Books Authored"

    def website_link(self, obj):
        if obj.website:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener">🔗 Visit</a>', obj.website
            )
        return "—"

    website_link.short_description = "Website"

    def book_list(self, obj):
        books = obj.books.all()
        if books:
            return format_html(
                '<ul style="margin: 0; padding-left: 20px;">{}</ul>',
                "".join([f"<li>{book.title}</li>" for book in books]),
            )
        return "No books"

    book_list.short_description = "Associated Books"


# ============================================================================
# PUBLISHER ADMIN
# ============================================================================


@admin.register(Publisher)
class PublisherAdmin(SearchableModelAdmin):
    list_display = ("name", "book_count", "email_link", "website_link", "contact_email")
    search_fields = ("name", "contact_email", "address")
    list_filter = ()

    fieldsets = (
        ("Basic Information", {"fields": ("name",)}),
        ("Contact Information", {"fields": ("contact_email", "website")}),
        ("Address", {"fields": ("address",), "classes": ("collapse",)}),
    )

    def book_count(self, obj):
        count = obj.books.count()
        return count_badge(count, "books")

    book_count.short_description = "Published Books"

    def email_link(self, obj):
        if obj.contact_email:
            return format_html(
                '<a href="mailto:{}">{}</a>', obj.contact_email, obj.contact_email
            )
        return "—"

    email_link.short_description = "Email"

    def website_link(self, obj):
        if obj.website:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener">🔗 Visit</a>', obj.website
            )
        return "—"

    website_link.short_description = "Website"


# ============================================================================
# BOOK COPY INLINE
# ============================================================================


class BookCopyInline(EditableInline):
    model = BookCopy
    extra = 1
    fields = (
        "copy_number",
        "barcode",
        "status",
        "condition",
        "location",
        "is_reference_only",
        "purchase_price",
    )
    list_display = ("copy_number", "status", "location")


# ============================================================================
# BOOK ADMIN
# ============================================================================


@admin.register(Book)
class BookAdmin(ExportableAdmin):
    list_display = (
        "book_title_with_image",
        "isbn",
        "publisher",
        "availability_status",
        "genre_list",
        "date_added",
    )
    search_fields = (
        "title",
        "isbn",
        "isbn13",
        "description",
        "authors__first_name",
        "authors__last_name",
    )
    list_filter = (
        "genres",
        "publisher",
        ("publication_date", admin.DateFieldListFilter),
        "language",
        "date_added",
    )
    filter_horizontal = ("authors", "genres")
    inlines = [BookCopyInline]
    readonly_fields = (
        "available_copies",
        "total_copies",
        "date_added",
        "last_updated",
        "book_cover_preview",
    )
    date_hierarchy = "date_added"
    list_per_page = 50

    fieldsets = (
        ("Basic Information", {"fields": ("title", "slug", "isbn", "isbn13")}),
        (
            "Metadata",
            {
                "fields": (
                    "authors",
                    "publisher",
                    "genres",
                    "language",
                    "edition",
                    "pages",
                    "publication_date",
                )
            },
        ),
        ("Description", {"fields": ("description",), "classes": ("collapse",)}),
        (
            "Media",
            {
                "fields": ("book_cover_preview", "cover_image", "sample_pages"),
                "classes": ("collapse",),
            },
        ),
        (
            "Statistics",
            {
                "fields": (
                    "available_copies",
                    "total_copies",
                    "date_added",
                    "last_updated",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["export_as_csv"]

    def book_title_with_image(self, obj):
        if obj.cover_image:
            img_html = get_image_preview(obj.cover_image.url, "50px", "75px")
            return format_html(
                '<div style="display: flex; gap: 10px; align-items: center;">'
                "{}<strong>{}</strong></div>",
                img_html,
                obj.title,
            )
        return format_html("<strong>{}</strong>", obj.title)

    book_title_with_image.short_description = "Book"

    def availability_status(self, obj):
        total = obj.total_copies
        available = obj.available_copies
        if total == 0:
            status = "No Copies"
            color = "#dc3545"
        elif available == 0:
            status = "All Checked Out"
            color = "#ffc107"
        else:
            status = f"{available}/{total} Available"
            color = "#28a745"

        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold; display: inline-block;">{}</span>',
            color,
            status,
        )

    availability_status.short_description = "Availability"

    def genre_list(self, obj):
        genres = obj.genres.all()
        if genres:
            return format_html(
                '<span style="display: inline-block; background: #e9ecef; padding: 5px 10px; '
                'border-radius: 20px; font-size: 0.85em;">{}</span>',
                ", ".join([g.name for g in genres]),
            )
        return "—"

    genre_list.short_description = "Genres"

    def book_cover_preview(self, obj):
        if obj.cover_image:
            return get_image_preview(obj.cover_image.url, "200px", "300px")
        return format_html('<span style="color: #ccc;">No cover image</span>')

    book_cover_preview.short_description = "Cover Preview"

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="books.csv"'
        writer = csv.writer(response)
        writer.writerow(
            [
                "Title",
                "ISBN",
                "Publisher",
                "Authors",
                "Genres",
                "Available",
                "Total Copies",
                "Date Added",
            ]
        )

        for book in queryset:
            writer.writerow(
                [
                    book.title,
                    book.isbn or "",
                    book.publisher.name if book.publisher else "",
                    ", ".join([str(a) for a in book.authors.all()]),
                    ", ".join([g.name for g in book.genres.all()]),
                    book.available_copies,
                    book.total_copies,
                    book.date_added.strftime("%Y-%m-%d"),
                ]
            )

        return response

    export_as_csv.short_description = "📥 Export selected books as CSV"


# ============================================================================
# BOOK COPY ADMIN
# ============================================================================


@admin.register(BookCopy)
class BookCopyAdmin(ExportableAdmin):
    list_display = (
        "copy_identifier",
        "book_link",
        "status_colored",
        "location",
        "condition",
        "is_reference",
        "acquisition_date",
    )
    search_fields = ("book__title", "copy_number", "barcode", "location")
    list_filter = (
        "status",
        "location",
        "is_reference_only",
        "acquisition_date",
    )
    list_editable = ("location", "condition")
    date_hierarchy = "acquisition_date"
    readonly_fields = ("qr_code_preview", "barcode_display")
    list_per_page = 100

    fieldsets = (
        ("Book Information", {"fields": ("book", "copy_number", "barcode_display")}),
        ("Status", {"fields": ("status", "condition", "location")}),
        ("Reference", {"fields": ("is_reference_only",)}),
        (
            "Acquisition",
            {
                "fields": ("acquisition_date", "purchase_price"),
                "classes": ("collapse",),
            },
        ),
        ("QR Code", {"fields": ("qr_code_preview",), "classes": ("collapse",)}),
    )

    def copy_identifier(self, obj):
        return f"{obj.copy_number}"

    copy_identifier.short_description = "Copy #"

    def book_link(self, obj):
        return format_html(
            '<a href="/admin/catalog/book/{}/change/">{}</a>',
            obj.book.id,
            obj.book.title,
        )

    book_link.short_description = "Book"

    def status_colored(self, obj):
        return colored_status(obj.status)

    status_colored.short_description = "Status"

    def is_reference(self, obj):
        if obj.is_reference_only:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Reference</span>'
            )
        return "—"

    is_reference.short_description = "Reference Only"

    def barcode_display(self, obj):
        return obj.barcode or "Not assigned"

    barcode_display.short_description = "Barcode"

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return get_image_preview(obj.qr_code.url, "200px", "200px")
        return "No QR code generated"

    qr_code_preview.short_description = "QR Code"


# ============================================================================
# PATRON ADMIN
# ============================================================================


@admin.register(Patron)
class PatronAdmin(SearchableModelAdmin):
    list_display = (
        "patron_name",
        "membership_type_colored",
        "membership_status",
        "active_loans_count",
        "outstanding_fines",
        "registration_display",
    )
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "membership_number",
        "phone",
    )
    list_filter = (
        "membership_type",
        "registration_date",
        "membership_expiry",
    )
    readonly_fields = (
        "registration_date",
        "active_loans_list",
        "outstanding_fines_display",
        "reservation_list",
        "qr_code_preview",
    )
    date_hierarchy = "registration_date"
    list_per_page = 50

    fieldsets = (
        ("User Information", {"fields": ("user",)}),
        (
            "Membership",
            {"fields": ("membership_type", "membership_number", "membership_expiry")},
        ),
        (
            "Personal Information",
            {
                "fields": ("phone", "date_of_birth", "address", "emergency_contact"),
                "classes": ("collapse",),
            },
        ),
        ("QR Code", {"fields": ("qr_code_preview",), "classes": ("collapse",)}),
        (
            "Account Status",
            {
                "fields": (
                    "active_loans_list",
                    "outstanding_fines_display",
                    "reservation_list",
                    "registration_date",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def patron_name(self, obj):
        return format_html(
            '<strong>{} {}</strong><br/><small style="color: #666;">@{}</small>',
            obj.user.first_name or "N/A",
            obj.user.last_name or "N/A",
            obj.user.username,
        )

    patron_name.short_description = "Patron"

    def membership_type_colored(self, obj):
        colors = {
            "student": "#007bff",
            "faculty": "#28a745",
            "public": "#ffc107",
            "special": "#dc3545",
        }
        color = colors.get(obj.membership_type, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_membership_type_display(),
        )

    membership_type_colored.short_description = "Membership Type"

    def membership_status(self, obj):
        if obj.membership_expiry:
            if obj.membership_expiry < timezone.now().date():
                status = "Expired"
                color = "#dc3545"
            else:
                status = "Active"
                color = "#28a745"
            return format_html(
                '<span style="background-color: {}; color: white; padding: 5px 10px; '
                'border-radius: 3px;">{}</span>',
                color,
                status,
            )
        return "—"

    membership_status.short_description = "Status"

    def active_loans_count(self, obj):
        count = obj.loans.filter(status="active", returned_date__isnull=True).count()
        return count_badge(count, "active loans")

    active_loans_count.short_description = "Active Loans"

    def outstanding_fines(self, obj):
        total = (
            obj.fines.filter(paid=False).aggregate(Sum("amount"))["amount__sum"] or 0
        )
        if total > 0:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 5px 10px; '
                'border-radius: 3px; font-weight: bold;">₦{}</span>',
                total,
            )
        return "—"

    outstanding_fines.short_description = "Outstanding Fines"

    def registration_display(self, obj):
        return obj.registration_date.strftime("%b %d, %Y")

    registration_display.short_description = "Registered"

    def active_loans_list(self, obj):
        loans = obj.loans.filter(status="active", returned_date__isnull=True)
        if loans:
            return format_html(
                '<ul style="margin: 0; padding-left: 20px;">{}</ul>',
                "".join(
                    [
                        f'<li>{loan.book_copy.book.title} - Due: {loan.due_date.strftime("%Y-%m-%d")}</li>'
                        for loan in loans
                    ]
                ),
            )
        return "No active loans"

    active_loans_list.short_description = "Active Loans"

    def outstanding_fines_display(self, obj):
        fines = obj.fines.filter(paid=False)
        total = fines.aggregate(Sum("amount"))["amount__sum"] or 0
        if total > 0:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">₦{}</span>', total
            )
        return format_html(
            '<span style="color: green; font-weight: bold;">✓ No outstanding fines</span>'
        )

    outstanding_fines_display.short_description = "Outstanding Fines"

    def reservation_list(self, obj):
        reservations = obj.reservations.filter(status="active")
        if reservations:
            return format_html(
                '<ul style="margin: 0; padding-left: 20px;">{}</ul>',
                "".join([f"<li>{res.book.title}</li>" for res in reservations]),
            )
        return "No active reservations"

    reservation_list.short_description = "Active Reservations"

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return get_image_preview(obj.qr_code.url, "150px", "150px")
        return "No QR code"

    qr_code_preview.short_description = "QR Code"


# ============================================================================
# LOAN ADMIN
# ============================================================================


@admin.register(Loan)
class LoanAdmin(ExportableAdmin):
    list_display = (
        "patron_link",
        "book_copy_link",
        "loan_date_display",
        "status_with_overdue",
        "due_date_display",
        "issued_by",
    )
    search_fields = (
        "patron__user__username",
        "patron__user__first_name",
        "patron__user__last_name",
        "book_copy__book__title",
        "book_copy__copy_number",
    )
    list_filter = (
        "status",
        "loan_date",
        "due_date",
        "issued_by",
    )
    readonly_fields = ("is_overdue", "days_overdue", "loan_date", "fine_if_overdue")
    date_hierarchy = "loan_date"
    list_per_page = 100

    actions = ["mark_as_returned", "mark_as_lost"]

    fieldsets = (
        (
            "Loan Information",
            {"fields": ("patron", "book_copy", "issued_by", "loan_date")},
        ),
        ("Dates", {"fields": ("due_date", "returned_date")}),
        ("Status", {"fields": ("status", "is_overdue", "days_overdue")}),
        (
            "Fine Information",
            {"fields": ("fine_if_overdue",), "classes": ("collapse",)},
        ),
        ("Notes", {"fields": ("notes",), "classes": ("collapse",)}),
    )

    def patron_link(self, obj):
        return format_html(
            '<a href="/admin/catalog/patron/{}/change/">{} {}</a>',
            obj.patron.id,
            obj.patron.user.first_name,
            obj.patron.user.last_name,
        )

    patron_link.short_description = "Patron"

    def book_copy_link(self, obj):
        return format_html(
            '<a href="/admin/catalog/bookcopy/{}/change/">{}</a>',
            obj.book_copy.id,
            obj.book_copy.book.title[:50],
        )

    book_copy_link.short_description = "Book"

    def loan_date_display(self, obj):
        return obj.loan_date.strftime("%b %d, %Y")

    loan_date_display.short_description = "Loan Date"

    def due_date_display(self, obj):
        if obj.is_overdue:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">{} (OVERDUE)</span>',
                obj.due_date.strftime("%b %d, %Y"),
            )
        return obj.due_date.strftime("%b %d, %Y")

    due_date_display.short_description = "Due Date"

    def status_with_overdue(self, obj):
        if obj.status == "returned":
            return colored_status("returned")
        elif obj.is_overdue:
            return colored_status("overdue", {"overdue": "#dc3545"})
        return colored_status(obj.status)

    status_with_overdue.short_description = "Status"

    def days_overdue(self, obj):
        if obj.is_overdue:
            days = (timezone.now().date() - obj.due_date).days
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">{} days</span>', days
            )
        return "—"

    days_overdue.short_description = "Days Overdue"

    def fine_if_overdue(self, obj):
        if obj.is_overdue:
            # Assuming 50 naira per day fine
            days = (timezone.now().date() - obj.due_date).days
            fine = days * 50
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">₦{}</span>', fine
            )
        return "—"

    fine_if_overdue.short_description = "Estimated Fine"

    def mark_as_returned(self, request, queryset):
        count = queryset.filter(status="active").update(
            status="returned", returned_date=timezone.now()
        )
        self.message_user(request, f"{count} loan(s) marked as returned.")

    mark_as_returned.short_description = "✓ Mark selected as returned"

    def mark_as_lost(self, request, queryset):
        count = queryset.filter(status="active").update(status="lost")
        self.message_user(request, f"{count} book(s) marked as lost.")

    mark_as_lost.short_description = "✗ Mark selected as lost"


# ============================================================================
# RESERVATION ADMIN
# ============================================================================


@admin.register(Reservation)
class ReservationAdmin(ExportableAdmin):
    list_display = (
        "patron_link",
        "book_link",
        "reservation_date_display",
        "status_colored",
        "ready_date_display",
        "notify_email_icon",
    )
    search_fields = (
        "patron__user__username",
        "patron__user__first_name",
        "patron__user__last_name",
        "book__title",
    )
    list_filter = (
        "status",
        "reservation_date",
        "notify_email",
    )
    readonly_fields = ("reservation_date", "waiting_days")
    date_hierarchy = "reservation_date"
    list_per_page = 50

    actions = ["mark_as_ready", "mark_as_fulfilled", "notify_patrons"]

    fieldsets = (
        ("Reservation Information", {"fields": ("patron", "book", "reservation_date")}),
        ("Status", {"fields": ("status", "waiting_days")}),
        (
            "Ready Information",
            {"fields": ("ready_date", "pickup_deadline"), "classes": ("collapse",)},
        ),
        (
            "Notification",
            {"fields": ("notify_email", "notes"), "classes": ("collapse",)},
        ),
    )

    def patron_link(self, obj):
        return format_html(
            '<a href="/admin/catalog/patron/{}/change/">{} {}</a>',
            obj.patron.id,
            obj.patron.user.first_name,
            obj.patron.user.last_name,
        )

    patron_link.short_description = "Patron"

    def book_link(self, obj):
        return format_html(
            '<a href="/admin/catalog/book/{}/change/">{}</a>',
            obj.book.id,
            obj.book.title[:50],
        )

    book_link.short_description = "Book"

    def reservation_date_display(self, obj):
        return obj.reservation_date.strftime("%b %d, %Y")

    reservation_date_display.short_description = "Reserved On"

    def status_colored(self, obj):
        return colored_status(obj.status)

    status_colored.short_description = "Status"

    def ready_date_display(self, obj):
        if obj.ready_date:
            return obj.ready_date.strftime("%b %d, %Y")
        return "—"

    ready_date_display.short_description = "Ready Date"

    def notify_email_icon(self, obj):
        if obj.notify_email:
            return format_html(
                '<span style="color: green; font-weight: bold;">✉ Email</span>'
            )
        return "—"

    notify_email_icon.short_description = "Notify"

    def waiting_days(self, obj):
        days = (timezone.now().date() - obj.reservation_date.date()).days
        return f"{days} days"

    waiting_days.short_description = "Waiting"

    def mark_as_ready(self, request, queryset):
        count = queryset.filter(status="active").update(
            status="ready", ready_date=timezone.now()
        )
        self.message_user(request, f"{count} reservation(s) marked as ready.")

    mark_as_ready.short_description = "📦 Mark as ready for pickup"

    def mark_as_fulfilled(self, request, queryset):
        count = queryset.filter(status="ready").update(status="fulfilled")
        self.message_user(request, f"{count} reservation(s) marked as fulfilled.")

    mark_as_fulfilled.short_description = "✓ Mark as fulfilled"

    def notify_patrons(self, request, queryset):
        # This would trigger email notifications
        count = queryset.filter(status="ready", notify_email=True).count()
        self.message_user(request, f"Notification emails queued for {count} patron(s).")

    notify_patrons.short_description = "✉ Send notifications to selected"


# ============================================================================
# FINE ADMIN
# ============================================================================


@admin.register(Fine)
class FineAdmin(ExportableAdmin):
    list_display = (
        "patron_link",
        "fine_type_colored",
        "amount_display",
        "paid",
        "paid_status",
        "date_assessed_display",
        "date_paid_display",
    )
    search_fields = ("patron__user__username", "fine_type", "description")
    list_filter = (
        "fine_type",
        "paid",
        "date_assessed",
    )
    list_editable = ("paid",)
    readonly_fields = ("date_assessed", "amount_display_rw")
    date_hierarchy = "date_assessed"
    list_per_page = 100

    actions = ["mark_as_paid", "mark_as_unpaid"]

    fieldsets = (
        ("Fine Information", {"fields": ("patron", "fine_type", "amount")}),
        ("Description", {"fields": ("description",)}),
        (
            "Payment Status",
            {
                "fields": ("paid", "date_assessed", "date_paid"),
            },
        ),
    )

    def patron_link(self, obj):
        return format_html(
            '<a href="/admin/catalog/patron/{}/change/">{} {}</a>',
            obj.patron.id,
            obj.patron.user.first_name,
            obj.patron.user.last_name,
        )

    patron_link.short_description = "Patron"

    def fine_type_colored(self, obj):
        colors = {
            "late": "#ffc107",
            "damage": "#dc3545",
            "loss": "#dc3545",
            "other": "#6c757d",
        }
        color = colors.get(obj.fine_type, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 0.9em;">{}</span>',
            color,
            obj.get_fine_type_display(),
        )

    fine_type_colored.short_description = "Type"

    def amount_display(self, obj):
        return format_html("<strong>₦{:.2f}</strong>", obj.amount)

    amount_display.short_description = "Amount"

    def amount_display_rw(self, obj):
        return f"₦{obj.amount:.2f}"

    amount_display_rw.short_description = "Amount"

    def paid_status(self, obj):
        if obj.paid:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-weight: bold;">✓ Paid</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold;">✗ Unpaid</span>'
        )

    paid_status.short_description = "Payment Status"

    def date_assessed_display(self, obj):
        return obj.date_assessed.strftime("%b %d, %Y")

    date_assessed_display.short_description = "Assessed"

    def date_paid_display(self, obj):
        if obj.date_paid:
            return obj.date_paid.strftime("%b %d, %Y")
        return "—"

    date_paid_display.short_description = "Paid On"

    def mark_as_paid(self, request, queryset):
        count = queryset.filter(paid=False).update(paid=True, date_paid=timezone.now())
        self.message_user(request, f"{count} fine(s) marked as paid.")

    mark_as_paid.short_description = "✓ Mark selected as paid"

    def mark_as_unpaid(self, request, queryset):
        count = queryset.update(paid=False, date_paid=None)
        self.message_user(request, f"{count} fine(s) marked as unpaid.")

    mark_as_unpaid.short_description = "✗ Mark selected as unpaid"


# ============================================================================
# ANALYTICS ADMIN (Read-only)
# ============================================================================


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(RobustModelAdmin):
    list_display = (
        "event_type_colored",
        "user_display",
        "book_display",
        "timestamp_display",
        "ip_address_display",
    )
    search_fields = ("event_type", "user__username", "book__title", "ip_address")
    list_filter = (
        "event_type",
        "timestamp",
        "user",
    )
    readonly_fields = ("user", "book", "timestamp", "event_type", "data_display")
    date_hierarchy = "timestamp"
    list_per_page = 100

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def event_type_colored(self, obj):
        colors = {
            "search": "#007bff",
            "view_book": "#17a2b8",
            "checkout": "#28a745",
            "checkin": "#6c757d",
            "reservation": "#ffc107",
            "login": "#007bff",
            "register": "#28a745",
            "page_view": "#6c757d",
        }
        color = colors.get(obj.event_type, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_event_type_display(),
        )

    event_type_colored.short_description = "Event"

    def user_display(self, obj):
        if obj.user:
            return format_html(
                '<a href="/admin/auth/user/{}/change/">{}</a>',
                obj.user.id,
                obj.user.username,
            )
        return "Anonymous"

    user_display.short_description = "User"

    def book_display(self, obj):
        if obj.book:
            return format_html(
                '<a href="/admin/catalog/book/{}/change/">{}</a>',
                obj.book.id,
                obj.book.title[:50],
            )
        return "—"

    book_display.short_description = "Book"

    def timestamp_display(self, obj):
        return obj.timestamp.strftime("%b %d, %Y %H:%M:%S")

    timestamp_display.short_description = "Timestamp"

    def ip_address_display(self, obj):
        return obj.ip_address or "—"

    ip_address_display.short_description = "IP Address"

    def data_display(self, obj):
        import json

        try:
            formatted = json.dumps(obj.data, indent=2)
            return format_html(
                '<pre style="background: #f5f5f5; padding: 10px; border-radius: 3px;">{}</pre>',
                formatted,
            )
        except:
            return str(obj.data)

    data_display.short_description = "Event Data"


# ============================================================================
# POPULAR BOOKS ADMIN
# ============================================================================


@admin.register(PopularBook)
class PopularBookAdmin(RobustModelAdmin):
    list_display = (
        "book_link",
        "popularity_score_display",
        "trending_score_display",
        "view_count",
        "checkout_count",
        "last_updated_display",
    )
    search_fields = ("book__title",)
    list_filter = ("last_updated",)
    readonly_fields = (
        "book",
        "popularity_score",
        "trending_score",
        "view_count",
        "checkout_count",
        "reservation_count",
        "search_appearance_count",
        "last_updated",
        "created_at",
    )
    date_hierarchy = "last_updated"
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def book_link(self, obj):
        return format_html(
            '<a href="/admin/catalog/book/{}/change/">{}</a>',
            obj.book.id,
            obj.book.title,
        )

    book_link.short_description = "Book"

    def popularity_score_display(self, obj):
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold;">{:.2f}</span>',
            obj.popularity_score,
        )

    popularity_score_display.short_description = "Popularity"

    def trending_score_display(self, obj):
        return format_html(
            '<span style="background-color: #ffc107; color: black; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold;">{:.2f}</span>',
            obj.trending_score,
        )

    trending_score_display.short_description = "Trending"

    def last_updated_display(self, obj):
        return obj.last_updated.strftime("%b %d, %Y %H:%M")

    last_updated_display.short_description = "Updated"


# ============================================================================
# SEARCH ANALYTICS ADMIN
# ============================================================================


@admin.register(SearchAnalytics)
class SearchAnalyticsAdmin(RobustModelAdmin):
    list_display = (
        "query_display",
        "user_display",
        "result_count_display",
        "clicked_results_display",
        "search_duration_display",
        "timestamp_display",
    )
    search_fields = ("query", "user__username")
    list_filter = ("timestamp", "user")
    readonly_fields = ("query", "user", "timestamp", "filters_display")
    date_hierarchy = "timestamp"
    list_per_page = 100

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def query_display(self, obj):
        return format_html('<strong>"{}"</strong>', obj.query)

    query_display.short_description = "Query"

    def user_display(self, obj):
        if obj.user:
            return obj.user.username
        return "Anonymous"

    user_display.short_description = "User"

    def result_count_display(self, obj):
        return count_badge(obj.result_count, "results")

    result_count_display.short_description = "Results"

    def clicked_results_display(self, obj):
        return count_badge(obj.clicked_results, "clicked")

    clicked_results_display.short_description = "Clicked"

    def search_duration_display(self, obj):
        if obj.search_duration:
            return f"{obj.search_duration}s"
        return "—"

    search_duration_display.short_description = "Duration"

    def timestamp_display(self, obj):
        return obj.timestamp.strftime("%b %d, %Y %H:%M:%S")

    timestamp_display.short_description = "Time"

    def filters_display(self, obj):
        import json

        try:
            formatted = json.dumps(obj.filters_used, indent=2)
            return format_html(
                '<pre style="background: #f5f5f5; padding: 10px; border-radius: 3px;">{}</pre>',
                formatted,
            )
        except:
            return str(obj.filters_used)

    filters_display.short_description = "Filters"


# ============================================================================
# SYSTEM METRICS ADMIN
# ============================================================================


@admin.register(SystemMetrics)
class SystemMetricsAdmin(RobustModelAdmin):
    list_display = (
        "date",
        "collection_summary",
        "circulation_summary",
        "financial_summary",
    )
    search_fields = ("date",)
    list_filter = (("date", admin.DateFieldListFilter),)
    readonly_fields = (
        "date",
        "total_books",
        "total_copies",
        "available_copies",
        "total_patrons",
        "active_patrons",
        "total_loans",
        "active_loans",
        "overdue_loans",
        "total_fines",
        "paid_fines",
        "outstanding_fines",
    )
    date_hierarchy = "date"
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def collection_summary(self, obj):
        return format_html(
            "<strong>{}</strong> books<br/><small>{} copies ({} available)</small>",
            obj.total_books,
            obj.total_copies,
            obj.available_copies,
        )

    collection_summary.short_description = "Collection"

    def circulation_summary(self, obj):
        return format_html(
            "<strong>{}</strong> loans<br/><small>{} active, {} overdue</small>",
            obj.total_loans,
            obj.active_loans,
            obj.overdue_loans,
        )

    circulation_summary.short_description = "Circulation"

    def financial_summary(self, obj):
        return format_html(
            "₦{:.2f} total<br/><small>₦{:.2f} paid, ₦{:.2f} outstanding</small>",
            obj.total_fines,
            obj.paid_fines,
            obj.outstanding_fines,
        )

    financial_summary.short_description = "Financials"


# ============================================================================
# USER ADMIN CUSTOMIZATION
# ============================================================================


class PatronInline(admin.StackedInline):
    model = Patron
    can_delete = False
    verbose_name_plural = "Patron Profile"
    fields = ("membership_type", "membership_number", "phone", "address")


class CustomUserAdmin(DefaultUserAdmin):
    inlines = (PatronInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff_display",
        "last_login_display",
    )

    def is_staff_display(self, obj):
        if obj.is_staff:
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 3px 8px; '
                'border-radius: 3px;">Staff</span>'
            )
        return "—"

    is_staff_display.short_description = "Role"

    def last_login_display(self, obj):
        if obj.last_login:
            return obj.last_login.strftime("%b %d, %Y %H:%M")
        return "Never"

    last_login_display.short_description = "Last Login"
