from rest_framework import serializers
from django.contrib.auth.models import User
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


# ─────────────────────────────
# USER REGISTER SERIALIZER
# ─────────────────────────────
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
