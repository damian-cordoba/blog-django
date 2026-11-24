from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Post


@receiver(post_delete, sender=Post)
def borrar_imagen_al_eliminar(sender, instance, **kwargs):
    """Elimina el archivo de imagen cuando se borra la publicación."""
    if instance.imagen:
        instance.imagen.delete(save=False)


@receiver(pre_save, sender=Post)
def borrar_imagen_reemplazada(sender, instance, **kwargs):
    """Elimina la imagen anterior si se reemplaza o se quita al editar."""
    if not instance.pk:
        return
    anterior = Post.objects.filter(pk=instance.pk).values_list("imagen", flat=True).first()
    if anterior and anterior != instance.imagen.name:
        instance.imagen.storage.delete(anterior)
