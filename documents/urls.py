# documents/urls.py
from django.urls import path
from . import views
from . import views_export  # ✅ Export Excel
from . import views_pdf     # ✅ PDF (traités / non traités)

app_name = "documents"

urlpatterns = [
    # =========================
    # Tableau de bord
    # =========================
    path("", views.dashboard, name="dashboard"),

    # =========================
    # Documents entrants
    # =========================
    path("entrants/", views.entrants_list, name="entrants_list"),

    # ✅ Téléchargement sécurisé de la pièce jointe (login requis)
    path(
        "entrants/<int:pk>/piece-jointe/",
        views.secure_entrant_attachment,
        name="entrant_piece_jointe",
    ),

    # Nouveaux formulaires séparés
    path("entrants/kin/nouveau/", views.entrants_create_kin, name="entrants_create_kin"),
    path("entrants/prov/nouveau/", views.entrants_create_prov, name="entrants_create_prov"),

    # Formulaire général
    path("entrants/nouveau/", views.entrants_create, name="entrants_create"),

    path("entrants/<int:pk>/modifier/", views.entrants_update, name="entrants_update"),
    path("entrants/<int:pk>/supprimer/", views.entrants_delete, name="entrants_delete"),

    # =========================
    # ✅ Export Excel — Documents entrants
    # =========================
    path(
        "entrants/export/excel/",
        views_export.export_entrants_excel,
        name="export_entrants_excel",
    ),

    # =========================
    # ✅ PDFs — Entrants (Kin/Prov x Traités/Non traités)
    # =========================
    path(
        "entrants/pdf/kin/traites/",
        views_pdf.liste_entrants_kin_traites_pdf,
        name="pdf_entrants_kin_traites",
    ),
    path(
        "entrants/pdf/kin/non-traites/",
        views_pdf.liste_entrants_kin_non_traites_pdf,
        name="pdf_entrants_kin_non_traites",
    ),
    path(
        "entrants/pdf/prov/traites/",
        views_pdf.liste_entrants_prov_traites_pdf,
        name="pdf_entrants_prov_traites",
    ),
    path(
        "entrants/pdf/prov/non-traites/",
        views_pdf.liste_entrants_prov_non_traites_pdf,
        name="pdf_entrants_prov_non_traites",
    ),

    # =========================
    # Documents sortants
    # =========================
    path("sortants/<slug:nature>/", views.sortants_list, name="sortants_list"),
    path("sortants/<slug:nature>/nouveau/", views.sortants_create, name="sortants_create"),
    path("sortants/<slug:nature>/<int:pk>/modifier/", views.sortants_update, name="sortants_update"),
    path("sortants/<slug:nature>/<int:pk>/supprimer/", views.sortants_delete, name="sortants_delete"),

    # =========================
    # ✅ Export Excel — Documents sortants
    # =========================
    path(
        "sortants/export/excel/",
        views_export.export_sortants_excel,
        name="export_sortants_excel",
    ),

    # =========================
    # ✅ Rapports annuels détaillés
    # =========================
    path(
        "rapports/activites/detaille/",
        views.rapport_activites_detaille,
        name="rapport_activites_detaille",
    ),
    path(
        "rapports/activites/detaille/pdf/",
        views.rapport_activites_detaille_pdf,
        name="rapport_activites_detaille_pdf",
    ),

    # =========================
    # ✅ Rapports mensuels (anciens) - REMIS
    # =========================
    path(
        "rapports/activites/mensuel/",
        views.rapport_activites_mensuel,
        name="rapport_activites_mensuel",
    ),
    path(
        "rapports/activites/mensuel/pdf/",
        views.rapport_activites_mensuel_pdf,
        name="rapport_activites_mensuel_pdf",
    ),

    # =========================
    # ✅ Rapports mensuels détaillés
    # =========================
    path(
        "rapports/activites/mensuel/detaille/",
        views.rapport_activites_mensuel_detaille,
        name="rapport_activites_mensuel_detaille",
    ),
    path(
        "rapports/activites/mensuel/detaille/pdf/",
        views.rapport_activites_mensuel_detaille_pdf,
        name="rapport_activites_mensuel_detaille_pdf",
    ),

    # =========================
    # ✅ Rapports hebdomadaires (Lundi → Vendredi)
    # =========================
    path(
        "rapports/activites/hebdo/",
        views.rapport_activites_hebdo,
        name="rapport_activites_hebdo",
    ),
    path(
        "rapports/activites/hebdo/pdf/",
        views.rapport_activites_hebdo_pdf,
        name="rapport_activites_hebdo_pdf",
    ),
]
