from django.db.models import Count

from .models import Categoria


def categorias(request):
    """Pone la lista de categorías a disposición de todos los templates (menú)."""
    return {
        "categorias_menu": Categoria.objects.annotate(total_posts=Count("posts")),
    }
