from django.db import models


class ResultadoDiagnostico(models.Model):
    """Resultado anónimo de un diagnóstico, para ver en el admin qué tan maduras
    llegan las PyMEs que usan la herramienta. No guarda datos personales."""

    puntaje = models.PositiveSmallIntegerField()
    nivel = models.CharField(max_length=30)
    respuestas = models.JSONField()
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "resultado de diagnóstico"
        verbose_name_plural = "resultados de diagnóstico"

    def __str__(self):
        return f"{self.nivel} ({self.puntaje}) — {self.creado:%d/%m/%Y}"
