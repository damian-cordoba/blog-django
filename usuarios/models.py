from django.conf import settings
from django.db import models
from django.urls import reverse


class Profile(models.Model):
    """Datos extra del usuario, relacionados 1 a 1 con el User de Django."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="usuario",
    )
    avatar = models.ImageField(
        upload_to="avatares/",
        blank=True,
        null=True,
        help_text="Opcional. Imagen cuadrada, hasta 2 MB.",
    )
    bio = models.TextField("biografía", max_length=400, blank=True)
    sitio_web = models.URLField("sitio web o LinkedIn", blank=True)

    class Meta:
        verbose_name = "perfil"
        verbose_name_plural = "perfiles"

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def get_absolute_url(self):
        return reverse("perfil_autor", kwargs={"username": self.user.username})
