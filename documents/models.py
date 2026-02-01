from django.db import models
from django.db.models import Max

# --- Choix Entreprise ---

DESTINATAIRES_ENTRANTS = [
    ('SDG', 'SDG'), ('DRH', 'DRH'), ('SOS', 'SOS'), ('DDF', 'DDF'),
    ('DF', 'DF'), ('DEO', 'DEO'), ('DJ', 'DJ'), ('DT', 'DT'),
    ('DAI', 'DAI'), ('DGI-O', 'DGI-O'), ('DASS', 'DASS'), ('DIREC', 'DIREC'),
    ('DSG', 'DSG'), ('DIPREV', 'DIPREV'), ('POFUPOP', 'POFUPOP'),
    ('CM MATONGE', 'CM MATONGE'),
    ('DUK-N', 'DUK-N'), ('DUK-S', 'DUK-S'), ('DUK-E', 'DUK-E'),
    ('DUK-O', 'DUK-O'), ('DUK-C', 'DUK-C'),
    ('DUK-NE', 'DUK-NE'), ('DUK-E', 'DUK-E'), ('DUK-SE', 'DUK-SE'), 
    ('AP', 'AP'), ('AA', 'AA'), ('AJ', 'AJ'), ('AM', 'AM'),  
    ('AREC', 'AREC'), ('AF', 'AF'), ('AT', 'AT'), ('DGI-E', 'DGI-E'),
    ('DP KATANGA I', 'DP KATANGA I'),
    ('CTI', 'CTI'), ('SCE PRESSE', 'SCE PRESSE'), ('CALL CENTER', 'CALL CENTER'),
    ('COURRIER', 'COURRIER'), ('CGPMP', 'CGPMP'), ('AFCNSS', 'AFCNSS'),
]

EMETTEUR_CHOICES = [('DG', 'DG'), ('DGA', 'DGA')]
STATUT_CHOICES = [('SIGNE', 'Signé'), ('REFUS', 'Refus')]

# ✅ Provenance (pour les entrants)
NATURE_CHOICES = [
    ('KIN', 'Kinshasa'),
    ('PROV', 'Province'),
]

# --- Utilitaires ---

class AutoNumeroOrdreMixin(models.Model):
    """Génère automatiquement N° d'ordre (1,2,3,...) dans chaque table."""
    numero_ordre = models.PositiveIntegerField(editable=False, unique=True, null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.numero_ordre:
            maxi = self.__class__.objects.aggregate(m=Max('numero_ordre'))['m'] or 0
            self.numero_ordre = maxi + 1
        super().save(*args, **kwargs)

# --- Entrants ---

class DocumentEntrant(AutoNumeroOrdreMixin):
    # =========================================================
    # ✅ DOUBLONS AUTORISÉS :
    # - Le champ numero_entree n'est pas unique.
    # - Aucune contrainte Meta.constraints n'impose l'unicité.
    # =========================================================
    numero_entree = models.CharField("N° entrée", max_length=64)  # ✅ doublons autorisés

    date_reception = models.DateField("Date réception")
    expediteur = models.CharField("Expéditeur", max_length=255)
    objet = models.CharField("Objet", max_length=255)

    piece_jointe = models.FileField(
        "Pièce jointe",
        upload_to="entrants/%Y/%m/%d/",
        blank=True,
        null=True,
    )

    nature_document = models.CharField(
        "Provenance",
        max_length=5,
        choices=NATURE_CHOICES,
        default='KIN',
    )

    destinataire = models.CharField(
        "Destinataire",
        max_length=32,
        choices=DESTINATAIRES_ENTRANTS,
        blank=True,
    )

    # ✅ champ utilisé pour compter "Documents traités"
    annotations_autorite = models.TextField("Annotations de l’autorité", blank=True)

    date_document_retourne = models.DateField("Date document retourné", blank=True, null=True)
    objet_document_retourne = models.CharField(
        "Objet document retourné",
        max_length=255,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['-date_reception', '-numero_ordre']
        verbose_name = "Document entrant"
        verbose_name_plural = "Documents entrants"

    def save(self, *args, **kwargs):
        if self.numero_entree:
            self.numero_entree = self.numero_entree.strip()

        if self.objet:
            self.objet = self.objet.strip()

        if self.expediteur:
            self.expediteur = self.expediteur.strip()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_entree} - {self.objet[:50]}"

# --- Sortants (base abstraite) ---

class SortantBase(AutoNumeroOrdreMixin):
    numero_registre = models.CharField("N° registre", max_length=64, unique=True)
    date_sortie = models.DateField("Date sortie")
    objet = models.CharField("Objet", max_length=255)
    destinataire = models.CharField("Destinataire", max_length=255)

    class Meta:
        abstract = True
        ordering = ['-date_sortie', '-numero_ordre']

    def __str__(self):
        return f"{self.numero_registre} - {self.objet[:50]}"

# --- Sortants qui gardent Émetteur et Statut ---

class SortantAvecEmetteurStatut(SortantBase):
    emetteur = models.CharField("Émetteur", max_length=3, choices=EMETTEUR_CHOICES)
    statut = models.CharField("Statut", max_length=6, choices=STATUT_CHOICES)

    class Meta:
        abstract = True

class Chrono(SortantAvecEmetteurStatut):
    class Meta:
        verbose_name = "Chrono"
        verbose_name_plural = "Chronos"

class Gouvernement(SortantAvecEmetteurStatut):
    class Meta:
        verbose_name = "Gouvernement"
        verbose_name_plural = "Gouvernements"

class Decision(SortantAvecEmetteurStatut):
    class Meta:
        verbose_name = "Décision"
        verbose_name_plural = "Décisions"

# ✅ REMPLACEMENT ICI
class PaiementPrestationsSociales(SortantAvecEmetteurStatut):
    class Meta:
        verbose_name = "Paiement prestations sociales"
        verbose_name_plural = "Paiements prestations sociales"

class AllocationsFamiliales(SortantAvecEmetteurStatut):
    class Meta:
        verbose_name = "Allocations familiales"
        verbose_name_plural = "Allocations familiales"

class AllocationsPrenatales(SortantAvecEmetteurStatut):
    class Meta:
        verbose_name = "Allocations prénatales"
        verbose_name_plural = "Allocations prénatales"

# --- Ordre de mission (✅ AJOUT STATUT, + champs mission) ---

class OrdreMission(SortantBase):
    destinataire = models.CharField("Personne(s) désigné(es)", max_length=255)

    statut = models.CharField(
        "Statut",
        max_length=6,
        choices=STATUT_CHOICES,
        default='SIGNE',
    )

    destination_mission = models.CharField(
        "Destination de la mission",
        max_length=255,
        blank=True,
        null=True
    )

    nombre_jours = models.PositiveIntegerField(
        "Nombre de jours",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Ordre de mission"
        verbose_name_plural = "Ordres de mission"
