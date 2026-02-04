# documents/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.forms import modelform_factory, DateInput
from django.contrib import messages
from django.db.models import F
from django.db.models.functions import Trim, Upper  # ✅ Upper ajouté
from django.core.paginator import Paginator
import datetime
from datetime import timedelta
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils import timezone  # ✅ ajouté

# ✅ AJOUT (pour construire l’URL absolue du logo)
from django.contrib.staticfiles.storage import staticfiles_storage

# ✅ AJOUT : pour servir un fichier de manière sécurisée
import os
from django.conf import settings
from django.http import FileResponse, Http404

from .models import (
    DocumentEntrant,
    Chrono, OrdreMission, Gouvernement, Decision,
    PaiementPrestationsSociales,
    AllocationsFamiliales, AllocationsPrenatales
)
from .forms import DocumentEntrantForm


def model_has_field(Model, field_name: str) -> bool:
    return any(f.name == field_name for f in Model._meta.get_fields())


# ==========================================================
# ✅ Téléchargement sécurisé de pièce jointe (Entrants)
# ==========================================================
@login_required(login_url='connexion')
def secure_entrant_attachment(request, pk: int):
    """
    Sert la pièce jointe d'un DocumentEntrant de manière sécurisée :
    - accès uniquement si connecté
    - vérifie que le fichier existe
    - empêche les chemins anormaux (traversal)
    """
    doc = get_object_or_404(DocumentEntrant, pk=pk)

    if not getattr(doc, "piece_jointe", None):
        raise Http404("Aucune pièce jointe.")

    if not doc.piece_jointe.name:
        raise Http404("Aucune pièce jointe.")

    # Chemin absolu du fichier sur disque
    try:
        file_path = doc.piece_jointe.path
    except Exception:
        # Certains storages peuvent ne pas exposer .path
        raise Http404("Fichier indisponible.")

    # Sécurité : s'assurer que le fichier est dans MEDIA_ROOT
    media_root = os.path.abspath(getattr(settings, "MEDIA_ROOT", "") or "")
    abs_file_path = os.path.abspath(file_path)

    if not media_root or not abs_file_path.startswith(media_root + os.sep):
        # protège contre chemins hors MEDIA_ROOT
        raise Http404("Accès refusé.")

    if not os.path.exists(abs_file_path):
        raise Http404("Fichier introuvable.")

    # Nom de fichier "propre" pour le navigateur
    filename = os.path.basename(doc.piece_jointe.name)

    # Option : forcer "attachment" pour téléchargement (plus sûr)
    # Si tu veux afficher PDF dans navigateur, remplace as_attachment=True par False.
    return FileResponse(
        open(abs_file_path, "rb"),
        as_attachment=True,
        filename=filename,
    )


# --- Dashboard ---
@login_required(login_url='connexion')
def dashboard(request):
    # ✅ pour permettre {{ now|date:"Y" }} dans dashboard.html
    return render(request, "documents/dashboard.html", {"now": timezone.now()})


# --- Entrants ---
@login_required(login_url='connexion')
def entrants_list(request):
    qs = DocumentEntrant.objects.all()

    prov = (request.GET.get("prov") or "").strip().upper()
    if prov in ("KIN", "PROV"):
        qs = qs.filter(nature_document=prov)

    numero_entree = (request.GET.get("numero_entree") or "").strip()
    objet = (request.GET.get("objet") or "").strip()

    if numero_entree:
        qs = qs.filter(numero_entree__icontains=numero_entree)
    if objet:
        qs = qs.filter(objet__icontains=objet)

    # ✅ Tri stable même si numero_entree contient des doublons
    qs = qs.order_by("date_reception", "numero_ordre")

    paginator = Paginator(qs, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "documents/entrants_list.html",
        {
            "rows": page_obj.object_list,
            "page_obj": page_obj,
            "numero_entree": numero_entree,
            "objet": objet,
            "prov": prov,
        },
    )


@login_required(login_url='connexion')
def entrants_create(request):
    if request.method == "POST":
        form = DocumentEntrantForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Document entrant enregistré.")
            return redirect("documents:entrants_list")
    else:
        form = DocumentEntrantForm()
    return render(request, "documents/entrants_form.html", {"form": form})


