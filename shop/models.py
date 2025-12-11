from django.db import models
from cloudinary.models import CloudinaryField
from django.utils.text import slugify


# ------------------------------------------------------------
# CATEGORY MODEL
# ------------------------------------------------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ------------------------------------------------------------
# PRODUCT MODEL
# ------------------------------------------------------------
class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    view_count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ------------------------------------------------------------
# PRODUCT IMAGES MODEL
# ------------------------------------------------------------
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE
    )
    image = CloudinaryField("image")  # Uploads directly to Cloudinary

    def __str__(self):
        return f"Image for {self.product.name}"
