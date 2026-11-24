from django.urls import path
from django.views.generic import TemplateView

from .views import PostCreateView, PostDeleteView, PostDetailView, PostListView, PostUpdateView

urlpatterns = [
    path("", PostListView.as_view(), name="lista_posts"),
    # "crear" va antes de <slug> para que no se interprete como un slug.
    path("posts/crear/", PostCreateView.as_view(), name="crear_post"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="detalle_post"),
    path("posts/<slug:slug>/editar/", PostUpdateView.as_view(), name="editar_post"),
    path("posts/<slug:slug>/eliminar/", PostDeleteView.as_view(), name="eliminar_post"),
    path("acerca/", TemplateView.as_view(template_name="acerca.html"), name="acerca"),
    path("categoria/<slug:slug>/", PostListView.as_view(), name="posts_por_categoria"),
]
