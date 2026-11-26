from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("sobre-mi/", views.sobre_mi, name="sobre_mi"),
    path("servicios/", views.servicios, name="servicios"),
    path("contacto/", views.contacto, name="contacto"),
]
