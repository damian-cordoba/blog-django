import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from portafolio.models import Proyecto
from posts.models import Post

from .forms import ConsultaForm
from .models import PerfilProfesional, Servicio

logger = logging.getLogger(__name__)


def inicio(request):
    contexto = {
        "servicios": Servicio.objects.filter(activo=True, destacado=True)[:4],
        "proyectos": Proyecto.objects.filter(publicado=True, destacado=True).prefetch_related("herramientas")[:3],
        "posts": Post.objects.select_related("autor", "categoria")[:3],
    }
    return render(request, "sitio/inicio.html", contexto)


def sobre_mi(request):
    return render(request, "sitio/sobre_mi.html")


def servicios(request):
    return render(request, "sitio/servicios.html", {"servicios": Servicio.objects.filter(activo=True)})


def contacto(request):
    if request.method == "POST":
        form = ConsultaForm(request.POST)
        if form.is_valid():
            if form.es_spam():
                # Al bot se le responde igual que a una persona, pero no se guarda nada.
                messages.success(request, "¡Gracias! Recibí tu consulta y te respondo a la brevedad.")
                return redirect("contacto")
            consulta = form.save(commit=False)
            consulta.origen = request.POST.get("origen", "")[:60]
            consulta.save()
            _avisar_por_email(consulta)
            messages.success(request, "¡Gracias! Recibí tu consulta y te respondo a la brevedad.")
            return redirect("contacto")
    else:
        inicial = {}
        slug = request.GET.get("servicio")
        if slug:
            inicial["servicio"] = Servicio.objects.filter(slug=slug, activo=True).first()
        if request.GET.get("mensaje"):
            inicial["mensaje"] = request.GET["mensaje"][:500]
        form = ConsultaForm(initial=inicial)

    return render(request, "sitio/contacto.html", {"form": form, "origen": request.GET.get("origen", "")})


def _avisar_por_email(consulta):
    """Envía un aviso al correo del perfil. Si el correo no está configurado,
    la consulta igual queda guardada en el panel de administración."""
    destino = PerfilProfesional.cargar().email
    if not destino:
        return
    cuerpo = (
        f"Nombre: {consulta.nombre}\nEmail: {consulta.email}\nEmpresa: {consulta.empresa}\n"
        f"Teléfono: {consulta.telefono}\nServicio: {consulta.servicio or '-'}\nOrigen: {consulta.origen or '-'}\n\n"
        f"{consulta.mensaje}"
    )
    try:
        send_mail(
            f"Nueva consulta de {consulta.nombre}",
            cuerpo,
            settings.DEFAULT_FROM_EMAIL,
            [destino],
        )
    except Exception:  # el sitio no debe fallar si el correo no está disponible
        logger.exception("No se pudo enviar el aviso de la consulta %s", consulta.pk)
