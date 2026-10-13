import django_filters
from django.db.models import Q
from .models import Shop


class ShopFilter(django_filters.FilterSet):
    # django-filter сам поймает ?search= в URL
    search = django_filters.CharFilter(method="filter_by_search", label="Поиск по названию и описанию")

    # min_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="gte") Примеры фильтрации на будущее
    # max_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="lte") Примеры на будущее

    # 2. Пример дополнительного фильтра (например, фильтр по конкретному статусу, если нужно)
    # is_active = django_filters.BooleanFilter(field_name='is_active')
    

    class Meta:
        model = Shop
        # Здесь указываем поля для точного совпадения, если они нужны (например, ?is_active=true)
        fields = []


    def filter_by_search(self, queryset, name, value):  # Так как вручную связали с методом, то в fields = [] прописывать не надо 
        if not value:
            return queryset
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))

