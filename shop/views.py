from rest_framework import generics
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Product
from .serializers import ProductSerializer


# -------------------------------------------------------
# ✅ PRODUCT LIST (latest products first)
# -------------------------------------------------------
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer


# -------------------------------------------------------
# ✅ TRENDING PRODUCTS (based on view_count)
# -------------------------------------------------------
class TrendingProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-view_count")[:10]
    serializer_class = ProductSerializer


# -------------------------------------------------------
# ✅ PRODUCT DETAIL (increments view count)
# -------------------------------------------------------
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "slug"

    def get_object(self):
        product = super().get_object()
        product.view_count += 1
        product.save()
        return product


# -------------------------------------------------------
# ✅ TEMPORARY ROUTE — CREATE ADMIN ONE TIME
# -------------------------------------------------------
def create_admin_once(request):
    """
    Creates admin: username=admin, password=admin123
    Only works once. Safe to remove after use.
    """
    if User.objects.filter(username="admin").exists():
        return JsonResponse({"status": "Admin already exists"})

    User.objects.create_superuser(
        username="admin",
        password="admin123",
        email="admin@ane.com"
    )

    return JsonResponse({
        "status": "Admin created successfully",
        "username": "admin",
        "password": "admin123"
    })