@login_required(login_url='connexion')
def entrants_create_kin(request):
    if request.method == "POST":
        form = DocumentEntrantForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.nature_document = "KIN"
            obj.save()
            messages.success(request, "Document entrant (Kinshasa) enregistré.")
            return redirect("documents:entrants_list")
    else:
        form = DocumentEntrantForm(initial={"nature_document": "KIN"})
    return render(
        request,
        "documents/entrants_form.html",
        {"form": form, "nature_lock": "KIN", "nature_label": "Kinshasa"},
    )


@login_required(login_url='connexion')
def entrants_create_prov(request):
    if request.method == "POST":
        form = DocumentEntrantForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.nature_document = "PROV"
            obj.save()
            messages.success(request, "Document entrant (Province) enregistré.")
            return redirect("documents:entrants_list")
    else:
        form = DocumentEntrantForm(initial={"nature_document": "PROV"})
    return render(
        request,
        "documents/entrants_form.html",
        {"form": form, "nature_lock": "PROV", "nature_label": "Province"},
    )


@login_required(login_url='connexion')
def entrants_update(request, pk):
    obj = get_object_or_404(DocumentEntrant, pk=pk)

    if request.method == "POST":
        form = DocumentEntrantForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Document entrant modifié.")
            return redirect("documents:entrants_list")
    else:
        form = DocumentEntrantForm(instance=obj)

    return render(request, "documents/entrants_form.html", {"form": form, "instance": obj})


@login_required(login_url='connexion')
@require_POST
def entrants_delete(request, pk):
    obj = get_object_or_404(DocumentEntrant, pk=pk)
    if getattr(obj, "piece_jointe", None):
        obj.piece_jointe.delete(save=False)
    obj.delete()
    messages.success(request, "Document entrant supprimé.")
    return redirect("documents:entrants_list")


# --- Sortants (génériques) ---
SORTANTS = {
    "chrono": (Chrono, "Chrono"),
    "ordre-mission": (OrdreMission, "Ordre de mission"),
    "gouvernement": (Gouvernement, "Gouvernement"),
    "decision": (Decision, "Décision"),
    "prestations-familles": (PaiementPrestationsSociales, "Paiement prestations sociales"),
    "allocations-familiales": (AllocationsFamiliales, "Allocations familiales"),
    "allocations-prenatales": (AllocationsPrenatales, "Allocations prénatales"),
}


def _get_sortant_model(nature_slug):
    if nature_slug not in SORTANTS:
        raise ValueError("Nature inconnue")
    return SORTANTS[nature_slug]


