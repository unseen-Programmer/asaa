from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static


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
    path("", home),
    path("admin/", admin.site.urls),

    # 🔍 TEST ROUTE (MUST WORK)
    path("api/test/", lambda request: JsonResponse({"ok": True})),

    # 🧩 SHOP APIs
    path("api/", include("shop.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
