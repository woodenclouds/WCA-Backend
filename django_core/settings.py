import os

from pathlib import Path
from datetime import timedelta
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-w-tnshl#k3ta$l&13j281ma(7zsu54gz06)6vo9t-$%xxanjb%'

DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
     'jazzmin',  
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'nested_admin',
    'general',
    'accounts',
    'activities',
    'courses',
    'payments'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

# CORS_ALLOWED_ORIGINS = []   # CORS Allowed hosts

ROOT_URLCONF = 'django_core.urls'

AUTH_USER_MODEL = "accounts.User"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_core.wsgi.application'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=config('ACCESS_TOKEN_LIFETIME', default=5, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

REST_FRAMEWORK = {
'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# DATABASES = {
#     'default': dj_database_url.config(default=config('DATABASE_URL'))
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'WcAcademy',
        'USER': 'woodenclouds',
        'PASSWORD': '123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# settings.py

JAZZMIN_SETTINGS = {
    "site_title": "WC Academy Admin Panel",  # Title in the browser tab
    "site_header": "Your Site Admin",  # Header in the admin
    "site_brand": "Your Brand",  # Branding on the admin login page
    "welcome_sign": "Welcome to Your Admin Portal",  # Custom welcome message
    "site_logo": "yourapp/img/logo.png",  # Logo on the login page (optional)
    "site_icon": None,  # Favicon for the admin site (optional)
    "custom_css": "css/admin_custom.css", 

    # Top bar links (Useful for documentation, user-facing links, etc.)
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://your-support-site.com", "new_window": True},
        {"name": "Github Repo", "url": "https://github.com/your-repo", "new_window": True},
    ],

    # Custom icons for each app
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },

    # Change the appearance of the admin pages
    "show_ui_builder": True,  # Turn on the UI builder to help with theming
    "order_with_respect_to": ["auth", "courses", "accounts","activities","payments"],  # Menu ordering

    # Change colors of the admin
    "theme": "flatly",  # Choose from themes like "cosmo", "flatly", "cyborg", "darkly", etc.
    "dark_mode_theme": None,  # Optionally set a theme for dark mode

    # Other settings...
}

RAZORPAY_KEY_ID="rzp_test_k401MSSoRFYoxD"
RAZORPAY_KEY_SECRET="DSypqxiBvxfaSTO3dFavcEpM"