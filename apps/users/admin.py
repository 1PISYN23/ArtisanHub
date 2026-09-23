from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, VerificationCode, VerificationPurpose


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ["email", "first_name", "last_name", "is_email_verified", "is_active", "date_joined"]
    list_filter = ["is_active", "is_superuser", "is_staff"]
    search_fields = ["email", "first_name", "last_name", "phone"]
    ordering = ["-date_joined"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "avatar", "phone")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")})
    )

    readonly_fields = ["date_joined"]


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "purpose",
        "attempts",
        "is_used",
        "is_expired_status",
        "created_at",
        "expires_at",
        "verified_at",
    )
    list_filter = ("purpose", "is_used", "created_at")
    search_fields = ("user__email", "purpose")
    readonly_fields = ("code_hash", "created_at", "verified_at")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "purpose",
                    "code_hash",
                )
            },
        ),
        (
            "Статус и попытки",
            {
                "fields": (
                    "attempts",
                    "is_used",
                )
            },
        ),
        (
            "Временные метки",
            {
                "fields": (
                    "created_at",
                    "expires_at",
                    "verified_at",
                )
            },
        ),
    )

    @admin.display(boolean=True, description="Истек?")
    def is_expired_status(self, obj):
        """Отображает статус протухания кода в виде иконки (галочка/крестик)"""
        return obj.is_expired()