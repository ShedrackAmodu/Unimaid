from celery import shared_task
from django.core.mail import send_mail
from django.template import Template, Context
from django.utils import timezone
from django.conf import settings
from .models import (
    Notification,
    NotificationTemplate,
    Loan,
    Reservation,
    Patron,
    BookCopy,
)
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_notification_email(notification_id):
    """Send a single notification email"""
    try:
        notification = Notification.objects.get(id=notification_id)
        if notification.is_sent:
            logger.info(f"Notification {notification_id} already sent")
            return

        # Send email
        send_mail(
            subject=notification.subject,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.patron.user.email],
            fail_silently=False,
        )

        # Mark as sent
        notification.sent_at = timezone.now()
        notification.save()

        logger.info(f"Notification {notification_id} sent successfully")

    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
    except Exception as e:
        logger.error(f"Failed to send notification {notification_id}: {str(e)}")
        notification.failed_at = timezone.now()
        notification.error_message = str(e)
        notification.save()


@shared_task
def create_due_date_reminders():
    """Create due date reminder notifications"""
    from django.conf import settings

    # Get reminder templates
    templates = NotificationTemplate.objects.filter(
        notification_type="due_reminder", is_active=True
    )

    for template in templates:
        days_before = template.days_before_due
        if not days_before:
            continue

        # Calculate target date
        target_date = timezone.now() + timedelta(days=days_before)

        # Find loans due on target date
        due_loans = Loan.objects.filter(
            due_date__date=target_date.date(),
            status="active",
            returned_date__isnull=True,
        ).select_related("patron__user", "book_copy__book")

        for loan in due_loans:
            # Check if notification already exists
            existing = Notification.objects.filter(
                patron=loan.patron,
                notification_type="due_reminder",
                loan=loan,
                created_at__date=timezone.now().date(),
            ).exists()

            if not existing:
                # Create notification
                context = {
                    "patron": loan.patron,
                    "loan": loan,
                    "book": loan.book_copy.book,
                    "due_date": loan.due_date,
                    "days_remaining": days_before,
                }

                subject = render_template(template.subject_template, context)
                message = render_template(template.message_template, context)

                notification = Notification.objects.create(
                    patron=loan.patron,
                    notification_type="due_reminder",
                    delivery_method="email",
                    subject=subject,
                    message=message,
                    loan=loan,
                    scheduled_for=timezone.now(),
                    priority=2,  # Medium priority
                )

                # Send immediately
                send_notification_email.delay(notification.id)


@shared_task
def create_overdue_notices():
    """Create overdue notice notifications"""
    templates = NotificationTemplate.objects.filter(
        notification_type="overdue_notice", is_active=True
    )

    for template in templates:
        days_overdue = template.days_overdue or 1

        # Find overdue loans
        cutoff_date = timezone.now() - timedelta(days=days_overdue)
        overdue_loans = Loan.objects.filter(
            status="active", returned_date__isnull=True, due_date__lt=cutoff_date
        ).select_related("patron__user", "book_copy__book")

        for loan in overdue_loans:
            # Check if notification already sent today
            existing = Notification.objects.filter(
                patron=loan.patron,
                notification_type="overdue_notice",
                loan=loan,
                created_at__date=timezone.now().date(),
            ).exists()

            if not existing:
                days_overdue_actual = (timezone.now() - loan.due_date).days
                fine_amount = (
                    days_overdue_actual
                    * settings.LIBRARY_SETTINGS["OVERDUE_FINE_PER_DAY"]
                )

                context = {
                    "patron": loan.patron,
                    "loan": loan,
                    "book": loan.book_copy.book,
                    "due_date": loan.due_date,
                    "days_overdue": days_overdue_actual,
                    "fine_amount": fine_amount,
                }

                subject = render_template(template.subject_template, context)
                message = render_template(template.message_template, context)

                notification = Notification.objects.create(
                    patron=loan.patron,
                    notification_type="overdue_notice",
                    delivery_method="email",
                    subject=subject,
                    message=message,
                    loan=loan,
                    scheduled_for=timezone.now(),
                    priority=3,  # High priority
                )

                # Send immediately
                send_notification_email.delay(notification.id)


