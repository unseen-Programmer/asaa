from django.contrib import admin
from .models import (
    Category,
    Product,
    ProductImage,
    Address,
    Wishlist,
    Order,
    OrderItem,
)

# =================================================
# 📂 CATEGORY
# =================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


# =================================================
# 🖼️ PRODUCT IMAGE (INLINE)
# =================================================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# =================================================
# 🛍️ PRODUCT
# =================================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "view_count", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_filter = ("created_at", "category")
    inlines = [ProductImageInline]


# =================================================
# 📍 ADDRESS
# =================================================
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "pincode", "auth0_user_id")
    search_fields = ("name", "city", "auth0_user_id")
    list_filter = ("city",)


# =================================================
# ❤️ WISHLIST
# =================================================
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("auth0_user_id", "product", "created_at")
    search_fields = ("auth0_user_id",)
    list_filter = ("created_at",)


# =================================================
# 🧾 ORDER ITEM (INLINE)
# =================================================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ["product"]


# =================================================
# 🧾 ORDER
# =================================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "auth0_user_id",
        "total_amount",
        "status",
        "payment_method",
        "created_at",
    )
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("auth0_user_id", "razorpay_order_id")
    inlines = [OrderItemInline]
    readonly_fields = ("razorpay_order_id", "razorpay_payment_id", "razorpay_signature")
