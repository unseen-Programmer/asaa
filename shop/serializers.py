from rest_framework import serializers
from django.contrib.auth.models import User

from .models import (
    Product,
    ProductImage,
    Category,
    Address,
    Order,
    OrderItem,
    Wishlist,
)

# ───────────────────────
# IMAGE SERIALIZER
# ───────────────────────
class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["image"]

    def get_image(self, obj):
        try:
            return obj.image.url
        except Exception:
            return None


# ───────────────────────
# CATEGORY SERIALIZER
# ───────────────────────
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


# ───────────────────────
# PRODUCT SERIALIZER
# ───────────────────────
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "price",
            "stock",
            "description",
            "images",
            "view_count",
        ]


# ───────────────────────
# ADDRESS SERIALIZER
# ───────────────────────
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "client_id",
            "name",
            "phone",
            "street",
            "city",
            "pincode",
            "updated_at",
        ]


# ───────────────────────
# USER REGISTER SERIALIZER
# ───────────────────────
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user


# ───────────────────────
# WISHLIST ❤️ (FIXES RENDER ERROR)
# ───────────────────────
class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "product", "created_at"]


# ───────────────────────
# ORDER ITEM SERIALIZER
# ───────────────────────
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name", read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ["product", "product_name", "price", "quantity"]


# ───────────────────────
# ORDER SERIALIZER
# ───────────────────────
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "address",
            "total_amount",
            "status",
            "items",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]
