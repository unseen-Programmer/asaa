from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

import razorpay
import hmac
import hashlib
import json
from django.core.exceptions import PermissionDenied

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction

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


# =================================================
# 🔐 RAZORPAY CLIENT
# =================================================
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


# =================================================
# 📍 ADDRESS (AUTH0 ONLY)
# =================================================
class AddressView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticatedWithAuth0]

    def get_queryset(self):
        return Address.objects.filter(
            auth0_user_id=self.request.auth0_user_id
        )

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

        serializer = WishlistSerializer(wishlist, many=True)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get("product_id")

        if not product_id:
            return Response(
                {"error": "product_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        wishlist_item = Wishlist.objects.filter(
            auth0_user_id=request.auth0_user_id,
            product_id=product_id,
        ).first()

        if wishlist_item:
            wishlist_item.delete()
        else:
            Wishlist.objects.create(
                auth0_user_id=request.auth0_user_id,
                product_id=product_id,
            )

        wishlist = Wishlist.objects.filter(
            auth0_user_id=request.auth0_user_id
        ).select_related("product").prefetch_related("product__images")

        serializer = WishlistSerializer(wishlist, many=True)
        return Response(serializer.data)


# =================================================
# 🧾 PLACE ORDER (DB ONLY)
# =================================================
class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticatedWithAuth0]

    @transaction.atomic
    def post(self, request):
        items = request.data.get("items")
        address_id = request.data.get("address_id")

        if not items or not address_id:
            return Response(
                {"error": "items and address_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 🔒 Ensure address belongs to user
        if not Address.objects.filter(
            id=address_id,
            auth0_user_id=request.auth0_user_id,
        ).exists():
            raise PermissionDenied("Invalid address")

        order = Order.objects.create(
            auth0_user_id=request.auth0_user_id,
            address_id=address_id,
            total_amount=0,
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

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# =================================================
# 📦 ORDER HISTORY
# =================================================
class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedWithAuth0]

    def get_queryset(self):
        return Order.objects.filter(
            auth0_user_id=self.request.auth0_user_id
        ).prefetch_related("items__product", "items__product__images")


# =================================================
# 💳 RAZORPAY CREATE ORDER
# =================================================
class RazorpayCreateOrderView(APIView):
    permission_classes = [IsAuthenticatedWithAuth0]

    def post(self, request):
        amount = request.data.get("amount")

        if not amount:
            return Response(
                {"error": "amount is required"},
                status=status.HTTP_400_BAD_REQUEST,
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
        })


# =================================================
# 💳 RAZORPAY VERIFY (FRONTEND)
# =================================================
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
                "status",
            ])

            return Response({"status": "success"})

        except Exception:
            return Response(
                {"status": "failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# =================================================
# 🔐 RAZORPAY WEBHOOK (SOURCE OF TRUTH)
# =================================================
@method_decorator(csrf_exempt, name="dispatch")
class RazorpayWebhookView(View):
    def post(self, request):
        webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        received_signature = request.headers.get("X-Razorpay-Signature")
        payload = request.body

        expected_signature = hmac.new(
            key=webhook_secret.encode(),
            msg=payload,
            digestmod=hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, received_signature):
            return HttpResponse("Invalid signature", status=400)

        data = json.loads(payload)
        event = data.get("event")

        if event == "payment.captured":
            payment = data["payload"]["payment"]["entity"]
            razorpay_order_id = payment["order_id"]

            Order.objects.filter(
                razorpay_order_id=razorpay_order_id
            ).update(
                status="paid",
                razorpay_payment_id=payment["id"],
            )

        return HttpResponse(status=200)
