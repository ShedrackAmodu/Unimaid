from django.core.management.base import BaseCommand
from catalog.models import NotificationTemplate


class Command(BaseCommand):
    help = "Create default notification templates"

    def handle(self, *args, **options):
        templates_data = [
            {
                "name": "Due Date Reminder - 3 Days",
                "notification_type": "due_reminder",
                "subject_template": "Library Book Due Soon: {{ book.title }}",
                "message_template": """Dear {{ patron.user.get_full_name }},

This is a friendly reminder that the following book is due back to the library in {{ days_remaining }} days:

Book: {{ book.title }}
Due Date: {{ due_date|date:"F j, Y" }}
Loan Date: {{ loan.loan_date|date:"F j, Y" }}

Please return the book by the due date to avoid overdue fines. If you need to renew this book, please visit the library or contact us.

Thank you for using our library services!

Best regards,
University of Maiduguri Library
""",
                "days_before_due": 3,
            },
            {
                "name": "Due Date Reminder - 1 Day",
                "notification_type": "due_reminder",
                "subject_template": "URGENT: Library Book Due Tomorrow - {{ book.title }}",
                "message_template": """Dear {{ patron.user.get_full_name }},

URGENT REMINDER: The following book is due back to the library TOMORROW:

Book: {{ book.title }}
Due Date: {{ due_date|date:"F j, Y" }}
Loan Date: {{ loan.loan_date|date:"F j, Y" }}

Please return the book by the due date to avoid overdue fines of ${{ library_settings.OVERDUE_FINE_PER_DAY }} per day.

If you need to renew this book, please visit the library or contact us immediately.

Thank you for using our library services!

Best regards,
University of Maiduguri Library
""",
                "days_before_due": 1,
            },
            {
                "name": "Overdue Notice - 1 Day Late",
                "notification_type": "overdue_notice",
                "subject_template": "OVERDUE: Library Book Past Due - {{ book.title }}",
                "message_template": """Dear {{ patron.user.get_full_name }},

NOTICE: The following book is now OVERDUE and accruing fines:

Book: {{ book.title }}
Due Date: {{ due_date|date:"F j, Y" }}
Days Overdue: {{ days_overdue }}
Current Fine: ${{ fine_amount }}

Overdue fines are ${{ library_settings.OVERDUE_FINE_PER_DAY }} per day. Please return this book immediately to avoid additional charges.

If you have questions about your account or need to renew this book, please contact the library.

Thank you for your prompt attention to this matter.

Best regards,
University of Maiduguri Library
Circulation Department
""",
                "days_overdue": 1,
            },
            {
                "name": "Reservation Ready",
                "notification_type": "reservation_ready",
                "subject_template": "Your Reserved Book is Ready for Pickup: {{ book.title }}",
                "message_template": """Dear {{ patron.user.get_full_name }},

Great news! Your reserved book is now available for pickup:

Book: {{ book.title }}
Reservation Date: {{ reservation.reservation_date|date:"F j, Y" }}
Ready Date: {{ ready_date|date:"F j, Y" }}
Pickup Deadline: {{ pickup_deadline|date:"F j, Y" }}

Please pick up your reserved book within 7 days of the ready date. After this period, the book may be released to the next person on the waitlist.

You can pick up your book at the library circulation desk during operating hours.

Thank you for using our reservation service!

Best regards,
University of Maiduguri Library
""",
            },
            {
                "name": "Welcome Message",
                "notification_type": "welcome",
                "subject_template": "Welcome to University of Maiduguri Library!",
                "message_template": """Dear {{ patron.user.get_full_name }},

Welcome to the University of Maiduguri Library! Your library account has been successfully created.

Membership Details:
- Membership Type: {{ patron.get_membership_type_display }}
- Membership Number: {{ patron.membership_number }}
- Maximum Books: {{ patron.max_books }}
- Maximum Loan Days: {{ patron.max_loan_days }}

You can now:
- Browse and search our collection of books
- Place reservations for popular items
- Access your account online
- Renew books before they become due
- View your loan history and current loans

To get started, visit our website and log in with your account credentials.

If you have any questions, please don't hesitate to contact us.

Happy reading!

Best regards,
University of Maiduguri Library
library@unimaid.edu.ng
""",
            },
            {
                "name": "Weekly Account Summary",
                "notification_type": "account_summary",
                "subject_template": "Your Weekly Library Account Summary",
                "message_template": """Dear {{ patron.user.get_full_name }},

Here's your weekly account summary for the past 7 days:

CURRENT LOANS:
{% for loan in current_loans %}
- {{ loan.book_copy.book.title }} (Due: {{ loan.due_date|date:"M j, Y" }})
{% empty %}
No current loans
{% endfor %}

RECENT ACTIVITY:
{% if recent_loans %}
Recent Loans:
{% for loan in recent_loans %}
- Borrowed: {{ loan.book_copy.book.title }} ({{ loan.loan_date|date:"M j" }})
{% endfor %}
{% endif %}

{% if recent_reservations %}
Recent Reservations:
{% for reservation in recent_reservations %}
- Reserved: {{ reservation.book.title }} ({{ reservation.reservation_date|date:"M j" }})
{% endfor %}
{% endif %}

{% if recent_fines %}
Recent Fines:
{% for fine in recent_fines %}
- {{ fine.fine_type|title }}: ${{ fine.amount }} ({{ fine.date_assessed|date:"M j" }})
{% endfor %}
{% endif %}

Total Outstanding Fines: ${{ total_fines }}

Please remember to return books by their due dates to avoid overdue charges. You can renew books online or by contacting the library.

If you have any questions about your account, please contact us.

Thank you for being a valued library member!

Best regards,
University of Maiduguri Library
""",
            },
        ]

        created_count = 0
        for template_data in templates_data:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data["name"], defaults=template_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created template: {template.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Template already exists: {template.name}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {created_count} notification templates"
            )
        )
