from django.urls import path

from .views import (
    ProductListView,
    TrendingProductListView,
    ProductDetailView,
    AddressView,
    create_admin_once,
)

from .order_views import PlaceOrderView


urlpatterns = [
    # 🛒 PRODUCTS (PUBLIC)
    path("products/", ProductListView.as_view(), name="product-list"),
    path("trending/", TrendingProductListView.as_view(), name="trending-products"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),

    # 📍 ADDRESS (PROTECTED – AUTH0)
    path("addresses/", AddressView.as_view(), name="address"),

    # 🧾 ORDERS (PROTECTED – AUTH0)
    path("orders/place/", PlaceOrderView.as_view(), name="place-order"),

    # ⚙️ ADMIN (DEV ONLY)
    path("create-admin/", create_admin_once, name="create-admin"),
]
