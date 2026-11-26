from urllib.parse import quote

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class PerfilProfesional(models.Model):
    """Datos de presentación del autor del sitio. Hay un solo registro (pk=1),
    editable desde el panel de administración."""

    nombre = models.CharField(max_length=120, default="Damián Emiliano Cordoba")
    titular = models.CharField(
        max_length=160,
        default="Analista de datos · BI y automatización para PyMEs",
        help_text="Frase corta que aparece debajo del nombre.",
    )
    bio_corta = models.TextField(
        "biografía corta",
        max_length=400,
        blank=True,
        help_text="Dos o tres oraciones para la portada.",
    )
    bio = models.TextField("biografía completa", blank=True, help_text="Texto de la página Sobre mí.")
    foto = models.ImageField(upload_to="perfil/", blank=True, null=True)
    ubicacion = models.CharField("ubicación", max_length=120, blank=True)
    idiomas = models.CharField(max_length=120, blank=True)
    disponibilidad = models.CharField(max_length=120, blank=True)
    habilidades = models.TextField(blank=True, help_text="Una habilidad por línea.")
    formacion = models.TextField("formación", blank=True, help_text="Un ítem por línea.")
    email = models.EmailField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    portafolio_notion = models.URLField("portafolio en Notion", blank=True)
    whatsapp = models.CharField(
        max_length=20,
        blank=True,
        help_text="Número con código de país y sin espacios ni signos, por ejemplo 5493871234567. "
        "Si queda vacío, no se muestra el botón de WhatsApp.",
    )
    whatsapp_mensaje = models.CharField(
        "mensaje de WhatsApp",
        max_length=300,
        blank=True,
        default="Hola Damián, te escribo desde tu sitio Datos en Criollo. Quería consultarte por ",
        help_text="Texto que aparece escrito al abrir el chat; la persona puede cambiarlo antes de enviar. "
        "Si queda vacío, el chat se abre sin mensaje.",
    )

    class Meta:
        verbose_name = "perfil profesional"
        verbose_name_plural = "perfil profesional"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.pk = 1  # registro único
        super().save(*args, **kwargs)

    @classmethod
    def cargar(cls):
        perfil, _ = cls.objects.get_or_create(pk=1)
        return perfil

    @property
    def lista_habilidades(self):
        return [linea.strip() for linea in self.habilidades.splitlines() if linea.strip()]

    @property
    def lista_formacion(self):
        return [linea.strip() for linea in self.formacion.splitlines() if linea.strip()]

    @property
    def whatsapp_url(self):
        numero = "".join(c for c in self.whatsapp if c.isdigit())
        if not numero:
            return ""
        url = f"https://wa.me/{numero}"
        if self.whatsapp_mensaje.strip():
            url += "?text=" + quote(self.whatsapp_mensaje)
        return url


class Servicio(models.Model):
    MODALIDADES = [
        ("proyecto", "Por proyecto"),
        ("hora", "Por hora"),
        ("ambas", "Por proyecto o por hora"),
    ]

    nombre = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    icono = models.CharField(max_length=8, blank=True, help_text="Un emoji, por ejemplo 📊.")
    resumen = models.CharField(max_length=220, help_text="Una oración para las tarjetas.")
    descripcion = models.TextField("descripción", blank=True)
    incluye = models.TextField(blank=True, help_text="Qué incluye el servicio. Un ítem por línea.")
    herramientas = models.CharField(max_length=200, blank=True, help_text="Separadas por coma.")
    modalidad = models.CharField(max_length=10, choices=MODALIDADES, default="ambas")
    destacado = models.BooleanField(default=False, help_text="Se muestra en la portada.")
    activo = models.BooleanField(default=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "servicio"
        verbose_name_plural = "servicios"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)[:140]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("servicios") + f"#{self.slug}"

    @property
    def lista_incluye(self):
        return [linea.strip() for linea in self.incluye.splitlines() if linea.strip()]

    @property
    def lista_herramientas(self):
        return [h.strip() for h in self.herramientas.split(",") if h.strip()]


class Consulta(models.Model):
    """Mensaje enviado desde el formulario de contacto."""

    ESTADOS = [
        ("nueva", "Nueva"),
        ("en_curso", "En curso"),
        ("respondida", "Respondida"),
        ("archivada", "Archivada"),
    ]

    nombre = models.CharField(max_length=120)
    email = models.EmailField()
    empresa = models.CharField("empresa o negocio", max_length=120, blank=True)
    telefono = models.CharField("teléfono", max_length=40, blank=True)
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consultas",
        verbose_name="servicio de interés",
    )
    mensaje = models.TextField()
    origen = models.CharField(
        max_length=60, blank=True, help_text="Desde dónde llegó la consulta (diagnóstico, calculadora…)."
    )
    estado = models.CharField(max_length=12, choices=ESTADOS, default="nueva")
    notas = models.TextField("notas internas", blank=True)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creada"]
        verbose_name = "consulta"
        verbose_name_plural = "consultas"

    def __str__(self):
        return f"{self.nombre} — {self.creada:%d/%m/%Y}"
