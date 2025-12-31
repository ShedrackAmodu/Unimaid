from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Book, BookCopy, Patron, Loan, Reservation, Author, Publisher, Genre


class PatronRegistrationForm(UserCreationForm):
    """Form for patron registration"""

    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    membership_type = forms.ChoiceField(
        choices=Patron.MEMBERSHIP_TYPES, initial="public", required=True
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()
            # Create associated Patron profile
            Patron.objects.create(
                user=user,
                phone=self.cleaned_data.get("phone"),
                address=self.cleaned_data.get("address"),
                membership_type=self.cleaned_data["membership_type"],
            )
        return user


class BookForm(forms.ModelForm):
    """Form for adding/editing books"""

    authors = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "select2"}),
        help_text="Hold Ctrl (Cmd on Mac) to select multiple authors",
    )
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "select2"}),
        help_text="Hold Ctrl (Cmd on Mac) to select multiple genres",
    )

    class Meta:
        model = Book
        fields = [
            "title",
            "isbn",
            "isbn13",
            "authors",
            "publisher",
            "genres",
            "description",
            "publication_date",
            "edition",
            "pages",
            "language",
            "cover_image",
            "sample_pages",
        ]
        widgets = {
            "publication_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class AuthorForm(forms.ModelForm):
    """Form for adding/editing authors"""

    class Meta:
        model = Author
        fields = [
            "first_name",
            "last_name",
            "bio",
            "birth_date",
            "death_date",
            "website",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "death_date": forms.DateInput(attrs={"type": "date"}),
            "bio": forms.Textarea(attrs={"rows": 3}),
        }


class PublisherForm(forms.ModelForm):
    """Form for adding/editing publishers"""

    class Meta:
        model = Publisher
        fields = ["name", "address", "website", "contact_email"]


class GenreForm(forms.ModelForm):
    """Form for adding/editing genres"""

    class Meta:
        model = Genre
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class BookCopyForm(forms.ModelForm):
    """Form for adding/editing book copies"""

    class Meta:
        model = BookCopy
        fields = [
            "book",
            "copy_number",
            "barcode",
            "status",
            "condition",
            "location",
            "acquisition_date",
            "purchase_price",
            "is_reference_only",
        ]
        widgets = {
            "acquisition_date": forms.DateInput(attrs={"type": "date"}),
        }


class LoanForm(forms.ModelForm):
    """Form for creating loans"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available book copies
        self.fields["book_copy"].queryset = BookCopy.objects.filter(status="available")

    class Meta:
        model = Loan
        fields = ["patron", "book_copy", "due_date", "notes"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class ReturnForm(forms.Form):
    """Form for returning books"""

    book_copy = forms.ModelChoiceField(
        queryset=BookCopy.objects.filter(status="checked_out"),
        widget=forms.HiddenInput(),
    )
    condition = forms.ChoiceField(
        choices=[
            ("good", "Good"),
            ("fair", "Fair"),
            ("poor", "Poor"),
            ("damaged", "Damaged"),
        ],
        initial="good",
    )
    notes = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 2, "placeholder": "Optional notes about the return"}
        ),
        required=False,
    )


class ReservationForm(forms.ModelForm):
    """Form for creating reservations"""

    class Meta:
        model = Reservation
        fields = ["book", "notify_email", "notify_sms", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class SearchForm(forms.Form):
    """Enhanced advanced search form with faceted filters"""

    query = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search by title, author, ISBN...",
                "class": "form-control",
            }
        ),
    )
    author = forms.ModelChoiceField(
        queryset=Author.objects.all().order_by("last_name", "first_name"),
        required=False,
        empty_label="All Authors",
        widget=forms.Select(attrs={"class": "form-control select2"}),
    )
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all().order_by("name"),
        required=False,
        empty_label="All Genres",
        widget=forms.Select(attrs={"class": "form-control select2"}),
    )
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all().order_by("name"),
        required=False,
        empty_label="All Publishers",
        widget=forms.Select(attrs={"class": "form-control select2"}),
    )
    language = forms.ChoiceField(
        choices=[
            ("", "All Languages"),
            ("English", "English"),
            ("French", "French"),
            ("Spanish", "Spanish"),
            ("German", "German"),
            ("Arabic", "Arabic"),
            ("Hausa", "Hausa"),
            ("Yoruba", "Yoruba"),
            ("Other", "Other"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    availability = forms.ChoiceField(
        choices=[
            ("", "All Books"),
            ("available", "Available Only"),
            ("checked_out", "Checked Out"),
            ("reserved", "Reserved"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    # Publication year range
    pub_year_from = forms.IntegerField(
        required=False,
        min_value=1000,
        max_value=2100,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "From year"}
        ),
    )
    pub_year_to = forms.IntegerField(
        required=False,
        min_value=1000,
        max_value=2100,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "To year"}
        ),
    )

    # Page count range
    pages_from = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min pages"}
        ),
    )
    pages_to = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max pages"}
        ),
    )

    # Format (for future digital content)
    format_type = forms.ChoiceField(
        choices=[
            ("", "All Formats"),
            ("physical", "Physical Books"),
            ("digital", "Digital Content"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    sort_by = forms.ChoiceField(
        choices=[
            ("relevance", "Relevance"),
            ("title", "Title A-Z"),
            ("title_desc", "Title Z-A"),
            ("date_added", "Recently Added"),
            ("publication_date", "Publication Date"),
            ("publication_date_desc", "Publication Date (Newest)"),
            ("author", "Author A-Z"),
            ("author_desc", "Author Z-A"),
            ("pages", "Page Count (Low to High)"),
            ("pages_desc", "Page Count (High to Low)"),
        ],
        initial="relevance",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class PatronProfileForm(forms.ModelForm):
    """Form for patrons to edit their profile"""

    class Meta:
        model = Patron
        fields = [
            "phone",
            "address",
            "date_of_birth",
            "emergency_contact",
            "max_books",
            "max_loan_days",
            "can_reserve",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }


class FinePaymentForm(forms.Form):
    """Form for paying fines"""

    fine_ids = forms.CharField(widget=forms.HiddenInput())
    payment_method = forms.ChoiceField(
        choices=[
            ("cash", "Cash"),
            ("card", "Card"),
            ("online", "Online"),
        ]
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.01"}),
    )