@login_required(login_url='connexion')
def sortants_list(request, nature):
    Model, label = _get_sortant_model(nature)
    qs = Model.objects.all()

    numero_registre = (request.GET.get("numero_registre") or "").strip()
    objet = (request.GET.get("objet") or "").strip()
    destinataire = (request.GET.get("destinataire") or "").strip()

    if numero_registre:
        qs = qs.filter(numero_registre__icontains=numero_registre)
    if objet:
        qs = qs.filter(objet__icontains=objet)
    if destinataire:
        qs = qs.filter(destinataire__icontains=destinataire)

    if model_has_field(Model, "date_sortie"):
        qs = qs.order_by("date_sortie", "numero_ordre")
    else:
        qs = qs.order_by("numero_ordre")

    paginator = Paginator(qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    return render(
        request,
        "documents/sortants_list.html",
        {
            "rows": page_obj.object_list,
            "page_obj": page_obj,
            "label": label,
            "nature": nature,
            "numero_registre": numero_registre,
            "objet": objet,
            "destinataire": destinataire,
            "querystring": querystring,
        },
    )


def _sortant_form_class(Model):
    date_widget = DateInput(format="%Y-%m-%d", attrs={"type": "date"})
    fields = ["numero_registre", "date_sortie", "objet", "destinataire"]

    if model_has_field(Model, "destination_mission"):
        fields.append("destination_mission")
    if model_has_field(Model, "nombre_jours"):
        fields.append("nombre_jours")
    if model_has_field(Model, "emetteur"):
        fields.append("emetteur")
    if model_has_field(Model, "statut"):
        fields.append("statut")

    widgets = {
        "date_sortie": date_widget,
        "objet": forms.Textarea(attrs={"rows": 3}),
        "destinataire": forms.Textarea(attrs={"rows": 3}),
    }

    FormClass = modelform_factory(Model, fields=fields, widgets=widgets)

    if "date_sortie" in FormClass.base_fields:
        FormClass.base_fields["date_sortie"].input_formats = ["%Y-%m-%d"]

    if model_has_field(Model, "destination_mission") and "destinataire" in FormClass.base_fields:
        FormClass.base_fields["destinataire"].label = "Personne(s) désigné(es)"

    return FormClass


@login_required(login_url='connexion')
def sortants_create(request, nature):
    Model, label = _get_sortant_model(nature)
    FormClass = _sortant_form_class(Model)

    if request.method == "POST":
        form = FormClass(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"{label} enregistré.")
            return redirect("documents:sortants_list", nature=nature)
    else:
        form = FormClass()

    return render(request, "documents/sortants_form.html", {"form": form, "label": label, "nature": nature})


@login_required(login_url='connexion')
def sortants_update(request, nature, pk):
    Model, label = _get_sortant_model(nature)
    obj = get_object_or_404(Model, pk=pk)
    FormClass = _sortant_form_class(Model)

    if request.method == "POST":
        form = FormClass(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"{label} modifié.")
            return redirect("documents:sortants_list", nature=nature)
    else:
        form = FormClass(instance=obj)

    return render(
        request,
        "documents/sortants_form.html",
        {"form": form, "label": label, "nature": nature, "instance": obj},
    )


@login_required(login_url='connexion')
@require_POST
def sortants_delete(request, nature, pk):
    Model, label = _get_sortant_model(nature)
    obj = get_object_or_404(Model, pk=pk)
    obj.delete()
    messages.success(request, f"{label} supprimé.")
    return redirect("documents:sortants_list", nature=nature)


# =========================
# ✅ Rapports (ANNUEL / MENSUEL / HEBDO)
# =========================

MOIS = [
    (1, "Janvier"), (2, "Février"), (3, "Mars"), (4, "Avril"),
    (5, "Mai"), (6, "Juin"), (7, "Juillet"), (8, "Août"),
    (9, "Septembre"), (10, "Octobre"), (11, "Novembre"), (12, "Décembre"),
]

SORTANT_MODELS = [
    Chrono, OrdreMission, Gouvernement, Decision,
    PaiementPrestationsSociales,
    AllocationsFamiliales, AllocationsPrenatales,
]


def _annees_disponibles():
    years = set(d.year for d in DocumentEntrant.objects.dates("date_reception", "year"))
    for Model in SORTANT_MODELS:
        if model_has_field(Model, "date_sortie"):
            years |= set(d.year for d in Model.objects.dates("date_sortie", "year"))
    if not years:
        years = {datetime.date.today().year}
    return sorted(years, reverse=True)


def _entrants_traites_count(year: int, month: int) -> int:
    qs = DocumentEntrant.objects.filter(date_reception__year=year, date_reception__month=month)

    field_name = "annotations_autorite"
    if not model_has_field(DocumentEntrant, field_name):
        return 0

    qs = qs.filter(**{f"{field_name}__isnull": False}).annotate(
        _ann_trim=Trim(F(field_name))
    ).exclude(_ann_trim="")
    return qs.count()


def _count_sortants_signes_month(Model, year: int, month: int) -> int:
    if not model_has_field(Model, "date_sortie"):
        return 0

    qs = Model.objects.filter(date_sortie__year=year, date_sortie__month=month)

    if model_has_field(Model, "statut"):
        qs = qs.annotate(_st=Upper(Trim(F("statut"))))
        qs = qs.filter(_st__in=["SIGNE", "SIGNÉ", "SIGNEE"])

    if model_has_field(Model, "emetteur"):
        qs = qs.annotate(_em=Upper(Trim(F("emetteur"))))
        qs = qs.filter(_em__in=["DG", "DGA", "DG/DGA"])

    return qs.count()


def _compte_sortants_signes(year: int, month: int) -> int:
    total = 0
    for Model in SORTANT_MODELS:
        total += _count_sortants_signes_month(Model, year, month)
    return total


def _compte_sortants_signes_detail(year: int, month: int) -> dict:
    dossiers_chrono = _count_sortants_signes_month(Chrono, year, month)
    dossiers_gouv = _count_sortants_signes_month(Gouvernement, year, month)
    dossiers_pps = _count_sortants_signes_month(PaiementPrestationsSociales, year, month)
    dossiers_ap = _count_sortants_signes_month(AllocationsPrenatales, year, month)
    dossiers_af = _count_sortants_signes_month(AllocationsFamiliales, year, month)
    dossiers_om = _count_sortants_signes_month(OrdreMission, year, month)
    dossiers_decision = _count_sortants_signes_month(Decision, year, month)

    total = (
        dossiers_chrono + dossiers_gouv + dossiers_pps +
        dossiers_ap + dossiers_af + dossiers_om + dossiers_decision
    )

    return {
        "dossiers_chrono": dossiers_chrono,
        "dossiers_gouv": dossiers_gouv,
        "dossiers_pps": dossiers_pps,
        "dossiers_ap": dossiers_ap,
        "dossiers_af": dossiers_af,
        "dossiers_om": dossiers_om,
        "dossiers_decision": dossiers_decision,
        "signes": total,
    }


def _rapport_data(annee: int):
    lignes = []
    totaux = {"recus": 0, "prov": 0, "kin": 0, "traites": 0, "non_traites": 0, "signes": 0}

    for m, label in MOIS:
        entrants_qs = DocumentEntrant.objects.filter(date_reception__year=annee, date_reception__month=m)
        prov = entrants_qs.filter(nature_document="PROV").count()
        kin = entrants_qs.filter(nature_document="KIN").count()

        traites = _entrants_traites_count(annee, m)

        total_recus = prov + kin
        non_traites = max(total_recus - traites, 0)

        signes = _compte_sortants_signes(annee, m)

        totaux["prov"] += prov
        totaux["kin"] += kin
        totaux["traites"] += traites
        totaux["recus"] += total_recus
        totaux["non_traites"] += non_traites
        totaux["signes"] += signes

        if (total_recus > 0) or (signes > 0) or (traites > 0):
            lignes.append({
                "mois": label,
                "prov": prov,
                "kin": kin,
                "traites": traites,
                "non_traites": non_traites,
                "total_recus": total_recus,
                "signes": signes,
            })

    return lignes, totaux


# ==========================================================
# ✅ NOUVEAUX RAPPORTS ANNUELS DÉTAILLÉS (HTML + PDF) — SEULS
# ==========================================================

@login_required(login_url='connexion')
def rapport_activites_detaille(request):
    try:
        annee = int(request.GET.get("annee") or datetime.date.today().year)
    except ValueError:
        annee = datetime.date.today().year

    lignes, totaux = _rapport_data(annee)

    totaux["total_documents_recus"] = totaux["recus"]
    totaux["documents_traites"] = totaux["traites"]
    totaux["documents_non_traites"] = totaux["non_traites"]

    contexte = {
        "annee": annee,
        "annees": _annees_disponibles(),
        "lignes": lignes,
        "totaux": totaux,
    }
    return render(request, "documents/rapports_activites-detaille.html", contexte)


@login_required(login_url='connexion')
def rapport_activites_detaille_pdf(request):
    from weasyprint import HTML

    try:
        annee = int(request.GET.get("annee") or datetime.date.today().year)
    except ValueError:
        annee = datetime.date.today().year

    lignes, totaux = _rapport_data(annee)

    totaux["total_documents_recus"] = totaux["recus"]
    totaux["documents_traites"] = totaux["traites"]
    totaux["documents_non_traites"] = totaux["non_traites"]

    printed_at = timezone.localtime(timezone.now()).strftime("%d/%m/%Y %H:%M")

    rel_logo = "documents/img/logo_cnss.png"
    logo_url = staticfiles_storage.url(rel_logo)
    logo_path = request.build_absolute_uri(logo_url)

    context = {
        "annee": annee,
        "lignes": lignes,
        "totaux": totaux,
        "printed_at": printed_at,
        "logo_path": logo_path,
    }

    html_string = render_to_string("documents/rapports_activites_detaille_pdf.html", context)
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri("/")).write_pdf()

    filename = f"rapport_activites_detaille_{annee}.pdf"
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    return response


