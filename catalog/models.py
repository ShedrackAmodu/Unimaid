from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw


class Genre(models.Model):
    """Book genres/categories"""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AnalyticsEvent(models.Model):
    """Track user interactions and system events for analytics"""

    EVENT_TYPES = [
        ("search", "Search Query"),
        ("view_book", "Book Detail View"),
        ("checkout", "Book Checkout"),
        ("checkin", "Book Check-in"),
        ("reservation", "Reservation Created"),
        ("login", "User Login"),
        ("register", "User Registration"),
        ("page_view", "Page View"),
    ]

    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_events",
    )
    session_id = models.CharField(max_length=100, blank=True)  # For anonymous users
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Event data (JSON field for flexible data storage)
    data = models.JSONField(default=dict, help_text="Additional event data")

    # Related objects
    book = models.ForeignKey(
        "Book",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_events",
    )
    book_copy = models.ForeignKey(
        "BookCopy",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_events",
    )
    patron = models.ForeignKey(
        "Patron",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_events",
    )

    # Metadata
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["event_type", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["book", "event_type"]),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.timestamp}"


class PopularBook(models.Model):
    """Track popular books based on various metrics"""

    book = models.OneToOneField(
        "Book", on_delete=models.CASCADE, related_name="popularity"
    )
    view_count = models.PositiveIntegerField(default=0)
    checkout_count = models.PositiveIntegerField(default=0)
    reservation_count = models.PositiveIntegerField(default=0)
    search_appearance_count = models.PositiveIntegerField(default=0)

    # Calculated scores
    popularity_score = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    trending_score = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Date tracking
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-popularity_score"]

    def __str__(self):
        return f"{self.book.title} - Score: {self.popularity_score}"

    def update_scores(self):
        """Recalculate popularity and trending scores"""
        # Popularity score: weighted combination of metrics
        self.popularity_score = (
            self.view_count * 1.0
            + self.checkout_count * 5.0
            + self.reservation_count * 3.0
            + self.search_appearance_count * 0.5
        )

        # Trending score: recent activity (could be enhanced with time decay)
        # For now, just use recent activity as a proxy
        self.trending_score = self.popularity_score * 0.8  # Simplified

        self.save()


class SearchAnalytics(models.Model):
    """Track search queries and their performance"""

    query = models.CharField(max_length=500)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="searches"
    )
    session_id = models.CharField(max_length=100, blank=True)

    # Search parameters
    filters_used = models.JSONField(default=dict, help_text="Applied filters")
    result_count = models.PositiveIntegerField(default=0)
    clicked_results = models.PositiveIntegerField(
        default=0
    )  # Books clicked from results

    # Performance metrics
    search_duration = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )  # in seconds

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["query", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
        ]

    def __str__(self):
        return f"'{self.query}' - {self.result_count} results"


