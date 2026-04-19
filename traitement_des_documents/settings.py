from pathlib import Path
import os
import dj_database_url

# --- Chemins de base ---
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
#  Sécurité & Debug (local/LAN vs Render/Production)
# ============================================================
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "dev-secret-key-only-change-me"
)

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"


# ============================================================
#  Hôtes autorisés / CSRF (important pour Render)
# ============================================================
if DEBUG:
    ALLOWED_HOSTS = ["192.168.1.74", "localhost", "127.0.0.1", "hp", "DESKTOP-U3PNFME"]
    CSRF_TRUSTED_ORIGINS = []
else:
    ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]


# ============================================================
#  Apps
# ============================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "documents",
]


# ============================================================
#  Middlewares
# ============================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "traitement_des_documents.urls"


# ============================================================
#  Templates
# ============================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "traitement_des_documents.wsgi.application"


# ============================================================
#  Base de données : SQLite en local / Postgres sur Render
# ============================================================
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}


# ============================================================
#  Validation des mots de passe
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ============================================================
#  Internationalisation
# ============================================================
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Kinshasa"
USE_I18N = True
USE_TZ = True


# ============================================================
#  Statiques & médias
# ============================================================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
#  Auth
# ============================================================
LOGIN_URL = "connexion"
LOGIN_REDIRECT_URL = "documents:dashboard"
LOGOUT_REDIRECT_URL = "connexion"


# ============================================================
#  SESSIONS : Sécurité (ta demande)
# ============================================================
# ✅ Force la reconnexion à la "réouverture" (fermeture du navigateur => session morte)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# ✅ Durée max de session (surtout utile en production)
# - si tu veux plus court, mets 15 min : 60*15
SESSION_COOKIE_AGE = 60 * 30  # 30 minutes

# ✅ Prolonge la session à chaque requête (si l’utilisateur reste actif)
SESSION_SAVE_EVERY_REQUEST = True

# ✅ Recommandé
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"


# --- Clé primaire par défaut ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
#  Sécurité production (uniquement si DEBUG=False)
# ============================================================
if not DEBUG:
    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS
    SECURE_HSTS_SECONDS = 60
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Headers
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
