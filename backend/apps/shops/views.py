from django.shortcuts import get_object_or_404
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
    queryset = Shop.objects.filter(is_active=True).select_related("owner")
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
        return get_object_or_404(Shop.objects.select_related("owner"), owner=self.request.user)
    
































































    @extend_schema(
    operation_id="products_list",
    summary="Список продуктов",
    description="Возвращает список всех продуктов с возможностью фильтрации и пагинацией. Требуется аутентификация.",
    tags=["продукты"],
    parameters=[
        OpenApiParameter(
            name='category',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY,
            description='Фильтр по категории (UUID каталога). Возвращает продукты из указанного каталога и всех его дочерних каталогов',
            required=False,
        ),
        OpenApiParameter(
            name='brand',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Фильтр по брендам. Можно указать несколько параметров: ?brand=Nike&brand=Adidas',
            required=False,
            many=True,
        ),
        OpenApiParameter(
            name='search',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Поиск по названию или артикулу',
            required=False,
        ),
        OpenApiParameter(
            name='promo',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Фильтр по промо-товарам (true/false)',
            required=False,
        ),
        OpenApiParameter(
            name='new',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Фильтр по новинкам (true/false)',
            required=False,
        ),
        OpenApiParameter(
            name='in_stock',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Фильтр по наличию товара на складе (true - только товары в наличии, stock > 0)',
            required=False,
        ),
        OpenApiParameter(
            name='favorites',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Фильтр по избранному текущего пользователя (true — только избранные, false — не избранные)',
            required=False,
        ),
        OpenApiParameter(
            name='page',
            type=int,
            location=OpenApiParameter.QUERY,
            description='Номер страницы (по умолчанию 1)',
            required=False,
        ),
        OpenApiParameter(
            name='page_size',
            type=int,
            location=OpenApiParameter.QUERY,
            description='Количество элементов на странице (по умолчанию 20, максимум 100)',
            required=False,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=PaginatedProductResponseSerializer,
            description="Список продуктов с пагинацией"
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_list_view(request):
    """
    Возвращает список всех продуктов с возможностью фильтрации и пагинацией.
    
    Поддерживаемые параметры:
    - category: фильтр по категории (UUID каталога). Возвращает продукты из указанного каталога и всех его дочерних каталогов
    - brand: фильтр по брендам (можно указать несколько параметров: ?brand=Nike&brand=Adidas)
    - search: поиск по названию или артикулу
    - promo: фильтр по промо-товарам (true/false)
    - new: фильтр по новинкам (true/false)
    - in_stock: фильтр по наличию товара на складе (true - только товары в наличии, stock > 0)
    - favorites: фильтр по избранному пользователя (true - только избранные, false - не избранные)
    - page: номер страницы (по умолчанию 1)
    - page_size: количество элементов на странице (по умолчанию 20, максимум 100)
    """
    products = Product.objects.filter(parent_products_q())

    # Фильтр по категории (UUID каталога)
    category = request.query_params.get('category')
    if category:
        try:
            import uuid
            category_uuid = uuid.UUID(category)
        except (ValueError, TypeError):
            # Неверный формат UUID - возвращаем пустой результат
            products = products.none()
        else:
            # Находим все дочерние каталоги (где id_parent_1c равен переданному UUID)
            child_catalogs = Catalog.objects.filter(id_parent_1c=category_uuid)
            child_catalog_ids = list(child_catalogs.values_list('id_1c', flat=True))

            # Фильтруем None значения и преобразуем UUID в строки
            category_ids_str = [str(cat_id) for cat_id in child_catalog_ids if cat_id is not None]
            
            # Добавляем сам родительский каталог в список для фильтрации
            parent_catalog = Catalog.objects.filter(id_1c=category_uuid).first()
            if parent_catalog:
                category_ids_str.append(str(category_uuid))
            
            if category_ids_str:
                # Фильтруем продукты по всем найденным ID каталогов (включая родительский)
                products = products.filter(category__in=category_ids_str)
            else:
                # Если каталог не найден или нет дочерних каталогов, возвращаем пустой результат
                products = products.none()

    # Фильтр по брендам (может быть несколько параметров brand)
    brands_list = request.query_params.getlist('brand')
    if brands_list:
        # Очищаем от пробелов и фильтруем пустые значения
        brands_list = [b.strip() for b in brands_list if b.strip()]
        if brands_list:
            # Используем Q объект для фильтрации по нескольким брендам (OR)
            brand_filter = Q()
            for brand in brands_list:
                brand_filter |= Q(brand__iexact=brand)
            products = products.filter(brand_filter)

    # Поиск по названию или артикулу
    search = request.query_params.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(article__icontains=search)
        )

    # Фильтр по промо-товарам
    promo = request.query_params.get('promo')
    if promo is not None:
        promo_bool = promo.lower() in ('true', '1', 'yes', 'да') if isinstance(promo, str) else bool(promo)
        products = products.filter(promo=promo_bool)

    # Фильтр по новинкам
    new = request.query_params.get('new')
    if new is not None:
        new_bool = new.lower() in ('true', '1', 'yes', 'да') if isinstance(new, str) else bool(new)
        products = products.filter(new=new_bool)

    # Фильтр по наличию товара на складе
    in_stock = request.query_params.get('in_stock')
    if in_stock is not None:
        in_stock_bool = in_stock.lower() in ('true', '1', 'yes', 'да') if isinstance(in_stock, str) else bool(in_stock)
        if in_stock_bool:
            # Получаем код склада пользователя
            warehouse_code = _get_warehouse_code_from_request(request)
            if warehouse_code is not None:
                # Фильтруем продукты, у которых есть stock > 0 на этом складе
                products_in_stock = Stock.objects.filter(
                    warehouse_code=warehouse_code,
                    stock__gt=0
                ).values_list('article', flat=True)
                products = products.filter(article__in=products_in_stock)
            else:
                # Если не удалось определить склад, возвращаем пустой результат
                products = products.none()

    # Фильтр по избранному текущего пользователя
    favorites_param = request.query_params.get('favorites')
    if favorites_param is not None:
        favorites_bool = (
            favorites_param.lower() in ('true', '1', 'yes', 'да')
            if isinstance(favorites_param, str)
            else bool(favorites_param)
        )
        in_favorites = Exists(
            FavoriteProduct.objects.filter(
                user=request.user,
                product_id=OuterRef('pkid'),
            )
        )
        if favorites_bool:
            products = products.filter(in_favorites)
        else:
            products = products.exclude(in_favorites)

    # Сортировка: сначала товары в наличии, потом отсутствующие
    # Получаем код склада пользователя для определения наличия
    warehouse_code = _get_warehouse_code_from_request(request)
    if warehouse_code is not None:
        # Аннотируем продукты флагом наличия на складе
        # 0 = в наличии (stock > 0), 1 = отсутствует (stock = 0 или нет записи)
        products = products.annotate(
            is_in_stock=Case(
                When(
                    Exists(
                        Stock.objects.filter(
                            article=OuterRef('article'),
                            warehouse_code=warehouse_code,
                            stock__gt=0
                        )
                    ),
                    then=0  # В наличии
                ),
                default=1,  # Отсутствует
                output_field=IntegerField()
            )
        ).order_by('is_in_stock', '-created_at')
    else:
        # Если не удалось определить склад, сортируем только по дате создания
        products = products.order_by('-created_at')
    
    # Оптимизируем запросы: prefetch изображений товаров
    products = products.prefetch_related('images')
    
    # Применяем пагинацию
    paginator = ProductPagination()
    paginated_products = paginator.paginate_queryset(products, request)
    
    product_context = {
        'request': request,
        'favorite_articles': favorite_articles_for_user(request.user),
    }
    if paginated_products is not None:
        serializer = ProductSerializer(
            paginated_products,
            many=True,
            context=product_context,
        )
        return paginator.get_paginated_response(serializer.data)
    
    # Если пагинация не применена (не должно произойти, но на всякий случай)
    serializer = ProductSerializer(products, many=True, context=product_context)
    return Response(serializer.data, status=status.HTTP_200_OK)