from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static


# 🏠 Health check / root endpoint
def home(request):
    return JsonResponse({
        "status": "ANE Crochet API Running Successfully 🚀",
        "admin": "/admin/",
        "products": "/api/products/",
        "addresses": "/api/addresses/",
        "orders": "/api/orders/",
        "payments": "/api/payments/",
    })


urlpatterns = [
    # Root
    path("", home),

    # Admin
    path("admin/", admin.site.urls),

    # 🔍 Test endpoint (IMPORTANT for Render debugging)
    path("api/test/", lambda request: JsonResponse({"ok": True})),

    # App APIs
    path("api/", include("shop.urls")),
]

# ✅ Serve media files ONLY in development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
