from rest_framework import serializers
from .models import (
    Product,
    ProductImage,
    Address,
    Wishlist,
    Order,
    OrderItem,
)


# =================================================
# 🖼️ PRODUCT IMAGE
# =================================================
class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ("id", "image")

    def get_image(self, obj):
        return obj.image.url if obj.image else None


# =================================================
# 🛍️ PRODUCT
# =================================================
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "price",
            "stock",
            "description",
            "images",
            "created_at",
            "view_count",
            "category",
        )


# =================================================
# 📍 ADDRESS
# =================================================
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ("auth0_user_id", "created_at", "updated_at")

# =================================================
# ❤️ WISHLIST
# =================================================
class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ("id", "product", "created_at")


# =================================================
# 🧾 ORDER ITEM
# =================================================
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "price", "quantity")


# =================================================
# 🧾 ORDER
# =================================================
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
