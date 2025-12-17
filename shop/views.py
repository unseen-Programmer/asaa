from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import (
    Product,
    Address,
    Wishlist,
    Order,
    OrderItem,
)
from .serializers import (
    ProductSerializer,
    AddressSerializer,
    WishlistSerializer,
    OrderSerializer,
)
from .permissions import IsAuthenticatedWithAuth0


# ─────────────────────────────
# 🛒 PRODUCTS (PUBLIC)
# ─────────────────────────────
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class TrendingProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-view_count")[:10]
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        product = super().get_object()
        product.view_count += 1
        product.save(update_fields=["view_count"])
        return product


# ─────────────────────────────
# 📍 ADDRESS (AUTH0 USER)
# ─────────────────────────────
class AddressView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticatedWithAuth0]

    def get_queryset(self):
        return Address.objects.filter(
            auth0_user_id=self.request.auth0_user_id
        ).order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(
            auth0_user_id=self.request.auth0_user_id
        )


# ─────────────────────────────
# ❤️ WISHLIST (TOGGLE + LIST)
# ─────────────────────────────
class WishlistView(APIView):
    permission_classes = [IsAuthenticatedWithAuth0]

    def get(self, request):
        wishlist = Wishlist.objects.filter(
            auth0_user_id=request.auth0_user_id
        ).select_related("product")

        serializer = WishlistSerializer(wishlist, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        product_id = request.data.get("product_id")

        if not product_id:
            return Response(
                {"error": "product_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        wishlist_item = Wishlist.objects.filter(
            auth0_user_id=request.auth0_user_id,
            product_id=product_id
        ).first()

        if wishlist_item:
            wishlist_item.delete()
        else:
            Wishlist.objects.create(
                auth0_user_id=request.auth0_user_id,
                product_id=product_id
            )

        wishlist = Wishlist.objects.filter(
            auth0_user_id=request.auth0_user_id
        ).select_related("product")

        serializer = WishlistSerializer(wishlist, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ─────────────────────────────
# 🧾 PLACE ORDER
# ─────────────────────────────
class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticatedWithAuth0]

    def post(self, request):
        items = request.data.get("items", [])
        address_id = request.data.get("address_id")

        if not items or not address_id:
            return Response(
                {"error": "items and address_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = Order.objects.create(
            auth0_user_id=request.auth0_user_id,
            address_id=address_id,
            total_amount=0,
        )

        total = 0

        for item in items:
            OrderItem.objects.create(
                order=order,
                product_id=item["product_id"],
                price=item["price"],
                quantity=item["quantity"],
            )
            total += item["price"] * item["quantity"]

        order.total_amount = total
        order.save(update_fields=["total_amount"])

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ─────────────────────────────
# 📦 ORDER HISTORY
# ─────────────────────────────
class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedWithAuth0]

    def get_queryset(self):
        return Order.objects.filter(
            auth0_user_id=self.request.auth0_user_id
        ).order_by("-created_at")
