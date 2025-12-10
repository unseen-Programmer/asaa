from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer

# ✅ PRODUCT LIST
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer


# ✅ TRENDING PRODUCTS
class TrendingProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-view_count")[:10]
    serializer_class = ProductSerializer


# ✅ PRODUCT DETAIL + VIEW COUNT INCREASE
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
# ✅ TEMPORARY ADMIN PASSWORD RESET (RENDER FREE FIX)
# -------------------------------------------------------

from django.http import JsonResponse
from django.contrib.auth.models import User

def reset_admin_password(request):
    try:
        user = User.objects.get(username="admin")
        user.set_password("admin123")
        user.save()
        return JsonResponse({
            "status": "Password reset successful",
            "username": "admin",
            "new_password": "admin123"
        })
    except User.DoesNotExist:
        return JsonResponse({"error": "Admin user does not exist"})
