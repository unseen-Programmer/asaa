from rest_framework import serializers
from .models import Product, ProductImage, Category
import cloudinary

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["image"]

    def get_image(self, obj):
        if obj.image:
            return cloudinary.utils.cloudinary_url(obj.image.name)[0]
        return None


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer()

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
