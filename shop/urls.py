from django.urls import path
from .views import ProductListView, TrendingProductListView, ProductDetailView

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("trending/", TrendingProductListView.as_view(), name="trending-products"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
]
