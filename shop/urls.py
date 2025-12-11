from django.urls import path
from .views import (
    ProductListView,
    TrendingProductListView,
    ProductDetailView,
    create_admin_once,
    AddressView
)

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("trending/", TrendingProductListView.as_view(), name="trending-products"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),

    # NEW — save / fetch address
    path("addresses/", AddressView.as_view(), name="address-api"),

    path("create-admin/", create_admin_once, name="create-admin"),
]
