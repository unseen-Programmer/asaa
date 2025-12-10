from django.urls import path
from .views import (
    ProductListView,
    TrendingProductListView,
    ProductDetailView,
    create_admin_once
)

urlpatterns = [
    path("products/", ProductListView.as_view()),
    path("trending/", TrendingProductListView.as_view()),
    path("products/<slug:slug>/", ProductDetailView.as_view()),
    path("create-admin/", create_admin_once),   # ✅ CREATE ADMIN
]
