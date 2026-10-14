from django.urls import path
from .views import (
    ShopsListCreateView,
    ShopDetailView,
    MyShopView
)


urlpatterns = [
    path("", ShopsListCreateView.as_view(), name="shop-list"),
    path("my-shop/", MyShopView.as_view(), name="my-shop"),
    path("<slug:slug>/", ShopDetailView.as_view(), name="detail-shop")
]
