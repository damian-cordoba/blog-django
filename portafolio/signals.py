from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import ImagenProyecto, Proyecto


@receiver(post_delete, sender=ImagenProyecto)
def borrar_archivo_de_galeria(sender, instance, **kwargs):
    if instance.imagen:
        instance.imagen.delete(save=False)


@receiver(post_delete, sender=Proyecto)
def borrar_portada(sender, instance, **kwargs):
    if instance.portada:
        instance.portada.delete(save=False)


@receiver(pre_save, sender=Proyecto)
def borrar_portada_reemplazada(sender, instance, **kwargs):
    if not instance.pk:
        return
    anterior = Proyecto.objects.filter(pk=instance.pk).values_list("portada", flat=True).first()
    if anterior and anterior != instance.portada.name:
        instance.portada.storage.delete(anterior)
