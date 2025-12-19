from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


def home(request):
    return JsonResponse({
        "status": "ANE Crochet API Running Successfully 🚀",
        "admin": "/admin/",
        "products": "/api/products/",
        "login": "/api/auth/login/",
        "register": "/api/auth/register/",
    })


urlpatterns = [
    # 🏠 Home
    path("", home),

    # 🛠 Admin
    path("admin/", admin.site.urls),

    # 🧩 App APIs (Products, Orders, Razorpay, etc.)
    path("api/", include("shop.urls")),

    # 🔐 JWT Authentication
    path("api/auth/login/", TokenObtainPairView.as_view(), name="jwt-login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
]
