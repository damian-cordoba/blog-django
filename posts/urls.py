from django.urls import path

from .views import PostCreateView, PostDeleteView, PostDetailView, PostListView, PostUpdateView

urlpatterns = [
    path("blog/", PostListView.as_view(), name="lista_posts"),
    # "crear" va antes de <slug> para que no se interprete como un slug.
    path("posts/crear/", PostCreateView.as_view(), name="crear_post"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="detalle_post"),
    path("posts/<slug:slug>/editar/", PostUpdateView.as_view(), name="editar_post"),
    path("posts/<slug:slug>/eliminar/", PostDeleteView.as_view(), name="eliminar_post"),
    path("blog/categoria/<slug:slug>/", PostListView.as_view(), name="posts_por_categoria"),
]
