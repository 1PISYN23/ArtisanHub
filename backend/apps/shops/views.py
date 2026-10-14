from rest_framework.response import Response
from rest_framework import generics, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view, OpenApiExample, OpenApiParameter
from rest_framework import serializers

from .serializers import (
    ShopListSerializer,
    ShopDetailSerizlier,
    MyShopSerializer,
    ShopCreateUpdateSerlizer
)
from .models import Shop
from .filters import ShopFilter
from .permissions import IsOwnerOrReadOnly
from .pagination import ShopPagination


# Схема для пагинированного ответа
class PaginatedShopResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField(help_text='Общее количество магазинов')
    next = serializers.URLField(allow_null=True, required=False, help_text='Ссылка на следующую страницу')
    previous = serializers.URLField(allow_null=True, required=False, help_text='Ссылка на предыдущую страницу')
    results = ShopListSerializer(many=True, help_text='Список магазинов')


@extend_schema_view(
    list=extend_schema(
        summary="Список активных магазинов",
        description="Возвращает пагинированный список всех активных магазинов с возможностью поиска, фильтрации и сортировки.",
        tags=["Магазины"],
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Поиск по названию или описанию',
                required=False,
            ),  
        ],
        responses={
            200: OpenApiResponse(
                response=PaginatedShopResponseSerializer,
                description="Успешный возврат списка магазинов. Структура пагинации генерируется автоматически."
            )
        }
    ),
    create=extend_schema(
        summary="Создать новый магазин",
        description="Создает новый магазин. Доступно только авторизованным пользователям с подтвержденным Email.",
        tags=["Магазины"],
        request=ShopCreateUpdateSerlizer,
        responses={
            201: OpenApiResponse(
                response=ShopCreateUpdateSerlizer,
                description="Магазин успешно создан"
            ),
            400: OpenApiResponse(
                description="Ошибка валидации данных (например, email не подтвержден или имя занято)",
                examples=[
                    OpenApiExample(
                        name="Email не подтвержден",
                        value={"error": "Ваш email не подтвержден."}
                    ),
                    OpenApiExample(
                        name="Ошибка заполнения полей",
                        value={"name": ["Обязательное поле.", "Магазин с таким именем уже существует."]}
                    )
                ]
            ),
            401: OpenApiResponse(description="Пользователь не авторизован")
        }
    )
)
class ShopsListCreateView(generics.ListCreateAPIView):
    queryset = Shop.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ShopFilter
    ordering_fields = ["name", "created_at", "reviews_count_cached", "rating_cached"]
    pagination_class = ShopPagination
    ordering = ["name"]


    def get_serializer_class(self):
        if self.request.method == "POST":
            return ShopCreateUpdateSerlizer
        return ShopListSerializer


@extend_schema_view(
    retrieve=extend_schema(
        summary="Детали магазина",
        description="Возвращает подробную информацию о конкретном магазине по его уникальному слагу.",
        tags=["Магазины"],
        request=ShopDetailSerizlier,
        responses={
            200: OpenApiResponse(response=ShopDetailSerizlier, description="Информация о магазине"),
            404: OpenApiResponse(description="Магазин не найден или не активен")
        }
    ),
    update=extend_schema(
        summary="Полное обновление магазина (PUT)",
        description="Обновляет все поля магазина. Доступно только владельцу магазина.",
        tags=["Магазины"],
        request=ShopCreateUpdateSerlizer,
        responses={
            200: OpenApiResponse(response=ShopCreateUpdateSerlizer, description="Магазин успешно обновлен"),
            400: OpenApiResponse(description="Ошибка валидации переданных данных"),
            403: OpenApiResponse(description="Вы не являетесь владельцем этого магазина")
        }
    ),
    partial_update=extend_schema(
        summary="Частичное обновление магазина (PATCH)",
        description="Обновляет только переданные поля магазина. Доступно только владельцу.",
        tags=["Магазины"],
        request=ShopCreateUpdateSerlizer,
        responses={
            200: OpenApiResponse(response=ShopCreateUpdateSerlizer, description="Поля магазина успешно обновлены"),
            403: OpenApiResponse(description="Вы не являетесь владельцем этого магазина")
        }
    ),
    destroy=extend_schema(
        summary="Мягкое удаление магазина (DELETE)",
        description="Деактивирует магазин (выставляет флаг `is_active=False`). Данные физически не удаляются. Доступно только владельцу.",
        tags=["Магазины"],
        responses={
            204: OpenApiResponse(description="Магазин успешно деактивирован (удален)"),
            403: OpenApiResponse(description="Вы не являетесь владельцем этого магазина")
        }
    )
)
class ShopDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shop.objects.select_related("owner")
    serializer_class = ShopDetailSerizlier
    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = "slug"


    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ShopCreateUpdateSerlizer
        return ShopDetailSerizlier

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


@extend_schema_view(
    retrieve=extend_schema(
        summary="Профиль личного магазина текущего пользователя",
        description="Возвращает детальную информацию о магазине, который принадлежит текущему авторизованному пользователю.",
        tags=["Личный кабинет магазина"],
        request=MyShopSerializer,
        responses={
            200: OpenApiResponse(response=MyShopSerializer, description="Данные вашего магазина"),
            401: OpenApiResponse(description="Вы не авторизованы")
        }
    ),
    update=extend_schema(
        summary="Обновить данные личного магазина (PUT)",
        description="Позволяет пользователю полностью обновить данные своего личного магазина.",
        tags=["Личный кабинет магазина"],
        request=MyShopSerializer,
        responses={
            200: OpenApiResponse(response=MyShopSerializer, description="Данные успешно обновлены")
        }
    ),
    partial_update=extend_schema(
        summary="Частично обновить данные личного магазина (PATCH)",
        description="Позволяет пользователю изменить отдельные поля своего магазина.",
        tags=["Личный кабинет магазина"],
        request=MyShopSerializer,
        responses={
            200: OpenApiResponse(response=MyShopSerializer, description="Поля успешно обновлены")
        }
    )
)
class MyShopView(generics.RetrieveUpdateAPIView):
    serializer_class = MyShopSerializer
    permission_classes = [IsAuthenticated]


    def get_object(self):
        return Shop.objects.select_related("owner").get(owner=self.request.user)
