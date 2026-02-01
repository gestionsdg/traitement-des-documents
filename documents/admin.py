from django.contrib import admin
from .models import (
    DocumentEntrant,
    Chrono, OrdreMission, Gouvernement, Decision,
    PaiementPrestationsSociales, AllocationsFamiliales, AllocationsPrenatales
)

# -------------------------------
# Document entrant
# -------------------------------

@admin.register(DocumentEntrant)
class DocumentEntrantAdmin(admin.ModelAdmin):
    list_display = (
        "numero_ordre",
        "numero_entree",
        "date_reception",
        "expediteur",
        "objet",
        "destinataire",
    )
    list_filter = ("destinataire", "date_reception")
    search_fields = ("numero_entree", "objet", "expediteur")
    ordering = ("-date_reception", "-numero_ordre")


# -------------------------------
# Admin générique des sortants
# (avec Émetteur & Statut)
# -------------------------------

class SortantAdmin(admin.ModelAdmin):
    list_display = (
        "numero_ordre",
        "numero_registre",
        "date_sortie",
        "objet",
        "destinataire",
        "emetteur",
        "statut",
    )
    list_filter = ("emetteur", "statut", "date_sortie")
    search_fields = ("numero_registre", "objet", "destinataire")
    ordering = ("-date_sortie", "-numero_ordre")


# -------------------------------
# Admin spécifique Ordre de mission
# (sans Émetteur & Statut)
# -------------------------------

@admin.register(OrdreMission)
class OrdreMissionAdmin(admin.ModelAdmin):
    list_display = (
        "numero_ordre",
        "numero_registre",
        "date_sortie",
        "objet",
        "destinataire",
        "destination_mission",
        "nombre_jours",
    )
    list_filter = ("date_sortie",)
    search_fields = (
        "numero_registre",
        "objet",
        "destinataire",
        "destination_mission",
    )
    ordering = ("-date_sortie", "-numero_ordre")


# -------------------------------
# Enregistrement des autres sortants
# -------------------------------

admin.site.register(Chrono, SortantAdmin)
admin.site.register(Gouvernement, SortantAdmin)
admin.site.register(Decision, SortantAdmin)
admin.site.register(PaiementPrestationsSociales, SortantAdmin)
admin.site.register(AllocationsFamiliales, SortantAdmin)
admin.site.register(AllocationsPrenatales, SortantAdmin)
