from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

# Slugs que coinciden con rutas fijas de la app y no pueden usarse para un post.
SLUGS_RESERVADOS = {"crear"}


class Categoria(models.Model):
    """Tema al que pertenece una publicación (Excel, SQL, Power BI, etc.)."""

    nombre = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True)
    descripcion = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("posts_por_categoria", kwargs={"slug": self.slug})


class Post(models.Model):
    """Publicación del blog."""

    titulo = models.CharField("título", max_length=200)
    slug = models.SlugField(max_length=220, unique=True, editable=False)
    subtitulo = models.CharField("subtítulo", max_length=250, blank=True)
    contenido = models.TextField()
    imagen = models.ImageField(
        upload_to="posts/",
        blank=True,
        null=True,
        help_text="Opcional. Formatos JPG, PNG, GIF o WEBP, hasta 5 MB.",
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="categoría",
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "publicación"
        verbose_name_plural = "publicaciones"

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        # El slug se genera una sola vez, al crear el post, para que la URL
        # no cambie si después se edita el título.
        if not self.slug:
            self.slug = self._generar_slug_unico()
        super().save(*args, **kwargs)

    def _generar_slug_unico(self):
        base = slugify(self.titulo)[:200] or "post"
        slug = base
        numero = 2
        while slug in SLUGS_RESERVADOS or Post.objects.filter(slug=slug).exists():
            slug = f"{base}-{numero}"
            numero += 1
        return slug

    def get_absolute_url(self):
        return reverse("detalle_post", kwargs={"slug": self.slug})

    def puede_editar(self, usuario):
        """Solo el autor o un usuario staff puede editar o eliminar el post."""
        return usuario.is_authenticated and (usuario == self.autor or usuario.is_staff)