# ==========================================================
# ✅ Fonctions utilitaires MENSUEL (UNE SEULE VERSION)
# ==========================================================

def _mois_label_fr(mois: int) -> str:
    for v, lbl in MOIS:
        if v == mois:
            return lbl.lower()
    return ""


def _de_ou_d(mois_label: str) -> str:
    return "d'" if mois_label[:1] in "aeiouâàäéèêëîïôöùûü" else "de "


def _rapport_mensuel_data(annee: int, mois: int):
    entrants_qs = DocumentEntrant.objects.filter(
        date_reception__year=annee,
        date_reception__month=mois,
    )
    prov = entrants_qs.filter(nature_document="PROV").count()
    kin = entrants_qs.filter(nature_document="KIN").count()

    traites = _entrants_traites_count(annee, mois)

    total_recus = prov + kin
    non_traites = max(total_recus - traites, 0)

    detail_signes = _compte_sortants_signes_detail(annee, mois)

    base = {
        "prov": prov,
        "kin": kin,
        "traites": traites,
        "non_traites": non_traites,
        "total_recus": total_recus,

        "documents_traites": traites,
        "documents_non_traites": non_traites,
        "total_documents_recus": total_recus,
    }
    base.update(detail_signes)
    return base


# ==========================================================
# ✅ NOUVEAUX RAPPORTS MENSUELS DÉTAILLÉS (HTML + PDF) — SEULS
# ==========================================================

