from django.db import models
from cloudinary.models import CloudinaryField

# ─────────────────────────────
# CATEGORY
# ─────────────────────────────
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


# ─────────────────────────────
# PRODUCT
# ─────────────────────────────
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


# ─────────────────────────────
# PRODUCT IMAGE
# ─────────────────────────────
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = CloudinaryField("image")

    def __str__(self):
        return f"Image for {self.product.name}"


# ─────────────────────────────
# ADDRESS (Auth0 User)
# ─────────────────────────────
class Address(models.Model):
    auth0_user_id = models.CharField(
        max_length=255,
        db_index=True
    )

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    street = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.city}"


# ─────────────────────────────
# WISHLIST ❤️ (Auth0)
# ─────────────────────────────
class Wishlist(models.Model):
    auth0_user_id = models.CharField(
        max_length=255,
        db_index=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlisted_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("auth0_user_id", "product")

    def __str__(self):
        return f"{self.auth0_user_id} ❤️ {self.product.name}"


# ─────────────────────────────
# ORDER 🧾 (Auth0)
# ─────────────────────────────
class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    auth0_user_id = models.CharField(
        max_length=255,
        db_index=True
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"


# ─────────────────────────────
# ORDER ITEM
# ─────────────────────────────
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product} x {self.quantity}"
