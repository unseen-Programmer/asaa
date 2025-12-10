from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer


class TrendingProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-view_count")[:10]
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "slug"

    def get_object(self):
        product = super().get_object()
        product.view_count += 1
        product.save()
        return product
