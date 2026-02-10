from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

import razorpay
import hmac
import hashlib
import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

from .models import Product, Address, Wishlist, Order, OrderItem
from .serializers import (
    ProductSerializer,
    AddressSerializer,
    WishlistSerializer,
    OrderSerializer,
)
from .permissions import IsAuthenticatedWithAuth0


# =================================================
# 🔐 SAFE RAZORPAY CLIENT (NO CRASH)
# =================================================
def get_razorpay_client():
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return None

    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


# =================================================
# 📍 ADDRESS
# =================================================
class AddressView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticatedWithAuth0]

    def get_queryset(self):
        return Address.objects.filter(
            auth0_user_id=self.request.auth0_user_id
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(auth0_user_id=self.request.auth0_user_id)


# =================================================
# 🛒 PRODUCTS (PUBLIC)
# =================================================
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.prefetch_related("images").order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class TrendingProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Product.objects.prefetch_related("images").order_by("-view_count")[:10]


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.prefetch_related("images")
    serializer_class = ProductSerializer
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        product = super().get_object()
        Product.objects.filter(id=product.id).update(
            view_count=product.view_count + 1
        )
        product.view_count += 1
        return product


# =================================================
# ❤️ WISHLIST
# =================================================
class WishlistView(APIView):
    permission_classes = [IsAuthenticatedWithAuth0]

    def get(self, request):
        wishlist = Wishlist.objects.filter(
            auth0_user_id=request.auth0_user_id
        ).select_related("product").prefetch_related("product__images")

        return Response(WishlistSerializer(wishlist, many=True).data)

    def post(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response({"error": "product_id required"}, status=400)

        item = Wishlist.objects.filter(
            auth0_user_id=request.auth0_user_id,
            product_id=product_id
        ).first()

        if item:
            item.delete()
        else:
            Wishlist.objects.create(
                auth0_user_id=request.auth0_user_id,
                product_id=product_id
            )

        wishlist = Wishlist.objects.filter(
            auth0_user_id=request.auth0_user_id
        ).select_related("product").prefetch_related("product__images")

        return Response(WishlistSerializer(wishlist, many=True).data)


# =================================================
# 🧾 PLACE ORDER
# =================================================
class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticatedWithAuth0]

    @transaction.atomic
    def post(self, request):
        items = request.data.get("items")
        address_id = request.data.get("address_id")

        if not items or not address_id:
            return Response(
                {"error": "items and address_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        address = Address.objects.filter(id=address_id).first()
        if not address:
            return Response({"error": "Address not found"}, status=404)

        if address.auth0_user_id != request.auth0_user_id:
            address.auth0_user_id = request.auth0_user_id
            address.save(update_fields=["auth0_user_id"])

        order = Order.objects.create(
            auth0_user_id=request.auth0_user_id,
            address=address,
            total_amount=0,
            payment_method="razorpay",
            status="pending",
        )

        total = 0
        for item in items:
            product = Product.objects.select_for_update().get(
                id=item["product_id"]
            )

            if product.stock < item["quantity"]:
                raise PermissionDenied("Insufficient stock")

            product.stock -= item["quantity"]
            product.save(update_fields=["stock"])

            OrderItem.objects.create(
                order=order,
                product=product,
                price=item["price"],
                quantity=item["quantity"],
            )

            total += item["price"] * item["quantity"]

        order.total_amount = total
        order.save(update_fields=["total_amount"])

        return Response(
            {"order_id": order.id, "total_amount": total},
            status=status.HTTP_201_CREATED
        )


# =================================================
# 📦 ORDER HISTORY
# =================================================
class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedWithAuth0]

    def get_queryset(self):
        return Order.objects.filter(
            auth0_user_id=self.request.auth0_user_id
        ).prefetch_related(
            "items__product",
            "items__product__images"
        )


# =================================================
# 💳 CREATE RAZORPAY ORDER
# =================================================
class RazorpayCreateOrderView(APIView):
    permission_classes = [IsAuthenticatedWithAuth0]

    def post(self, request):
        client = get_razorpay_client()
        if not client:
            return Response(
                {"error": "Razorpay not configured"},
                status=503
            )

        order_id = request.data.get("order_id")
        if not order_id:
            return Response({"error": "order_id required"}, status=400)

        order = Order.objects.filter(
            id=order_id,
            auth0_user_id=request.auth0_user_id
        ).first()

        if not order:
            return Response({"error": "Order not found"}, status=404)

        amount_paise = int(order.total_amount * 100)

        razorpay_order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
        })

        order.razorpay_order_id = razorpay_order["id"]
        order.save(update_fields=["razorpay_order_id"])

        return Response({
            "key": settings.RAZORPAY_KEY_ID,
            "amount": amount_paise,
            "currency": "INR",
            "razorpay_order_id": razorpay_order["id"],
        })


# =================================================
# ✅ VERIFY PAYMENT
# =================================================
class RazorpayVerifyPaymentView(APIView):
    permission_classes = [IsAuthenticatedWithAuth0]

    def post(self, request):
        client = get_razorpay_client()
        if not client:
            return Response(
                {"error": "Razorpay not configured"},
                status=503
            )

        data = request.data

        client.utility.verify_payment_signature({
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

        return Response({"status": "success"})


# =================================================
# 🔐 RAZORPAY WEBHOOK
# =================================================
@method_decorator(csrf_exempt, name="dispatch")
class RazorpayWebhookView(View):

    def post(self, request):
        if not settings.RAZORPAY_WEBHOOK_SECRET:
            return HttpResponse(status=200)

        signature = request.headers.get("X-Razorpay-Signature")
        payload = request.body

        expected_signature = hmac.new(
            settings.RAZORPAY_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, signature):
            return HttpResponse("Invalid signature", status=400)

        data = json.loads(payload)

        if data.get("event") == "payment.captured":
            payment = data["payload"]["payment"]["entity"]
            Order.objects.filter(
                razorpay_order_id=payment["order_id"]
            ).update(
                status="paid",
                razorpay_payment_id=payment["id"]
            )

        return HttpResponse(status=200)
