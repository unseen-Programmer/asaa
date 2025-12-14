from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Order, OrderItem, Product, Address
from .serializers import OrderSerializer


class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        address_id = data.get("address")
        items = data.get("items")
        total_amount = data.get("total_amount")

        if not address_id or not items:
            return Response(
                {"error": "Address and items are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return Response(
                {"error": "Invalid address"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create Order
        order = Order.objects.create(
            user=user,
            address=address,
            total_amount=total_amount
        )

        # Create Order Items
        for item in items:
            product = Product.objects.get(id=item["product"])
            OrderItem.objects.create(
                order=order,
                product=product,
                price=item["price"],
                quantity=item["quantity"]
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
