from django.urls import path

from .views import (
    # 🛒 Products
    ProductListView,
    TrendingProductListView,
    ProductDetailView,

    # 📍 Address
    AddressView,

    # ❤️ Wishlist
    WishlistView,

    # 🧾 Orders
    PlaceOrderView,
    OrderHistoryView,

    # 💳 Razorpay
    RazorpayCreateOrderView,
    RazorpayVerifyPaymentView,
)

urlpatterns = [
    # ─────────────────────────
    # 🛒 PRODUCTS (PUBLIC)
    # ─────────────────────────
    path("products/", ProductListView.as_view(), name="product-list"),
    path("trending/", TrendingProductListView.as_view(), name="trending-products"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),

    # ─────────────────────────
    # 📍 ADDRESS (AUTH0)
    # ─────────────────────────
    path("addresses/", AddressView.as_view(), name="address"),

    # ─────────────────────────
    # ❤️ WISHLIST
    # ─────────────────────────
    path("wishlist/", WishlistView.as_view(), name="wishlist"),

    # ─────────────────────────
    # 🧾 ORDERS
    # ─────────────────────────
    path("orders/place/", PlaceOrderView.as_view(), name="place-order"),
    path("orders/history/", OrderHistoryView.as_view(), name="order-history"),

    # ─────────────────────────
    # 💳 RAZORPAY PAYMENTS
    # ─────────────────────────
    path("payment/razorpay/create/", RazorpayCreateOrderView.as_view(), name="razorpay-create"),
    path("payment/razorpay/verify/", RazorpayVerifyPaymentView.as_view(), name="razorpay-verify"),
]