@login_required(login_url='connexion')
def rapport_activites_mensuel_detaille(request):
    today = datetime.date.today()

    try:
        annee = int(request.GET.get("annee") or today.year)
    except ValueError:
        annee = today.year

    try:
        mois = int(request.GET.get("mois") or today.month)
    except ValueError:
        mois = today.month

    if mois < 1 or mois > 12:
        mois = today.month

    data = _rapport_mensuel_data(annee, mois)
    mois_label = _mois_label_fr(mois)
    de_d = _de_ou_d(mois_label)

    data.update({
        "annee": annee,
        "mois": mois,
        "MOIS": MOIS,
        "annees": _annees_disponibles(),
        "mois_label": mois_label,
        "de_d": de_d,
    })

    return render(request, "documents/rapport_activites_mensuel_detaille.html", data)


@login_required(login_url='connexion')
def rapport_activites_mensuel_detaille_pdf(request):
    from weasyprint import HTML

    today = timezone.localdate()

    try:
        annee = int(request.GET.get("annee") or today.year)
    except ValueError:
        annee = today.year

    try:
        mois = int(request.GET.get("mois") or today.month)
    except ValueError:
        mois = today.month

    if mois < 1 or mois > 12:
        mois = today.month

    data = _rapport_mensuel_data(annee, mois)
    mois_label = _mois_label_fr(mois)
    de_d = _de_ou_d(mois_label)

    printed_at = timezone.localtime(timezone.now()).strftime("%d/%m/%Y %H:%M")

    rel_logo = "documents/img/logo_cnss.png"
    logo_url = staticfiles_storage.url(rel_logo)
    logo_path = request.build_absolute_uri(logo_url)

    data.update({
        "annee": annee,
        "mois": mois,
        "mois_label": mois_label,
        "de_d": de_d,
        "printed_at": printed_at,
        "logo_path": logo_path,
    })

    html = render_to_string("documents/rapport_activites_mensuel_detaille_pdf.html", data)
    pdf = HTML(string=html, base_url=request.build_absolute_uri("/")).write_pdf()

    filename = f"rapport_activites_mensuel_detaille_{annee}_{mois:02d}.pdf"
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="{filename}"'
    return resp


