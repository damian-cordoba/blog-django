from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm, RegistroForm, UsuarioForm
from .models import Profile


def registro(request):
    """Alta de usuario. Al registrarse, el usuario queda con la sesión iniciada."""
    if request.user.is_authenticated:
        return redirect("lista_posts")

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()  # el perfil se crea con la señal post_save
            login(request, usuario)
            messages.success(request, f"¡Bienvenido/a, {usuario.username}! Tu cuenta ya está lista.")
            return redirect("lista_posts")
    else:
        form = RegistroForm()

    return render(request, "usuarios/registro.html", {"form": form})


def perfil_autor(request, username):
    """Perfil público de un autor con sus publicaciones."""
    autor = get_object_or_404(User, username=username)
    perfil, _ = Profile.objects.get_or_create(user=autor)
    posts = autor.posts.select_related("categoria")
    return render(
        request,
        "usuarios/perfil.html",
        {"autor": autor, "perfil": perfil, "posts": posts, "es_propio": request.user == autor},
    )


@login_required
def mi_perfil(request):
    return perfil_autor(request, request.user.username)


@login_required
def editar_perfil(request):
    perfil, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        usuario_form = UsuarioForm(request.POST, instance=request.user)
        perfil_form = ProfileForm(request.POST, request.FILES, instance=perfil)
        if usuario_form.is_valid() and perfil_form.is_valid():
            with transaction.atomic():
                usuario_form.save()
                perfil_form.save()
            messages.success(request, "Tu perfil se actualizó correctamente.")
            return redirect("mi_perfil")
    else:
        usuario_form = UsuarioForm(instance=request.user)
        perfil_form = ProfileForm(instance=perfil)

    return render(
        request,
        "usuarios/editar_perfil.html",
        {"usuario_form": usuario_form, "perfil_form": perfil_form},
    )
