from rest_framework import generics, status
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth.models import User

from .models import Product, Address
from .serializers import ProductSerializer, AddressSerializer


# ─────────────────────────────
# PRODUCT LIST
# ─────────────────────────────
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer


# ─────────────────────────────
# TRENDING PRODUCTS
# ─────────────────────────────
class TrendingProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-view_count")[:10]
    serializer_class = ProductSerializer


# ─────────────────────────────
# PRODUCT DETAIL
# ─────────────────────────────
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "slug"

    def get_object(self):
        product = super().get_object()
        product.view_count += 1
        product.save()
        return product


# ─────────────────────────────
# CREATE ADMIN ONCE (TEMP)
# ─────────────────────────────
def create_admin_once(request):
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


# ─────────────────────────────
# ADDRESS SAVE + GET VIEW
# ─────────────────────────────
class AddressView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer

    def get_queryset(self):
        client_id = self.request.query_params.get("client_id")
        if not client_id:
            return Address.objects.none()

        return Address.objects.filter(client_id=client_id).order_by("-updated_at")

    def create(self, request, *args, **kwargs):
        client_id = request.data.get("client_id")

        existing = Address.objects.filter(client_id=client_id).first()

        # Update if already exists
        if existing:
            serializer = AddressSerializer(existing, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Else create new
        return super().create(request, *args, **kwargs)
