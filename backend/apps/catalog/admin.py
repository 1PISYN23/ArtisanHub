from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Catalog


@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    # 1. Поля, которые отображаются в общем списке
    list_display = (
        "id",
        "name",
        "parent",
        "priority",
        "get_html_image",
        "slug",
        "created_at",
    )

    # 2. Поля, которые кликабельны для перехода в редактирование
    list_display_links = ("name",)

    # 3. Возможность быстро менять приоритет прямо из списка, не заходя внутрь записи
    list_editable = ("priority",)

    # 4. Поля, по которым работает поиск (по названию и по slug)
    search_fields = ("name", "slug")

    # 5. Боковые фильтры (по наличию родителя и дате создания)
    list_filter = (
        ("parent", admin.RelatedOnlyFieldListFilter),  # Покажет в фильтре только те категории, которые реально выбраны родителями
        "created_at",
    )

    # 6. Автоматическое заполнение slug из поля name при вводе (в режиме реального времени)
    prepopulated_fields = {"slug": ("name",)}

    # 7. Защита от огромных выпадающих списков, если категорий станет много
    raw_id_fields = ("parent",)

    # 8. Метод для красивого вывода миниатюры картинки в списке
    def get_html_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" style="object-fit: cover; border-radius: 4px;" />')
        return "—"
    
    get_html_image.short_description = "Миниатюра"
