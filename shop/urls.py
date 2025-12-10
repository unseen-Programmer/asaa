from django.urls import path
from .views import (
    ProductListView,
    TrendingProductListView,
    ProductDetailView,
    reset_admin_password
)

urlpatterns = [
    path("products/", ProductListView.as_view()),
    path("trending/", TrendingProductListView.as_view()),
    path("products/<slug:slug>/", ProductDetailView.as_view()),
    path("reset-admin/", reset_admin_password),   # ✅ THIS WAS MISSING
]
