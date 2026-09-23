import hashlib
import random 
from django.core.exceptions import ValidationError

from django.utils import timezone
from datetime import timedelta

from django.db import models
from .models import VerificationPurpose, VerificationCode
from .tasks import send_email_code_verification


CODE_TTL_MINUTES = 5
CODE_CONFIRM_PASSWORD_RESET = 10
MAX_ATTEMPTS = 5


class VerificationCodeService:

    @staticmethod
    def _hash(raw_code):
        """Хэширует код для базы данных"""
        return hashlib.sha256(raw_code.encode()).hexdigest()


    @staticmethod
    def _generate_raw_code():
        """Создает 6-значный код для отправки на email"""
        return f"{random.randint(0, 999999):06d}"


    @classmethod
    def _issue_code(cls, user, purpose):
        """Общая функция, чтобы не повторяться, для удаления текущих не использованных кодов и создания нового"""
        VerificationCode.objects.filter(
            user=user,
            purpose=purpose,
            is_used=False,
        ).update(is_used=True)

        raw_code = cls._generate_raw_code()

        VerificationCode.objects.create(
            user=user, 
            purpose=purpose,
            code_hash=cls._hash(raw_code=raw_code),
            expires_at=timezone.now() + timedelta(minutes=CODE_TTL_MINUTES)
        )

        return raw_code


    @classmethod
    def _check_code(cls, user, purpose, raw_code):
        """Функция для проверки верификации кода"""
        verification = VerificationCode.objects.filter(
            user=user,
            purpose=purpose,
            is_used=False,
        ).order_by("-created_at").first()

        if verification is None:
            raise ValidationError("Код не найден, запросите новый")

        if verification.is_expired():
            raise ValidationError("Код истек, запросите новый")

        if verification.attempts >= MAX_ATTEMPTS:
            raise ValidationError("Количество попыток превышено, запросите новый код")

        if cls._hash(raw_code) != verification.code_hash:
            verification.attempts = models.F("attempts") + 1
            verification.save(update_fields=["attempts"])
            raise ValidationError("Неверный код")

        return verification


    @classmethod
    def send_verification_code(cls, user):
        code = cls._issue_code(user=user, purpose=VerificationPurpose.VERIFICATION)
        send_email_code_verification.delay(user.id, VerificationPurpose.VERIFICATION, code)


    @classmethod
    def send_password_reset_code(cls, user):
        code = cls._issue_code(user=user, purpose=VerificationPurpose.PASSWORD_RESET)
        send_email_code_verification.delay(user.id, VerificationPurpose.PASSWORD_RESET, code)


    @classmethod
    def verify_verification_code(cls, user, raw_code):
        verification = cls._check_code(user=user, purpose=VerificationPurpose.VERIFICATION, raw_code=raw_code)
        verification.is_used = True
        verification.save(update_fields=["is_used"])

        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])


    @classmethod
    def verify_password_reset_code(cls, user, raw_code):
        verification = cls._check_code(user=user, purpose=VerificationPurpose.PASSWORD_RESET, raw_code=raw_code)
        verification.verified_at = timezone.now()
        verification.save(update_fields=["verified_at"])


    @classmethod
    def check_verification_verified(cls, user):
        return user.is_email_verified


    @classmethod
    def check_password_reset_verified(cls, user):
        cut_off = timezone.now() - timedelta(minutes=CODE_CONFIRM_PASSWORD_RESET)
        return VerificationCode.objects.filter(
            user=user, 
            purpose=VerificationPurpose.PASSWORD_RESET,
            is_used=False,
            verified_at__isnull=False,
            verified_at__gt=cut_off,
        ).exists()


    @classmethod
    def consume_password_reset(cls, user):
        VerificationCode.objects.filter(
            user=user, 
            purpose=VerificationPurpose.PASSWORD_RESET,
            is_used=False,
            verified_at__isnull=False,
        ).update(is_used=True)

        
# Релаизовать функцию, которая хэширует 6-зныйчный код для бд 
# Реализовать функцию, которая создает 6-значный код в виде строки
# Реализовать функцию, которая создает код для отправки его на email, также которая удаляет все активные коды  
# Реализовать функцию, которая делает проверки кода, то есть берет код из бд и делает разные проверки и возвращает код 
# Реализовать функцию, которая отправляет код на маил для того и того способа
# Реализовать функцию, которая верифицирет коды 
# Реализовать функцию, которая проверяет верификацию кодов 
# Реализовать функцию, которая ставит флаг is_used=True для кодов сброса пароля