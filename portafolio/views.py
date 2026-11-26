from urllib.parse import urlencode

from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Herramienta, Proyecto


def lista_proyectos(request):
    proyectos = Proyecto.objects.filter(publicado=True).prefetch_related("herramientas")

    herramienta = None
    if request.GET.get("herramienta"):
        herramienta = get_object_or_404(Herramienta, slug=request.GET["herramienta"])
        proyectos = proyectos.filter(herramientas=herramienta)

    tipo = request.GET.get("tipo", "")
    if tipo in dict(Proyecto.TIPOS):
        proyectos = proyectos.filter(tipo=tipo)
    else:
        tipo = ""

    contexto = {
        "proyectos": proyectos,
        "herramientas": Herramienta.objects.filter(proyectos__publicado=True).distinct(),
        "herramienta_actual": herramienta,
        "tipo_actual": tipo,
        "tipos": Proyecto.TIPOS,
    }
    return render(request, "portafolio/lista.html", contexto)


def detalle_proyecto(request, slug):
    proyecto = get_object_or_404(
        Proyecto.objects.prefetch_related("herramientas", "imagenes"), slug=slug, publicado=True
    )
    otros = Proyecto.objects.filter(publicado=True).exclude(pk=proyecto.pk)[:3]
    contacto_url = reverse("contacto") + "?" + urlencode(
        {
            "origen": f"caso: {proyecto.slug}"[:60],
            "mensaje": f"Vi el caso «{proyecto.titulo}» y quiero algo similar para mi negocio.",
        }
    )
    return render(
        request, "portafolio/detalle.html", {"proyecto": proyecto, "otros": otros, "contacto_url": contacto_url}
    )
