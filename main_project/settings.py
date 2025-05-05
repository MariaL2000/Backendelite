#python manage.py runserver_plus localhost:8001 --cert-file=certificates/cert.pem --key-file=certificates/key.pem

from pathlib import Path
import os
from decouple import Config, Csv
import time
from dotenv import load_dotenv
import logging
import dj_database_url

from django.utils.translation import gettext_lazy as _


load_dotenv()
STATIC_VERSION = int(time.time())




DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'  

#DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'







BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de archivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configuración de archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

config = Config(repository=os.path.join(BASE_DIR, '.env'))



DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['backendelite.onrender.com', 'localhost', '127.0.0.1']


SECURE_ALLOWED_REDIRECTS = ['mailto:']

# Development Settings
USE_X_FORWARDED_HOST = False
USE_X_FORWARDED_PORT = False



SECRET_KEY = config('SECRET_KEY', default='clave_secreta_default')


COLORFIELD_ENABLE_PICKER = True



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER




logging.info(f"EMAIL_HOST: {EMAIL_HOST}")
logging.info(f"EMAIL_PORT: {EMAIL_PORT}")
logging.info(f"EMAIL_HOST_USER: {EMAIL_HOST_USER}")
logging.info(f"EMAIL_USE_TLS: {EMAIL_USE_TLS}")

if not all([EMAIL_HOST_USER, EMAIL_HOST_PASSWORD]):
    raise Exception('Email settings not properly configured. Check your .env file.')


INSTALLED_APPS = [
    'jazzmin', 
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'colorfield',
 'corsheaders',
    'orders',
]













JAZZMIN_SETTINGS = {
    # Títulos generales
    "site_title": "Elite Countertops Admin",
    "site_header": "Elite Countertops",
    "site_brand": "Elite Countertops",
    "site_logo": None,
    "welcome_sign": "Bienvenido al panel de administración de Elite Countertops",
    "copyright": "Elite Countertops",
    
    # Favicon - Asegúrate de tener el archivo en static/images/favicon.ico
    "site_icon": "images/favicon.ico",  # o .png si prefieres
    
    # Avatar de usuario
    "user_avatar": None,
    
    # UI
    "show_ui_builder": True,
    "changeform_format": "horizontal_tabs",
    "related_modal_active": False,
    
    # Menú superior
    "topmenu_links": [
        {"name": "Inicio", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Sitio Web", "url": "/", "permissions": ["auth.view_user"]},
        {"model": "auth.User"},
        {"app": "orders"},
    ],
    
    # Menú lateral
    "show_sidebar": True,
    "navigation_expanded": True,
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    # Icons personalizados
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "orders.Order": "fas fa-shopping-cart",
        "orders.Schedule": "fas fa-calendar-alt",
        "orders.Comment": "fas fa-comments",
        "orders.SiteConfiguration": "fas fa-cogs",
    },
    
    # Custom CSS/JS
    "custom_css": None,
    "custom_js": None,
    
    # Overrides para formularios específicos
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
        "orders.order": "horizontal_tabs",
    },
    
    # Orden de apps en el menú
    "order_with_respect_to": [
        "orders",
        "auth",
    ],
    
    # Lenguaje
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-purple",
    "accent": "accent-primary",
    "navbar": "navbar-purple navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-purple",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": True,
    "sidebar_nav_flat_style": False,
    "theme": "cosmo",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-outline-success"
    },
    "actions_sticky_top": True
}




MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  
    'django.contrib.sessions.middleware.SessionMiddleware',
     'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]





REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
}





CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINGS = True

CORS_ALLOWED_ORIGINS = [
    "https://localhost:3000",
    "https://127.0.0.1:3000",
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
    "https://localhost:5173",  
    "https://127.0.0.1:5173",
    "https://localhost:5173",
    "https://marial2000.github.io"

]


CSRF_TRUSTED_ORIGINS = [
    "https://elite-frontend.onrender.com",
    'https://localhost:3000',
    'http://localhost:3000',
    'https://127.0.0.1:3000',
    'http://127.0.0.1:3000',
    "https://localhost:5173",
    "https://marial2000.github.io"
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]



CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cache-control',  
    'pragma',         
    'expires',        
]


CORS_EXPOSE_HEADERS = [
    'content-type',
    'content-length',
]



X_FRAME_OPTIONS = 'SAMEORIGIN'








ROOT_URLCONF = 'main_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
         'DIRS': [BASE_DIR / 'orders/templates'], 
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

WSGI_APPLICATION = 'main_project.wsgi.application'






DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST') + '.virginia-postgres.render.com',  # Add full domain
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}




if DEBUG:
    # Configuración para desarrollo local
    CERT_FILE = 'certificates/cert.pem'
    KEY_FILE = 'certificates/key.pem'
    
    # Desactivar redirecciones y cookies seguras en desarrollo
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    
    # Desactivar otras restricciones de seguridad en desarrollo
    SECURE_BROWSER_XSS_FILTER = False
    SECURE_CONTENT_TYPE_NOSNIFF = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    
    # Opcional: permitir todos los orígenes en desarrollo
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # Configuración para producción
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True





DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True
    )



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True










