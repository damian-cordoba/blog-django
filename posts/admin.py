from django.contrib import admin

from .models import Categoria, Post


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "slug"]
    prepopulated_fields = {"slug": ["nombre"]}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["titulo", "autor", "categoria", "creado"]
    list_filter = ["categoria", "creado"]
    search_fields = ["titulo", "contenido"]
    readonly_fields = ["slug", "creado", "actualizado"]