# =========================
# ✅ Rapport d'activités MENSUEL (anciens - à garder)
# =========================

@login_required(login_url='connexion')
def rapport_activites_mensuel(request):
    today = datetime.date.today()

    try:
        annee = int(request.GET.get("annee") or today.year)
    except ValueError:
        annee = today.year

    try:
        mois = int(request.GET.get("mois") or today.month)
    except ValueError:
        mois = today.month

    data = _rapport_mensuel_data(annee, mois)
    mois_label = _mois_label_fr(mois)
    de_d = _de_ou_d(mois_label)

    data.update({
        "annee": annee,
        "mois": mois,
        "MOIS": MOIS,
        "annees": _annees_disponibles(),
        "mois_label": mois_label,
        "de_d": de_d,
    })

    return render(request, "documents/rapport_activites_mensuel.html", data)


@login_required(login_url='connexion')
def rapport_activites_mensuel_pdf(request):
    """
    ✅ PDF du rapport mensuel (ancien) - design KPI
    - Ajoute printed_at pour le footer
    - Ajoute logo_path (URL absolue) pour afficher le logo dans WeasyPrint
    """
    from weasyprint import HTML

    today = timezone.localdate()

    try:
        annee = int(request.GET.get("annee") or today.year)
    except ValueError:
        annee = today.year

    try:
        mois = int(request.GET.get("mois") or today.month)
    except ValueError:
        mois = today.month

    if mois < 1 or mois > 12:
        mois = today.month

    data = _rapport_mensuel_data(annee, mois)
    mois_label = _mois_label_fr(mois)
    de_d = _de_ou_d(mois_label)

    printed_at = timezone.localtime(timezone.now()).strftime("%d/%m/%Y %H:%M")

    rel_logo = "documents/img/logo_cnss.png"
    logo_url = staticfiles_storage.url(rel_logo)
    logo_path = request.build_absolute_uri(logo_url)

    data.update({
        "annee": annee,
        "mois": mois,
        "mois_label": mois_label,
        "de_d": de_d,
        "printed_at": printed_at,
        "logo_path": logo_path,
    })

    html = render_to_string("documents/rapport_activites_mensuel_pdf.html", data)
    pdf = HTML(string=html, base_url=request.build_absolute_uri("/")).write_pdf()

    filename = f"rapport_activites_mensuel_{annee}_{mois:02d}.pdf"
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="{filename}"'
    return resp


# =========================
# ✅ Rapport d'activités Hebdomadaire (Lundi -> Vendredi)
# =========================

def _normalize_monday_friday(debut_date: datetime.date, fin_date):
    monday = debut_date - timedelta(days=debut_date.weekday())
    if not fin_date:
        friday = monday + timedelta(days=4)
    else:
        friday = fin_date
        if friday < monday:
            friday = monday + timedelta(days=4)
    return monday, friday


def _date_range_exclusive(date_debut: datetime.date, date_fin_inclusive: datetime.date):
    end_exclusive = date_fin_inclusive + timedelta(days=1)
    return date_debut, end_exclusive


def _entrants_traites_range(date_debut: datetime.date, date_fin_inclusive: datetime.date) -> int:
    start, end_excl = _date_range_exclusive(date_debut, date_fin_inclusive)
    qs = DocumentEntrant.objects.filter(date_reception__gte=start, date_reception__lt=end_excl)

    field_name = "annotations_autorite"
    if not model_has_field(DocumentEntrant, field_name):
        return 0

    qs = qs.filter(**{f"{field_name}__isnull": False}).annotate(
        _ann_trim=Trim(F(field_name))
    ).exclude(_ann_trim="")
    return qs.count()


def _count_sortants_signes_range(Model, date_debut: datetime.date, date_fin_inclusive: datetime.date) -> int:
    start, end_excl = _date_range_exclusive(date_debut, date_fin_inclusive)
    qs = Model.objects.filter(date_sortie__gte=start, date_sortie__lt=end_excl)

    if model_has_field(Model, "statut"):
        qs = qs.filter(statut="SIGNE")

    if model_has_field(Model, "emetteur"):
        qs = qs.filter(emetteur__in=["DG", "DGA"])

    return qs.count()