class SystemMetrics(models.Model):
    """Daily system metrics snapshot"""

    date = models.DateField(unique=True)

    # Collection metrics
    total_books = models.PositiveIntegerField(default=0)
    total_copies = models.PositiveIntegerField(default=0)
    available_copies = models.PositiveIntegerField(default=0)

    # User metrics
    total_patrons = models.PositiveIntegerField(default=0)
    active_patrons = models.PositiveIntegerField(
        default=0
    )  # With loans/reservations in last 30 days

    # Circulation metrics
    total_loans = models.PositiveIntegerField(default=0)
    active_loans = models.PositiveIntegerField(default=0)
    overdue_loans = models.PositiveIntegerField(default=0)
    returned_today = models.PositiveIntegerField(default=0)

    # Reservation metrics
    total_reservations = models.PositiveIntegerField(default=0)
    active_reservations = models.PositiveIntegerField(default=0)
    reservations_fulfilled = models.PositiveIntegerField(default=0)

    # Financial metrics
    total_fines = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    paid_fines = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    outstanding_fines = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )

    # Usage metrics
    total_searches = models.PositiveIntegerField(default=0)
    unique_search_queries = models.PositiveIntegerField(default=0)
    page_views = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Metrics for {self.date}"

    @classmethod
    def generate_daily_metrics(cls, target_date=None):
        """Generate metrics for a specific date"""
        if target_date is None:
            target_date = timezone.now().date()

        # Avoid duplicates
        if cls.objects.filter(date=target_date).exists():
            return cls.objects.get(date=target_date)

        metrics = cls(date=target_date)

        # Collection metrics
        metrics.total_books = Book.objects.count()
        metrics.total_copies = BookCopy.objects.count()
        metrics.available_copies = BookCopy.objects.filter(status="available").count()

        # User metrics
        metrics.total_patrons = Patron.objects.count()
        thirty_days_ago = timezone.now() - timedelta(days=30)
        metrics.active_patrons = (
            Patron.objects.filter(
                models.Q(loans__loan_date__gte=thirty_days_ago)
                | models.Q(reservations__reservation_date__gte=thirty_days_ago)
            )
            .distinct()
            .count()
        )

        # Circulation metrics
        metrics.total_loans = Loan.objects.count()
        metrics.active_loans = Loan.objects.filter(
            status="active", returned_date__isnull=True
        ).count()
        metrics.overdue_loans = Loan.objects.filter(
            status="active", due_date__lt=timezone.now(), returned_date__isnull=True
        ).count()
        metrics.returned_today = Loan.objects.filter(
            returned_date__date=target_date
        ).count()

        # Reservation metrics
        metrics.total_reservations = Reservation.objects.count()
        metrics.active_reservations = Reservation.objects.filter(
            status="active"
        ).count()
        metrics.reservations_fulfilled = Reservation.objects.filter(
            status="fulfilled", ready_date__date=target_date
        ).count()

        # Financial metrics
        all_fines = Fine.objects.all()
        metrics.total_fines = (
            all_fines.aggregate(models.Sum("amount"))["amount__sum"] or 0
        )
        metrics.paid_fines = (
            all_fines.filter(paid=True).aggregate(models.Sum("amount"))["amount__sum"]
            or 0
        )
        metrics.outstanding_fines = (
            all_fines.filter(paid=False).aggregate(models.Sum("amount"))["amount__sum"]
            or 0
        )

        # Usage metrics
        metrics.total_searches = SearchAnalytics.objects.filter(
            timestamp__date=target_date
        ).count()
        metrics.unique_search_queries = (
            SearchAnalytics.objects.filter(timestamp__date=target_date)
            .values("query")
            .distinct()
            .count()
        )
        metrics.page_views = AnalyticsEvent.objects.filter(
            timestamp__date=target_date, event_type="page_view"
        ).count()

        metrics.save()
        return metrics


