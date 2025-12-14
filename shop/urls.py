from django.urls import path

from .views import (
    ProductListView,
    TrendingProductListView,
    ProductDetailView,
    create_admin_once,
    AddressView,
)

from .auth_views import RegisterView
from .order_views import PlaceOrderView


urlpatterns = [
    # 🛒 Products
    path("products/", ProductListView.as_view(), name="product-list"),
    path("trending/", TrendingProductListView.as_view(), name="trending-products"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),

    # 📍 Address
    path("addresses/", AddressView.as_view(), name="address"),

    # 🔐 Authentication
    path("auth/register/", RegisterView.as_view(), name="register"),

    # 🧾 Orders
    path("orders/place/", PlaceOrderView.as_view(), name="place-order"),

    # ⚙️ Admin (one-time)
    path("create-admin/", create_admin_once, name="create-admin"),
]
