from django.urls import path

from . import views

urlpatterns = [
    path("", views.indice, name="herramientas"),
    path("punto-de-equilibrio/", views.punto_equilibrio, name="punto_equilibrio"),
    path("precio-y-margen/", views.precio_margen, name="precio_margen"),
    path("descuentos/", views.descuento, name="descuento"),
    path("diagnostico/", views.diagnostico, name="diagnostico"),
]
