from django.urls import path

from .views import (
    ProductListView,
    TrendingProductListView,
    ProductDetailView,
    AddressView,
    WishlistView,
    PlaceOrderView,
    OrderHistoryView,
)

urlpatterns = [
    # 🛒 Products (PUBLIC)
    path("products/", ProductListView.as_view(), name="product-list"),
    path("trending/", TrendingProductListView.as_view(), name="trending-products"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),

    # 📍 Address (PROTECTED)
    path("addresses/", AddressView.as_view(), name="address"),

    # ❤️ Wishlist (PROTECTED)
    path("wishlist/", WishlistView.as_view(), name="wishlist"),

    # 🧾 Orders (PROTECTED)
    path("orders/place/", PlaceOrderView.as_view(), name="place-order"),
    path("orders/history/", OrderHistoryView.as_view(), name="order-history"),
]
