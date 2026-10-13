from django.urls import path
from views import (
    ShopsListCreateView,
    ShopDetailView,
    MyShopView
)


urlpatterns = [
    path("", ShopsListCreateView, name="shop-list"),
    path("<slug:slug>/", ShopDetailView, name="detail-shop"),
    path("my-shop/", MyShopView, name="my-shop")
]
