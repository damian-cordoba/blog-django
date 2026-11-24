from django.conf import settings
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil(sender, instance, created, **kwargs):
    """Crea el perfil automáticamente cada vez que se registra un usuario
    (también al usar createsuperuser)."""
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(pre_save, sender=Profile)
def borrar_avatar_reemplazado(sender, instance, **kwargs):
    """Elimina el avatar anterior si se reemplaza o se quita."""
    if not instance.pk:
        return
    anterior = Profile.objects.filter(pk=instance.pk).values_list("avatar", flat=True).first()
    if anterior and anterior != instance.avatar.name:
        instance.avatar.storage.delete(anterior)


@receiver(post_delete, sender=Profile)
def borrar_avatar_al_eliminar(sender, instance, **kwargs):
    if instance.avatar:
        instance.avatar.delete(save=False)
