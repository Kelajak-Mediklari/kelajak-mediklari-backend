from smtplib import SMTPServerDisconnected

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task(time_limit=600)
def send_email(subject: str, template_name: str, context: dict, receivers: list):
    """
    Send email with celery task.

    subject: email title
    template_name: rendering template
    context: variables that are being rendered in the email template
    receivers: List of email recipients

    usage:
        send_email.apply_async(
            kwargs={
                "subject": "Hello world!",
                "template_name" :"email/registration_code.html",
                "context": {"code": "1293412"},
                "receivers": ["jakhongirsv@gmail.com"]
                }
        )
    """

    html_content = render_to_string(template_name, context)
    try:
        send_mail(
            subject=subject,
            message="",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=receivers,
            fail_silently=False,
            html_message=html_content,
        )
    except OSError as e:
        return f"OS error. Email sending failed. {e}"
    except SMTPServerDisconnected as e:
        return f"SMTP server disconnected. Email sending failed. {e}"

    return "Email sent."