def _rapport_hebdo_data(date_debut: datetime.date, date_fin: datetime.date):
    start, end_excl = _date_range_exclusive(date_debut, date_fin)

    entrants = DocumentEntrant.objects.filter(date_reception__gte=start, date_reception__lt=end_excl)
    recus_prov = entrants.filter(nature_document="PROV").count()
    recus_kin = entrants.filter(nature_document="KIN").count()

    traites = _entrants_traites_range(date_debut, date_fin)

    total_recus = recus_prov + recus_kin
    non_traites = max(total_recus - traites, 0)

    dossiers_chrono = _count_sortants_signes_range(Chrono, date_debut, date_fin)
    dossiers_gouv = _count_sortants_signes_range(Gouvernement, date_debut, date_fin)
    dossiers_pps = _count_sortants_signes_range(PaiementPrestationsSociales, date_debut, date_fin)
    dossiers_ap = _count_sortants_signes_range(AllocationsPrenatales, date_debut, date_fin)
    dossiers_om = _count_sortants_signes_range(OrdreMission, date_debut, date_fin)
    dossiers_decision = _count_sortants_signes_range(Decision, date_debut, date_fin)
    dossiers_af = _count_sortants_signes_range(AllocationsFamiliales, date_debut, date_fin)

    total_sortants = (
        dossiers_chrono + dossiers_gouv + dossiers_pps +
        dossiers_ap + dossiers_om + dossiers_decision + dossiers_af
    )

    return {
        "lundi": date_debut,
        "vendredi": date_fin,
        "debut_str": date_debut.strftime("%d/%m/%Y"),
        "fin_str": date_fin.strftime("%d/%m/%Y"),

        "recus_prov": recus_prov,
        "recus_kin": recus_kin,

        "traites": traites,
        "non_traites": non_traites,

        "total_recus": total_recus,

        "documents_traites": traites,
        "documents_non_traites": non_traites,
        "total_documents_recus": total_recus,

        "dossiers_chrono": dossiers_chrono,
        "dossiers_gouv": dossiers_gouv,
        "dossiers_pps": dossiers_pps,
        "dossiers_ap": dossiers_ap,
        "dossiers_om": dossiers_om,
        "dossiers_decision": dossiers_decision,
        "dossiers_af": dossiers_af,
        "total_sortants": total_sortants,
    }


@login_required(login_url='connexion')
def rapport_activites_hebdo(request):
    debut_str_get = (request.GET.get("debut") or "").strip()
    fin_str_get = (request.GET.get("fin") or "").strip()

    debut_date = parse_date(debut_str_get) if debut_str_get else datetime.date.today()
    if not debut_date:
        debut_date = datetime.date.today()

    fin_date = parse_date(fin_str_get) if fin_str_get else None

    lundi, vendredi = _normalize_monday_friday(debut_date, fin_date)
    data = _rapport_hebdo_data(lundi, vendredi)

    data["debut_input"] = lundi.strftime("%Y-%m-%d")
    data["fin_input"] = vendredi.strftime("%Y-%m-%d")

    return render(request, "documents/rapport_activites_hebdo.html", data)


@login_required(login_url='connexion')
def rapport_activites_hebdo_pdf(request):
    from weasyprint import HTML

    debut_str_get = (request.GET.get("debut") or "").strip()
    fin_str_get = (request.GET.get("fin") or "").strip()

    debut_date = parse_date(debut_str_get) if debut_str_get else datetime.date.today()
    if not debut_date:
        debut_date = datetime.date.today()

    fin_date = parse_date(fin_str_get) if fin_str_get else None

    lundi, vendredi = _normalize_monday_friday(debut_date, fin_date)
    data = _rapport_hebdo_data(lundi, vendredi)

    html = render_to_string("documents/rapport_activites_hebdo_pdf.html", data)
    pdf = HTML(string=html, base_url=request.build_absolute_uri("/")).write_pdf()

    filename = f"rapport_activites_hebdo_{lundi.strftime('%Y%m%d')}_{vendredi.strftime('%Y%m%d')}.pdf"
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="{filename}"'
    return resp
