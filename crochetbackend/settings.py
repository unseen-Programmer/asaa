from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------- #
# SECURITY
# --------------------------------------------------------------------------- #

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
DEBUG = True

ALLOWED_HOSTS = ["*"]

# --------------------------------------------------------------------------- #
# INSTALLED APPS
# --------------------------------------------------------------------------- #

INSTALLED_APPS = [
    # 🌸 Jazzmin Admin UI (must be first)
    "jazzmin",

    # Django default apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "rest_framework",
    "corsheaders",
    "cloudinary",
    "cloudinary_storage",

    # Local apps
    "shop",
]

# --------------------------------------------------------------------------- #
# MIDDLEWARE
# --------------------------------------------------------------------------- #

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "crochetbackend.urls"

# --------------------------------------------------------------------------- #
# TEMPLATES
# --------------------------------------------------------------------------- #

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "crochetbackend.wsgi.application"

# --------------------------------------------------------------------------- #
# DATABASE CONFIG — SQLITE (LOCAL) / POSTGRESQL (RENDER)
# --------------------------------------------------------------------------- #

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    import dj_database_url
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --------------------------------------------------------------------------- #
# PASSWORD VALIDATION
# --------------------------------------------------------------------------- #

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------------------------------- #
# INTERNATIONALIZATION
# --------------------------------------------------------------------------- #

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------- #
# STATIC & MEDIA FILES
# --------------------------------------------------------------------------- #

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# --------------------------------------------------------------------------- #
# CLOUDINARY CONFIG
# --------------------------------------------------------------------------- #

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}

# --------------------------------------------------------------------------- #
# CORS
# --------------------------------------------------------------------------- #

CORS_ALLOW_ALL_ORIGINS = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------------------------------- #
# 🌸 JAZZMIN ADMIN THEME SETTINGS (PREMIUM UI)
# --------------------------------------------------------------------------- #

JAZZMIN_SETTINGS = {
    "site_title": "ANE Crochet Admin",
    "site_header": "ANE Crochet",
    "site_brand": "ANE Crochet Dashboard",
    "welcome_sign": "Welcome to ANE Crochet Management",
    "copyright": "ANE Crochet",
    "search_model": ["shop.Product", "shop.Category"],
    "show_ui_builder": False,

    "topmenu_links": [
        {"name": "Home", "url": "/", "permissions": ["auth.view_user"]},
        {"name": "Products", "url": "/admin/shop/product/"},
        {"name": "Categories", "url": "/admin/shop/category/"},
    ],

    "hide_apps": [],
    "hide_models": [],
}

