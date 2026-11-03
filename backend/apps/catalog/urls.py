from django.urls import path
from .views import catalog_list_view


urlpatterns = [
    path("", catalog_list_view, name="catalog-list")
]
