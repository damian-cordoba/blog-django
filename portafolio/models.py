from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

# Solo se permiten tableros e informes embebidos de estos sitios.
DOMINIOS_EMBED = (
    "app.powerbi.com",
    "lookerstudio.google.com",
    "datastudio.google.com",
    "public.tableau.com",
    "docs.google.com",
    "www.youtube.com",
    "www.youtube-nocookie.com",
)


def validar_url_embed(valor):
    partes = urlparse(valor)
    if partes.scheme != "https" or partes.hostname not in DOMINIOS_EMBED:
        raise ValidationError(
            "Solo se pueden embeber enlaces https de Power BI, Looker Studio, Tableau Public, "
            "Google Docs/Sheets o YouTube."
        )


class Herramienta(models.Model):
    nombre = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "herramienta"
        verbose_name_plural = "herramientas"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Proyecto(models.Model):
    TIPOS = [
        ("cliente", "Cliente"),
        ("formacion", "Proyecto de formación"),
        ("personal", "Proyecto personal"),
    ]

    titulo = models.CharField("título", max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    tipo = models.CharField(max_length=10, choices=TIPOS, default="cliente")
    sector = models.CharField(max_length=80, blank=True, help_text="Ej.: Lubricentro, Estudio contable.")
    periodo = models.CharField("período", max_length=40, blank=True, help_text="Ej.: Diciembre 2025.")
    resumen = models.CharField(max_length=280, help_text="Una o dos oraciones para la tarjeta.")
    problema = models.TextField("el problema", help_text="Qué pasaba antes y por qué importaba.")
    solucion = models.TextField("la solución", help_text="Qué construiste y cómo.")
    resultados = models.TextField(blank=True, help_text="Impacto, cifras y hallazgos.")
    detalle_tecnico = models.TextField("detalle técnico", blank=True)
    nota = models.CharField(
        max_length=200, blank=True, help_text="Aclaración visible, por ejemplo sobre confidencialidad de datos."
    )
    herramientas = models.ManyToManyField(Herramienta, related_name="proyectos", blank=True)
    portada = models.ImageField(upload_to="proyectos/", blank=True, null=True)
    embed_url = models.URLField(
        "tablero embebido",
        blank=True,
        validators=[validar_url_embed],
        help_text="Enlace «Publicar en la web» de Power BI, Looker Studio, Tableau Public o YouTube.",
    )
    repositorio = models.URLField(blank=True)
    enlace_externo = models.URLField("más información", blank=True, help_text="Por ejemplo, la página en Notion.")
    destacado = models.BooleanField(default=False, help_text="Se muestra en la portada.")
    publicado = models.BooleanField(default=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["orden", "titulo"]
        verbose_name = "caso de estudio"
        verbose_name_plural = "casos de estudio"

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)[:180]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("detalle_proyecto", kwargs={"slug": self.slug})


class ImagenProyecto(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to="proyectos/galeria/")
    titulo = models.CharField("título", max_length=120, blank=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["orden", "pk"]
        verbose_name = "imagen"
        verbose_name_plural = "galería de imágenes"

    def __str__(self):
        return self.titulo or f"Imagen de {self.proyecto}"
