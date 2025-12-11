from rest_framework import serializers
from .models import Product, ProductImage, Category, Address


# ─────────────────────────────
# IMAGE SERIALIZER
# ─────────────────────────────
class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["image"]

    def get_image(self, obj):
        try:
            return obj.image.url
        except:
            return None


# ─────────────────────────────
# CATEGORY SERIALIZER
# ─────────────────────────────
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


# ─────────────────────────────
# PRODUCT SERIALIZER
# ─────────────────────────────
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


# ─────────────────────────────
# ADDRESS SERIALIZER
# ─────────────────────────────
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
