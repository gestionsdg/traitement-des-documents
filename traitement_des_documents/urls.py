# traitement_des_documents/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # ⬅️ Vues d'auth Django
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # --- Authentification ---
    path("connexion/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="connexion"),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="deconnexion"),

    # --- Application principale (namespacée) ---
    # Toutes les URLs de l'app seront référencées comme 'documents:...'
    path("", include(("documents.urls", "documents"), namespace="documents")),
]

# --- Fichiers statiques et médias en mode DEBUG ---
if settings.DEBUG:
    # Sert les fichiers uploadés (MEDIA)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Option pratique en local : servir aussi le dossier static/ du projet
    if getattr(settings, "STATICFILES_DIRS", None):
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
