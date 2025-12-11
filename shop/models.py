from django.db import models
from cloudinary.models import CloudinaryField

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    view_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = CloudinaryField("image")   # Uploads to Cloudinary

    def __str__(self):
        return f"Image for {self.product.name}"
