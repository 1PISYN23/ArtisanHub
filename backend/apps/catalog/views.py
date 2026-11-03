from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Catalog
from .serializers import CatalogSerializer


@extend_schema(
    summary="Список элементов каталога",
    description="Возвращает список элементов каталога.",
    tags=["Каталог"],
    request=CatalogSerializer,
    responses={
        200: OpenApiResponse(
            description="Список элементов каталога"
        ),
        400: OpenApiResponse(
            description="Неверный формат идентификатора"
        )
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def catalog_list_view(request):
    catalog_id = request.query_params.get("id", None)

    if catalog_id:
        try:
            valid_id = int(catalog_id)
            catalog_items = Catalog.objects.filter(parent__id=valid_id)
        except (ValueError, TypeError):
            return Response({
                "error": "Неверный формат идентификатора"
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        catalog_items = Catalog.objects.filter(parent__isnull=True)

    serializer = CatalogSerializer(catalog_items, many=True, context={"request": request})
    return Response(serializer.data, status=status.HTTP_200_OK)