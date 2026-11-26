from django.contrib import admin

from .models import Herramienta, ImagenProyecto, Proyecto


class ImagenProyectoInline(admin.TabularInline):
    model = ImagenProyecto
    extra = 1


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ["titulo", "tipo", "sector", "destacado", "publicado", "orden"]
    list_editable = ["destacado", "publicado", "orden"]
    list_filter = ["tipo", "herramientas", "publicado"]
    search_fields = ["titulo", "resumen", "problema", "solucion"]
    prepopulated_fields = {"slug": ["titulo"]}
    filter_horizontal = ["herramientas"]
    inlines = [ImagenProyectoInline]
    fieldsets = [
        (None, {"fields": ["titulo", "slug", "tipo", "sector", "periodo", "resumen", "herramientas"]}),
        ("Contenido", {"fields": ["problema", "solucion", "resultados", "detalle_tecnico", "nota"]}),
        ("Imágenes y enlaces", {"fields": ["portada", "embed_url", "repositorio", "enlace_externo"]}),
        ("Publicación", {"fields": ["destacado", "publicado", "orden"]}),
    ]


@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "orden"]
    list_editable = ["orden"]
    prepopulated_fields = {"slug": ["nombre"]}
