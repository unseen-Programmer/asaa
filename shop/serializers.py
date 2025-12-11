from rest_framework import serializers
from .models import Product, ProductImage, Category


# -----------------------------------------
# IMAGE SERIALIZER (Cloudinary Safe)
# -----------------------------------------
class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["image"]

    def get_image(self, obj):
        """
        Cloudinary images do NOT use .name — instead they have .url.
        This returns the full image URL.
        """
        try:
            return obj.image.url
        except:
            return None


# -----------------------------------------
# CATEGORY SERIALIZER
# -----------------------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


# -----------------------------------------
# PRODUCT SERIALIZER
# -----------------------------------------
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