class Author(models.Model):
    """Book authors"""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    website = models.URLField(blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        unique_together = ["first_name", "last_name"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Publisher(models.Model):
    """Book publishers"""

    name = models.CharField(max_length=200, unique=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Book(models.Model):
    """Book catalog entry"""

    AVAILABILITY_CHOICES = [
        ("available", "Available"),
        ("checked_out", "Checked Out"),
        ("reserved", "Reserved"),
        ("lost", "Lost"),
        ("damaged", "Damaged"),
        ("processing", "Processing"),
    ]

    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    isbn13 = models.CharField(max_length=13, unique=True, blank=True, null=True)

    authors = models.ManyToManyField(Author, related_name="books")
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, null=True, blank=True
    )
    genres = models.ManyToManyField(Genre, related_name="books")

    description = models.TextField(blank=True)
    publication_date = models.DateField(null=True, blank=True)
    edition = models.CharField(max_length=100, blank=True)
    pages = models.PositiveIntegerField(null=True, blank=True)
    language = models.CharField(max_length=50, default="English")

    cover_image = models.ImageField(upload_to="books/covers/", blank=True, null=True)
    sample_pages = models.FileField(upload_to="books/samples/", blank=True, null=True)

    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def available_copies(self):
        return self.copies.filter(status="available").count()

    @property
    def first_available_copy_id(self):
        available_copy = self.copies.filter(status="available").first()
        return available_copy.id if available_copy else None

    @property
    def total_copies(self):
        return self.copies.count()

    @property
    def authors_display(self):
        return ", ".join(author.full_name for author in self.authors.all())

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("catalog:book_detail", args=[self.slug])


class BookCopy(models.Model):
    """Physical/digital copies of books"""

    STATUS_CHOICES = [
        ("available", "Available"),
        ("checked_out", "Checked Out"),
        ("reserved", "Reserved"),
        ("lost", "Lost"),
        ("damaged", "Damaged"),
        ("processing", "Processing"),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="copies")
    copy_number = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True)
    qr_code = models.ImageField(upload_to="qrcodes/books/", blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="available"
    )
    condition = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)  # Shelf location
    acquisition_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    is_reference_only = models.BooleanField(default=False)

    class Meta:
        ordering = ["copy_number"]

    def save(self, *args, **kwargs):
        # Generate QR code if not exists
        if not self.qr_code and self.barcode:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def generate_qr_code(self):
        """Generate QR code for this book copy"""
        if not self.barcode:
            return

        # Create QR code data - could include book info and copy details
        qr_data = f"BOOK:{self.book.isbn or self.book.id}:COPY:{self.copy_number}:BARCODE:{self.barcode}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Save to model
        filename = f"book_{self.book.id}_copy_{self.copy_number}.png"
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

    def __str__(self):
        return f"{self.book.title} - Copy {self.copy_number}"


class Patron(models.Model):
    """Library patrons/members"""

    MEMBERSHIP_TYPES = [
        ("student", "Student"),
        ("faculty", "Faculty/Staff"),
        ("public", "Public Member"),
        ("special", "Special Access"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership_type = models.CharField(
        max_length=20, choices=MEMBERSHIP_TYPES, default="public"
    )
    membership_number = models.CharField(max_length=50, unique=True, blank=True)
    qr_code = models.ImageField(upload_to="qrcodes/patrons/", blank=True, null=True)

    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=200, blank=True)

    registration_date = models.DateTimeField(auto_now_add=True)
    membership_expiry = models.DateField(null=True, blank=True)

    max_books = models.PositiveIntegerField(default=5)
    max_loan_days = models.PositiveIntegerField(default=14)
    can_reserve = models.BooleanField(default=True)

    fines_owed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def save(self, *args, **kwargs):
        # Generate QR code if not exists and membership number is set
        if not self.qr_code and self.membership_number:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def generate_qr_code(self):
        """Generate QR code for this patron"""
        if not self.membership_number:
            return

        # Create QR code data - patron info for quick identification
        qr_data = f"PATRON:{self.membership_number}:NAME:{self.user.get_full_name()}:ID:{self.user.id}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Save to model
        filename = f"patron_{self.membership_number}.png"
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.membership_number})"

    @property
    def current_loans(self):
        return self.loans.filter(returned_date__isnull=True).count()

    @property
    def active_reservations(self):
        return self.reservations.filter(status="active").count()


class Loan(models.Model):
    """Book loan records"""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("returned", "Returned"),
        ("overdue", "Overdue"),
        ("lost", "Lost"),
    ]

    patron = models.ForeignKey(Patron, on_delete=models.CASCADE, related_name="loans")
    book_copy = models.ForeignKey(
        BookCopy, on_delete=models.CASCADE, related_name="loans"
    )
    loan_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    returned_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    # Fine calculation
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fine_paid = models.BooleanField(default=False)

    # Staff who processed the loan
    issued_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="issued_loans"
    )
    returned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="returned_loans",
    )

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-loan_date"]

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.loan_date + timedelta(days=self.patron.max_loan_days)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return self.status == "active" and timezone.now() > self.due_date

    def __str__(self):
        return f"{self.patron} - {self.book_copy} ({self.loan_date.date()})"


