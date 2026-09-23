from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email: 
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Имя")
    last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Фамилия")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Номер телефона")
    avatar = models.ImageField(upload_to="avatar/", blank=True, null=True, verbose_name="Аватар")

    is_email_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower().strip()
        super().save(*args, **kwargs)
        

    def __str__(self):
        return self.email


class VerificationPurpose(models.TextChoices):
    VERIFICATION = "verification", "Верификация"
    PASSWORD_RESET = "password_reset", "Сброс пароля"


class VerificationCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="verification_codes")
    purpose = models.CharField(max_length=20, choices=VerificationPurpose.choices)
    code_hash = models.CharField(max_length=64)

    attempts = models.PositiveSmallIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    verified_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()


    class Meta:
        verbose_name = "Код для верификации"
        verbose_name_plural = "Коды для верификции"
        indexes = [
            models.Index(fields=["user", "purpose", "is_used"])
        ]


    def __str__(self):
        return f"{self.user} - {self.purpose}"


    def is_expired(self):
        return self.expires_at < timezone.now()