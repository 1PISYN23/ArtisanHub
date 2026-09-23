from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import CustomUser


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_code_verification(self, user_id, purpose, code):
    if purpose == "verification":
        subject = "Код подтверждения верификации — ArtisanHub"
        title = "Добро пожаловать в ArtisanHub"
        message = "Для верификации введите следующий код подтверждения:"
    elif purpose == "password_reset":
        subject = "Код подтверждения для смены пароля"
        title = "Смена пароля"
        message = "Для смены пароля введите следующий код подтверждения:"

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return

    body_html = render_to_string("emails/verification_code.html", {
        "title": title,
        "message": message,
        "code": code,
    })
    
    try:
        send_mail(
            subject=subject,
            message="",
            html_message=body_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )
    except Exception as e:
        raise self.retry(exc=e)


@shared_task
def send_welcome_email(user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except Exception as e:
        return 

    body_html = render_to_string("emails/welcome.html", {
        "user": user,
    })

    send_mail(
        subject="Добро пожалоть в ArtisanHub",
        message="",
        html_message=body_html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email]
    )