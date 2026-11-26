from .models import PerfilProfesional


def perfil(request):
    """Datos del perfil (nombre, redes, WhatsApp) para el menú y el pie de todas las páginas."""
    return {"perfil": PerfilProfesional.cargar()}
