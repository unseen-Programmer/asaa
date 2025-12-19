from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

import razorpay
from django.conf import settings

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


# -------------------------------------------------
# RAZORPAY CLIENT
# -------------------------------------------------
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


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
# 🧾 PLACE ORDER (CREATE DB ORDER)
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
            status="pending",
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


# ─────────────────────────────
# 💳 RAZORPAY: CREATE PAYMENT ORDER
# ─────────────────────────────
class RazorpayCreateOrderView(APIView):
    permission_classes = [IsAuthenticatedWithAuth0]

    def post(self, request):
        amount = request.data.get("amount")

        if not amount:
            return Response(
                {"error": "amount is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        amount_paise = int(float(amount) * 100)

        razorpay_order = razorpay_client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "payment_capture": 1,
        })

        order = Order.objects.create(
            auth0_user_id=request.auth0_user_id,
            total_amount=amount,
            payment_method="razorpay",
            razorpay_order_id=razorpay_order["id"],
            status="pending",
        )

        return Response({
            "order_id": razorpay_order["id"],
            "amount": razorpay_order["amount"],
            "key": settings.RAZORPAY_KEY_ID,
            "order_db_id": order.id,
        }, status=status.HTTP_201_CREATED)


# ─────────────────────────────
# 💳 RAZORPAY: VERIFY PAYMENT
# ─────────────────────────────
class RazorpayVerifyPaymentView(APIView):
    permission_classes = [IsAuthenticatedWithAuth0]

    def post(self, request):
        data = request.data

        try:
            razorpay_client.utility.verify_payment_signature({
                "razorpay_order_id": data["razorpay_order_id"],
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_signature": data["razorpay_signature"],
            })

            order = Order.objects.get(
                razorpay_order_id=data["razorpay_order_id"]
            )

            order.razorpay_payment_id = data["razorpay_payment_id"]
            order.razorpay_signature = data["razorpay_signature"]
            order.status = "paid"
            order.save(update_fields=[
                "razorpay_payment_id",
                "razorpay_signature",
                "status"
            ])

            return Response(
                {"status": "success"},
                status=status.HTTP_200_OK
            )

        except Exception:
            return Response(
                {"status": "failed"},
                status=status.HTTP_400_BAD_REQUEST
            )
