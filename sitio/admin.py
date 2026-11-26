from django.contrib import admin

from .models import Consulta, PerfilProfesional, Servicio


@admin.register(PerfilProfesional)
class PerfilProfesionalAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Presentación", {"fields": ["nombre", "titular", "bio_corta", "bio", "foto"]}),
        ("Datos", {"fields": ["ubicacion", "idiomas", "disponibilidad", "habilidades", "formacion"]}),
        ("Contacto y redes", {"fields": ["email", "whatsapp", "whatsapp_mensaje", "linkedin", "github", "portafolio_notion"]}),
    ]

    def has_add_permission(self, request):
        return not PerfilProfesional.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ["nombre", "modalidad", "destacado", "activo", "orden"]
    list_editable = ["destacado", "activo", "orden"]
    prepopulated_fields = {"slug": ["nombre"]}


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "email", "empresa", "servicio", "origen", "estado", "creada"]
    list_filter = ["estado", "servicio", "origen", "creada"]
    list_editable = ["estado"]
    search_fields = ["nombre", "email", "empresa", "mensaje"]
    readonly_fields = ["nombre", "email", "empresa", "telefono", "servicio", "mensaje", "origen", "creada"]
    fields = readonly_fields + ["estado", "notas"]

    def has_add_permission(self, request):
        return False
