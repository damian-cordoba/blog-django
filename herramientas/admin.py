from django.contrib import admin

from .models import ResultadoDiagnostico


@admin.register(ResultadoDiagnostico)
class ResultadoDiagnosticoAdmin(admin.ModelAdmin):
    list_display = ["creado", "nivel", "puntaje"]
    list_filter = ["nivel", "creado"]
    readonly_fields = ["puntaje", "nivel", "respuestas", "creado"]

    def has_add_permission(self, request):
        return False
