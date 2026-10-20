from django.contrib import admin
from django.utils.html import format_html
from .models import Shop


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    # Поля, которые будут отображаться в списке магазинов
    list_display = (
        "name",
        "owner",
        "get_logo_preview",
        "stripe_onboarding_complete",
        "rating_cached",
        "reviews_count_cached",
        "is_active",
        "created_at",
    )

    # Поля, по которым доступна фильтрация в правой панели
    list_filter = ("is_active", "stripe_onboarding_complete", "created_at")

    # Поля, по которым можно искать (owner__username позволит искать по имени пользователя)
    search_fields = ("name", "owner__name", "owner__email", "stripe_account_id")

    # Автоматическое заполнение slug на основе name при создании в админке
    prepopulated_fields = {"slug": ("name",)}

    # Поля, доступные только для чтения (кешированные данные и даты)
    readonly_fields = ("rating_cached", "reviews_count_cached", "created_at", "updated_at", "get_logo_preview")

    # Разделение полей на логические блоки внутри формы редактирования
    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "slug", "owner", "description", "is_active")
        }),
        ("Медиа", {
            "fields": ("logo", "get_logo_preview")
        }),
        ("Интеграция со Stripe", {
            "fields": ("stripe_account_id", "stripe_onboarding_complete"),
            "classes": ("collapse",),  # Блок можно будет сворачивать
        }),
        ("Статистика и Системные даты", {
            "fields": ("rating_cached", "reviews_count_cached", "created_at", "updated_at"),
        }),
    )

    # Кастомный метод для отображения маленького превью логотипа в списке и форме
    @admin.display(description="Превью логотипа")
    def get_logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 40px; border-radius: 4px;" />', obj.logo.url)
        return "Нет логотипа"
