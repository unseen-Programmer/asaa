from django.db import models
from cloudinary.models import CloudinaryField


# ─────────────────────────────
# CATEGORY
# ─────────────────────────────
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, db_index=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# ─────────────────────────────
# PRODUCT
# ─────────────────────────────
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, db_index=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        db_index=True
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0, db_index=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


# ─────────────────────────────
# PRODUCT IMAGE
# ─────────────────────────────
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        db_index=True
    )
    image = CloudinaryField("image")

    def __str__(self):
        return f"ProductImage ({self.product.id})"


# ─────────────────────────────
# ADDRESS
# ─────────────────────────────
class Address(models.Model):
    ADDRESS_TYPE_CHOICES = (
        ("home", "Home"),
        ("work", "Work"),
    )

    auth0_user_id = models.CharField(max_length=255, db_index=True)

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    street = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)

    address_type = models.CharField(
        max_length=10,
        choices=ADDRESS_TYPE_CHOICES,
        default="home"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.address_type})"


# ─────────────────────────────
# WISHLIST
# ─────────────────────────────
class Wishlist(models.Model):
    auth0_user_id = models.CharField(max_length=255, db_index=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlisted_by",
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("auth0_user_id", "product")

    def __str__(self):
        return f"{self.auth0_user_id} ❤️ {self.product.name}"


# ─────────────────────────────
# ORDER
# ─────────────────────────────
class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("razorpay", "Razorpay"),
        ("cod", "Cash on Delivery"),
    ]

    auth0_user_id = models.CharField(max_length=255, db_index=True)

    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="razorpay"
    )

    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.status}"


# ─────────────────────────────
# ORDER ITEM
# ─────────────────────────────
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name if self.product else 'Deleted'} × {self.quantity}"
