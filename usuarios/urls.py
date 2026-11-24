from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    path("cuentas/registro/", views.registro, name="registro"),
    path(
        "cuentas/login/",
        auth_views.LoginView.as_view(
            template_name="usuarios/login.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    # LogoutView solo acepta POST (el botón del menú es un formulario).
    path("cuentas/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("cuentas/perfil/", views.mi_perfil, name="mi_perfil"),
    path("cuentas/perfil/editar/", views.editar_perfil, name="editar_perfil"),
    path("autores/<str:username>/", views.perfil_autor, name="perfil_autor"),
]
