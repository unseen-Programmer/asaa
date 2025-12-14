from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


# ───────────────────────
# CATEGORY MODEL
# ───────────────────────
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


# ───────────────────────
# PRODUCT MODEL
# ───────────────────────
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    view_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


# ───────────────────────
# PRODUCT IMAGE MODEL
# ───────────────────────
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = CloudinaryField("image")

    def __str__(self):
        return f"Image for {self.product.name}"


# ──────────────────────────────────────────────
# ADDRESS MODEL (Checkout)
# ──────────────────────────────────────────────
class Address(models.Model):
    """
    Stores address for guest users or logged-in users.
    client_id is used for guests (UUID from frontend)
    """

    client_id = models.CharField(max_length=200, db_index=True)

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    street = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.city}"


# ──────────────────────────────────────────────
# WISHLIST MODEL (Like button – Flipkart style)
# ──────────────────────────────────────────────
class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlisted_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} ❤️ {self.product.name}"
