from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def home(request):
    return JsonResponse({
        "status": "ANE Crochet API Running Successfully 🚀",
        "admin": "/admin/",
        "products": "/api/products/"
    })

urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("api/", include("shop.urls")),
]