class Reservation(models.Model):
    """Book reservations/holds"""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("ready", "Ready for Pickup"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
        ("fulfilled", "Fulfilled"),
    ]

    patron = models.ForeignKey(
        Patron, on_delete=models.CASCADE, related_name="reservations"
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="reservations"
    )
    reservation_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    # Notification preferences
    notify_email = models.BooleanField(default=True)
    notify_sms = models.BooleanField(default=False)

    # When the reservation becomes ready
    ready_date = models.DateTimeField(null=True, blank=True)
    pickup_deadline = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-reservation_date"]

    def __str__(self):
        return f"{self.patron} reserved {self.book.title}"


class Fine(models.Model):
    """Fine records"""

    FINE_TYPES = [
        ("overdue", "Overdue Book"),
        ("lost", "Lost Book"),
        ("damaged", "Damaged Book"),
    ]

    patron = models.ForeignKey(Patron, on_delete=models.CASCADE, related_name="fines")
    loan = models.ForeignKey(
        Loan, on_delete=models.SET_NULL, null=True, blank=True, related_name="fines"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fine_type = models.CharField(max_length=20, choices=FINE_TYPES)
    description = models.TextField(blank=True)
    date_assessed = models.DateTimeField(default=timezone.now)
    date_paid = models.DateTimeField(null=True, blank=True)
    paid = models.BooleanField(default=False)

    # Payment details
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-date_assessed"]

    def __str__(self):
        return f"{self.patron} - {self.fine_type} - ${self.amount}"


class Notification(models.Model):
    """Email/SMS notification records"""

    NOTIFICATION_TYPES = [
        ("due_reminder", "Due Date Reminder"),
        ("overdue_notice", "Overdue Notice"),
        ("reservation_ready", "Reservation Ready"),
        ("reservation_expired", "Reservation Expired"),
        ("account_summary", "Account Summary"),
        ("welcome", "Welcome Message"),
    ]

    DELIVERY_METHODS = [
        ("email", "Email"),
        ("sms", "SMS"),
        ("both", "Email and SMS"),
    ]

    patron = models.ForeignKey(
        Patron, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    delivery_method = models.CharField(
        max_length=10, choices=DELIVERY_METHODS, default="email"
    )

    subject = models.CharField(max_length=200)
    message = models.TextField()

    # Related objects
    loan = models.ForeignKey(Loan, on_delete=models.SET_NULL, null=True, blank=True)
    reservation = models.ForeignKey(
        Reservation, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Status tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    # Scheduling
    scheduled_for = models.DateTimeField(null=True, blank=True)
    priority = models.PositiveIntegerField(default=1)  # 1=low, 2=medium, 3=high

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["patron", "notification_type"]),
            models.Index(fields=["scheduled_for", "sent_at"]),
        ]

    def __str__(self):
        return f"{self.patron} - {self.get_notification_type_display()}"

    @property
    def is_sent(self):
        return self.sent_at is not None

    @property
    def is_delivered(self):
        return self.delivered_at is not None

    @property
    def is_failed(self):
        return self.failed_at is not None


class NotificationTemplate(models.Model):
    """Templates for different types of notifications"""

    NOTIFICATION_TYPES = [
        ("due_reminder", "Due Date Reminder"),
        ("overdue_notice", "Overdue Notice"),
        ("reservation_ready", "Reservation Ready"),
        ("reservation_expired", "Reservation Expired"),
        ("account_summary", "Account Summary"),
        ("welcome", "Welcome Message"),
    ]

    name = models.CharField(max_length=100, unique=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    subject_template = models.CharField(
        max_length=200, help_text="Django template syntax supported"
    )
    message_template = models.TextField(help_text="Django template syntax supported")
    is_active = models.BooleanField(default=True)

    # Timing configuration
    days_before_due = models.PositiveIntegerField(
        null=True, blank=True, help_text="For due reminders"
    )
    days_overdue = models.PositiveIntegerField(
        null=True, blank=True, help_text="For overdue notices"
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["notification_type", "name"]

    def __str__(self):
        return self.name
