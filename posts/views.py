from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import PostForm
from .models import Categoria, Post


class PostListView(ListView):
    """Lista de publicaciones. Admite búsqueda (?q=) y filtro por categoría."""

    model = Post
    template_name = "posts/post_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        queryset = Post.objects.select_related("autor", "categoria")

        self.categoria = None
        if "slug" in self.kwargs:
            self.categoria = get_object_or_404(Categoria, slug=self.kwargs["slug"])
            queryset = queryset.filter(categoria=self.categoria)

        self.busqueda_enviada = "q" in self.request.GET
        self.termino = self.request.GET.get("q", "").strip()
        if self.termino:
            queryset = queryset.filter(
                Q(titulo__icontains=self.termino)
                | Q(subtitulo__icontains=self.termino)
                | Q(contenido__icontains=self.termino)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categoria_actual"] = self.categoria
        context["termino"] = self.termino
        context["busqueda_vacia"] = self.busqueda_enviada and not self.termino
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "posts/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.select_related("autor", "categoria")


class AutorRequeridoMixin(UserPassesTestMixin):
    """Permite editar o eliminar solo al autor del post (o a un usuario staff).

    Se usa siempre después de LoginRequiredMixin: el visitante anónimo es
    enviado al login y el usuario autenticado que no es autor recibe un 403.
    """

    def test_func(self):
        return self.get_object().puede_editar(self.request.user)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"
    extra_context = {"titulo_pagina": "Nueva publicación", "texto_boton": "Publicar"}

    def form_valid(self, form):
        form.instance.autor = self.request.user
        messages.success(self.request, "La publicación se creó correctamente.")
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, AutorRequeridoMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"
    extra_context = {"titulo_pagina": "Editar publicación", "texto_boton": "Guardar cambios"}

    def form_valid(self, form):
        messages.success(self.request, "La publicación se actualizó correctamente.")
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, AutorRequeridoMixin, DeleteView):
    model = Post
    template_name = "posts/post_confirm_delete.html"
    success_url = reverse_lazy("lista_posts")

    def form_valid(self, form):
        messages.success(self.request, f"Se eliminó la publicación «{self.object.titulo}».")
        return super().form_valid(form)
