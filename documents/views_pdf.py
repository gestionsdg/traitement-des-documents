from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q
from weasyprint import HTML

from .models import DocumentEntrant


def _render_pdf(template_name, context, filename):
    html_string = render_to_string(template_name, context)
    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    return response


def _get_qs_entrants(nature_code: str, traites: bool):
    qs = DocumentEntrant.objects.filter(nature_document=nature_code)

    # Traités = annotations_autorite non vide
    if traites:
        qs = qs.exclude(annotations_autorite__isnull=True).exclude(annotations_autorite__exact="")
    else:
        qs = qs.filter(Q(annotations_autorite__isnull=True) | Q(annotations_autorite__exact=""))

    return qs.order_by("-date_reception", "-numero_ordre")


def liste_entrants_kin_traites_pdf(request):
    qs = _get_qs_entrants("KIN", True)
    context = {
        "titre": "Liste des documents entrants traités de Kinshasa",
        "docs": qs,
        "date_print": timezone.localtime(timezone.now()),
    }
    return _render_pdf("documents/entrants_list_pdf.html", context, "entrants_kin_traites.pdf")


def liste_entrants_kin_non_traites_pdf(request):
    qs = _get_qs_entrants("KIN", False)
    context = {
        "titre": "Liste des documents entrants non traités de Kinshasa",
        "docs": qs,
        "date_print": timezone.localtime(timezone.now()),
    }
    return _render_pdf("documents/entrants_list_pdf.html", context, "entrants_kin_non_traites.pdf")


def liste_entrants_prov_traites_pdf(request):
    qs = _get_qs_entrants("PROV", True)
    context = {
        "titre": "Liste des documents entrants traités de Province",
        "docs": qs,
        "date_print": timezone.localtime(timezone.now()),
    }
    return _render_pdf("documents/entrants_list_pdf.html", context, "entrants_prov_traites.pdf")


def liste_entrants_prov_non_traites_pdf(request):
    qs = _get_qs_entrants("PROV", False)
    context = {
        "titre": "Liste des documents entrants non traités de Province",
        "docs": qs,
        "date_print": timezone.localtime(timezone.now()),
    }
    return _render_pdf("documents/entrants_list_pdf.html", context, "entrants_prov_non_traites.pdf")