@shared_task
def create_reservation_ready_notifications():
    """Notify patrons when their reservations become ready"""
    template = NotificationTemplate.objects.filter(
        notification_type="reservation_ready", is_active=True
    ).first()

    if not template:
        return

    # Find reservations that became ready
    ready_reservations = Reservation.objects.filter(
        status="ready", ready_date__isnull=False
    ).select_related("patron__user", "book")

    for reservation in ready_reservations:
        # Check if notification already sent
        existing = Notification.objects.filter(
            patron=reservation.patron,
            notification_type="reservation_ready",
            reservation=reservation,
        ).exists()

        if not existing:
            pickup_deadline = reservation.pickup_deadline or (
                reservation.ready_date + timedelta(days=7)
            )

            context = {
                "patron": reservation.patron,
                "reservation": reservation,
                "book": reservation.book,
                "ready_date": reservation.ready_date,
                "pickup_deadline": pickup_deadline,
            }

            subject = render_template(template.subject_template, context)
            message = render_template(template.message_template, context)

            notification = Notification.objects.create(
                patron=reservation.patron,
                notification_type="reservation_ready",
                delivery_method="email",
                subject=subject,
                message=message,
                reservation=reservation,
                scheduled_for=timezone.now(),
                priority=2,
            )

            send_notification_email.delay(notification.id)


@shared_task
def send_welcome_notification(patron_id):
    """Send welcome notification to new patrons"""
    try:
        patron = Patron.objects.get(id=patron_id)
        template = NotificationTemplate.objects.filter(
            notification_type="welcome", is_active=True
        ).first()

        if template:
            context = {
                "patron": patron,
                "library_settings": settings.LIBRARY_SETTINGS,
            }

            subject = render_template(template.subject_template, context)
            message = render_template(template.message_template, context)

            notification = Notification.objects.create(
                patron=patron,
                notification_type="welcome",
                delivery_method="email",
                subject=subject,
                message=message,
                scheduled_for=timezone.now(),
                priority=1,
            )

            send_notification_email.delay(notification.id)

    except Patron.DoesNotExist:
        logger.error(f"Patron {patron_id} not found")


@shared_task
def send_weekly_account_summaries():
    """Send weekly account summary to all patrons"""
    template = NotificationTemplate.objects.filter(
        notification_type="account_summary", is_active=True
    ).first()

    if not template:
        return

    # Get all patrons with activity in the last week
    week_ago = timezone.now() - timedelta(days=7)
    active_patrons = Patron.objects.filter(
        models.Q(loans__loan_date__gte=week_ago)
        | models.Q(reservations__reservation_date__gte=week_ago)
        | models.Q(fines__date_assessed__gte=week_ago)
    ).distinct()

    for patron in active_patrons:
        # Gather account summary data
        recent_loans = patron.loans.filter(loan_date__gte=week_ago)[:5]
        recent_reservations = patron.reservations.filter(
            reservation_date__gte=week_ago
        )[:5]
        recent_fines = patron.fines.filter(date_assessed__gte=week_ago)[:5]
        current_loans = patron.loans.filter(returned_date__isnull=True)

        context = {
            "patron": patron,
            "recent_loans": recent_loans,
            "recent_reservations": recent_reservations,
            "recent_fines": recent_fines,
            "current_loans": current_loans,
            "total_fines": patron.fines_owed,
        }

        subject = render_template(template.subject_template, context)
        message = render_template(template.message_template, context)

        notification = Notification.objects.create(
            patron=patron,
            notification_type="account_summary",
            delivery_method="email",
            subject=subject,
            message=message,
            scheduled_for=timezone.now(),
            priority=1,
        )

        send_notification_email.delay(notification.id)


@shared_task
def process_scheduled_notifications():
    """Process notifications scheduled for sending"""
    now = timezone.now()

    # Get notifications ready to send
    notifications = Notification.objects.filter(
        scheduled_for__lte=now, sent_at__isnull=True, failed_at__isnull=True
    ).order_by("-priority", "scheduled_for")

    for notification in notifications:
        if notification.delivery_method in ["email", "both"]:
            send_notification_email.delay(notification.id)


def render_template(template_string, context_dict):
    """Render a Django template with context"""
    template = Template(template_string)
    context = Context(context_dict)
    return template.render(context)
