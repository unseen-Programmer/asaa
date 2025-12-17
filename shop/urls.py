from django.urls import path

from .views import (
    ProductListView,
    TrendingProductListView,
    ProductDetailView,
    AddressView,
)

from .auth_views import RegisterView
from .order_views import PlaceOrderView


urlpatterns = [
    # 🛒 Products (PUBLIC)
    path("products/", ProductListView.as_view(), name="product-list"),
    path("trending/", TrendingProductListView.as_view(), name="trending-products"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),

    # 📍 Address (PROTECTED - Auth0)
    path("addresses/", AddressView.as_view(), name="address"),

    # 🔐 Authentication
    path("auth/register/", RegisterView.as_view(), name="register"),

    # 🧾 Orders (PROTECTED - Auth0)
    path("orders/place/", PlaceOrderView.as_view(), name="place-order"),
]
