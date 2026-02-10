from django.urls import path
from .views import (
    ProductListView,
    TrendingProductListView,
    ProductDetailView,
    AddressView,
    WishlistView,
    PlaceOrderView,
    OrderHistoryView,
    RazorpayCreateOrderView,
    RazorpayVerifyPaymentView,
    RazorpayWebhookView,
)

urlpatterns = [
    # 🛍 Products
    path("products/", ProductListView.as_view(), name="products"),
    path("products/trending/", TrendingProductListView.as_view(), name="trending-products"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),

    # 📍 Address
    path("addresses/", AddressView.as_view(), name="addresses"),

    # ❤️ Wishlist
    path("wishlist/", WishlistView.as_view(), name="wishlist"),

    # 🧾 Orders
    path("orders/place/", PlaceOrderView.as_view(), name="place-order"),
    path("orders/history/", OrderHistoryView.as_view(), name="order-history"),

    # 💳 Razorpay
    path("payments/razorpay/create/", RazorpayCreateOrderView.as_view(), name="razorpay-create"),
    path("payments/razorpay/verify/", RazorpayVerifyPaymentView.as_view(), name="razorpay-verify"),
    path("payments/razorpay/webhook/", RazorpayWebhookView.as_view(), name="razorpay-webhook"),
]
