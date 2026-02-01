from django import forms
from django.forms import DateInput, ClearableFileInput
from django.core.exceptions import ValidationError

from .models import DocumentEntrant, OrdreMission, STATUT_CHOICES


class DatePicker(DateInput):
    """Widget date HTML5 avec format ISO pour afficher la valeur en édition."""
    input_type = "date"
    format = "%Y-%m-%d"  # requis par <input type="date">

    def __init__(self, *args, **kwargs):
        # S'assure que le rendu utilise le format ISO (sinon le champ reste vide)
        kwargs.setdefault("format", self.format)
        super().__init__(*args, **kwargs)


# ------------------------------------
# ✅ Formulaire : Document Entrant
# ------------------------------------

class DocumentEntrantForm(forms.ModelForm):
    class Meta:
        model = DocumentEntrant
        # ⚠️ Ordre des champs = ordre d'affichage dans le formulaire
        fields = [
            "numero_entree",
            "date_reception",
            "expediteur",
            "objet",
            "nature_document",          # Provenance (Kinshasa / Province)
            "destinataire",
            "annotations_autorite",
            "date_document_retourne",   # ✅ date de retour
            "objet_document_retourne",  # ✅ objet de retour (juste après la date)
            "piece_jointe",             # fichier joint
        ]
        widgets = {
            "date_reception": DatePicker(),
            "date_document_retourne": DatePicker(),
            "nature_document": forms.Select(),
            "objet_document_retourne": forms.TextInput(attrs={
                "placeholder": "Ex. Objet du document renvoyé",
            }),
            "annotations_autorite": forms.Textarea(attrs={"rows": 5}),
            "piece_jointe": ClearableFileInput(attrs={
                "accept": ".pdf,.jpg,.jpeg,.png,.doc,.docx"
            }),
        }
        labels = {
            "nature_document": "Provenance",
            "piece_jointe": "Pièce jointe",
            "date_document_retourne": "Date document retourné",
            "objet_document_retourne": "Objet document retourné",

            # ✅ Renommage demandé (si tu veux harmoniser partout)
            "destinataire": "Personne(s) désigné(es)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Aligne les formats d'entrée des dates (sécurisé si un champ est absent un jour)
        if "date_reception" in self.fields:
            self.fields["date_reception"].input_formats = ["%Y-%m-%d"]
        if "date_document_retourne" in self.fields:
            self.fields["date_document_retourne"].input_formats = ["%Y-%m-%d"]

    def clean(self):
        cleaned = super().clean()
        d_recv = cleaned.get("date_reception")
        d_ret = cleaned.get("date_document_retourne")

        # Règle métier : le retour ne peut pas précéder la réception
        if d_recv and d_ret and d_ret < d_recv:
            raise ValidationError(
                "La date de retour ne peut pas précéder la date de réception."
            )
        return cleaned


# ------------------------------------
# ✅ Formulaire : Ordre de mission
# ------------------------------------

class OrdreMissionForm(forms.ModelForm):
    class Meta:
        model = OrdreMission
        fields = [
            "numero_registre",
            "date_sortie",
            "objet",
            "destinataire",          # ✅ Personne(s) désigné(es)
            "destination_mission",   # ✅ Destination
            "nombre_jours",          # ✅ Nombre jours
            "statut",                # ✅ AJOUT : Statut (Signé / Refus)
        ]
        widgets = {
            "date_sortie": DatePicker(),
            "objet": forms.TextInput(attrs={"placeholder": "Objet de la mission"}),
            "destinataire": forms.TextInput(attrs={"placeholder": "Nom(s) de la/les personne(s) désignée(s)"}),
            "destination_mission": forms.TextInput(attrs={"placeholder": "Ex. Matadi / Goma / ..."}),
            "nombre_jours": forms.NumberInput(attrs={"min": 1, "placeholder": "Ex. 3"}),
            "statut": forms.Select(choices=STATUT_CHOICES),
        }
        labels = {
            "numero_registre": "N° registre",
            "date_sortie": "Date sortie",
            "destinataire": "Personne(s) désigné(es)",
            "destination_mission": "Destination de la mission",
            "nombre_jours": "Nombre de jours",
            "statut": "Statut",
        }
