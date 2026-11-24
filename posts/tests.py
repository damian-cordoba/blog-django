import io
import shutil
import tempfile
from pathlib import Path

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Categoria, Post

MEDIA_TEMPORAL = tempfile.mkdtemp()


def imagen_de_prueba(nombre="prueba.jpg"):
    """Genera una imagen JPG válida en memoria para simular una subida."""
    buffer = io.BytesIO()
    Image.new("RGB", (40, 30), (0, 133, 161)).save(buffer, format="JPEG")
    return SimpleUploadedFile(nombre, buffer.getvalue(), content_type="image/jpeg")


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class BasePostTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMPORAL, ignore_errors=True)

    def setUp(self):
        self.autor = User.objects.create_user("autora", "autora@example.com", "Clave-segura-123")
        self.otro = User.objects.create_user("otro", "otro@example.com", "Clave-segura-123")
        self.excel = Categoria.objects.get(slug="excel")
        self.post = Post.objects.create(
            titulo="Tablas dinámicas en Excel",
            contenido="Resumen de ventas por mes con una tabla dinámica.",
            categoria=self.excel,
            autor=self.autor,
        )


class ListadoYDetalleTest(BasePostTest):
    def test_categorias_iniciales_creadas_por_migracion(self):
        self.assertEqual(Categoria.objects.count(), 6)

    def test_listado_muestra_posts(self):
        respuesta = self.client.get(reverse("lista_posts"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, self.post.titulo)

    def test_detalle_sin_imagen_no_falla(self):
        respuesta = self.client.get(self.post.get_absolute_url())
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, self.post.contenido)
        self.assertNotContains(respuesta, "imagen-post")

    def test_detalle_inexistente_da_404(self):
        respuesta = self.client.get(reverse("detalle_post", kwargs={"slug": "no-existe"}))
        self.assertEqual(respuesta.status_code, 404)

    def test_slug_unico_y_reservado(self):
        repetido = Post.objects.create(titulo=self.post.titulo, contenido="x", autor=self.autor)
        reservado = Post.objects.create(titulo="Crear", contenido="x", autor=self.autor)
        self.assertNotEqual(repetido.slug, self.post.slug)
        self.assertEqual(reservado.slug, "crear-2")

    def test_filtro_por_categoria(self):
        Post.objects.create(titulo="Medidas DAX", contenido="x", autor=self.autor,
                            categoria=Categoria.objects.get(slug="power-bi"))
        respuesta = self.client.get(reverse("posts_por_categoria", kwargs={"slug": "excel"}))
        self.assertContains(respuesta, self.post.titulo)
        self.assertNotContains(respuesta, "Medidas DAX")


class BusquedaTest(BasePostTest):
    def test_busca_por_titulo(self):
        respuesta = self.client.get(reverse("lista_posts"), {"q": "dinámicas"})
        self.assertContains(respuesta, self.post.titulo)

    def test_busca_por_contenido(self):
        respuesta = self.client.get(reverse("lista_posts"), {"q": "ventas por mes"})
        self.assertContains(respuesta, self.post.titulo)

    def test_sin_coincidencias_muestra_aviso(self):
        respuesta = self.client.get(reverse("lista_posts"), {"q": "blockchain"})
        self.assertContains(respuesta, "No encontramos coincidencias")

    def test_busqueda_vacia_muestra_todo_y_avisa(self):
        respuesta = self.client.get(reverse("lista_posts"), {"q": "   "})
        self.assertContains(respuesta, "Escribí una palabra para buscar")
        self.assertContains(respuesta, self.post.titulo)


class RutasProtegidasTest(BasePostTest):
    """El visitante anónimo es redirigido al login, incluso por URL directa."""

    def assertRedirigeAlLogin(self, respuesta, url):
        self.assertRedirects(respuesta, f"{reverse('login')}?next={url}")

    def test_anonimo_no_puede_crear(self):
        url = reverse("crear_post")
        self.assertRedirigeAlLogin(self.client.get(url), url)
        self.assertRedirigeAlLogin(self.client.post(url, {"titulo": "x", "contenido": "y"}), url)
        self.assertEqual(Post.objects.count(), 1)

    def test_anonimo_no_puede_editar(self):
        url = reverse("editar_post", kwargs={"slug": self.post.slug})
        self.assertRedirigeAlLogin(self.client.get(url), url)
        self.client.post(url, {"titulo": "Hackeado", "contenido": "y"})
        self.post.refresh_from_db()
        self.assertEqual(self.post.titulo, "Tablas dinámicas en Excel")

    def test_anonimo_no_puede_eliminar(self):
        url = reverse("eliminar_post", kwargs={"slug": self.post.slug})
        self.assertRedirigeAlLogin(self.client.get(url), url)
        self.assertRedirigeAlLogin(self.client.post(url), url)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_otro_usuario_no_puede_editar_ni_eliminar(self):
        self.client.login(username="otro", password="Clave-segura-123")
        editar = reverse("editar_post", kwargs={"slug": self.post.slug})
        eliminar = reverse("eliminar_post", kwargs={"slug": self.post.slug})
        self.assertEqual(self.client.get(editar).status_code, 403)
        self.assertEqual(self.client.post(editar, {"titulo": "x", "contenido": "y"}).status_code, 403)
        self.assertEqual(self.client.post(eliminar).status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_botones_de_edicion_solo_para_el_autor(self):
        self.client.login(username="otro", password="Clave-segura-123")
        respuesta = self.client.get(self.post.get_absolute_url())
        self.assertNotContains(respuesta, reverse("editar_post", kwargs={"slug": self.post.slug}))

    def test_staff_puede_editar(self):
        self.otro.is_staff = True
        self.otro.save()
        self.client.login(username="otro", password="Clave-segura-123")
        url = reverse("editar_post", kwargs={"slug": self.post.slug})
        self.assertEqual(self.client.get(url).status_code, 200)


class CrudAutenticadoTest(BasePostTest):
    def setUp(self):
        super().setUp()
        self.client.login(username="autora", password="Clave-segura-123")

    def test_crear_post_con_imagen(self):
        respuesta = self.client.post(reverse("crear_post"), {
            "titulo": "Mi primer tablero",
            "subtitulo": "Paso a paso",
            "categoria": self.excel.pk,
            "contenido": "Contenido del tablero.",
            "imagen": imagen_de_prueba(),
        })
        nuevo = Post.objects.get(titulo="Mi primer tablero")
        self.assertRedirects(respuesta, nuevo.get_absolute_url())
        self.assertEqual(nuevo.autor, self.autor)
        self.assertTrue(nuevo.imagen.name.startswith("posts/"))
        self.assertTrue(Path(nuevo.imagen.path).exists())

        detalle = self.client.get(nuevo.get_absolute_url())
        self.assertContains(detalle, nuevo.imagen.url)

    def test_crear_post_sin_imagen(self):
        self.client.post(reverse("crear_post"), {"titulo": "Sin foto", "contenido": "Texto."})
        nuevo = Post.objects.get(titulo="Sin foto")
        self.assertFalse(nuevo.imagen)
        self.assertEqual(self.client.get(reverse("lista_posts")).status_code, 200)

    def test_formulario_invalido_no_guarda(self):
        respuesta = self.client.post(reverse("crear_post"), {"titulo": "", "contenido": ""})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Post.objects.count(), 1)

    def test_archivo_que_no_es_imagen_se_rechaza(self):
        falso = SimpleUploadedFile("virus.jpg", b"no soy una imagen", content_type="image/jpeg")
        respuesta = self.client.post(reverse("crear_post"), {"titulo": "X", "contenido": "Y", "imagen": falso})
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Post.objects.filter(titulo="X").exists())

    def test_editar_post(self):
        url = reverse("editar_post", kwargs={"slug": self.post.slug})
        respuesta = self.client.post(url, {"titulo": "Título nuevo", "contenido": "Contenido nuevo"})
        self.post.refresh_from_db()
        self.assertRedirects(respuesta, self.post.get_absolute_url())
        self.assertEqual(self.post.titulo, "Título nuevo")
        self.assertEqual(self.post.slug, "tablas-dinamicas-en-excel")  # la URL no cambia

    def test_eliminar_post_borra_tambien_la_imagen(self):
        self.post.imagen = imagen_de_prueba()
        self.post.save()
        ruta = Path(self.post.imagen.path)
        self.assertTrue(ruta.exists())

        respuesta = self.client.post(reverse("eliminar_post", kwargs={"slug": self.post.slug}))
        self.assertRedirects(respuesta, reverse("lista_posts"))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())
        self.assertFalse(ruta.exists())


class DatosDemoTest(BasePostTest):
    def test_comando_carga_y_no_duplica(self):
        call_command("cargar_datos_demo", stdout=io.StringIO())
        call_command("cargar_datos_demo", stdout=io.StringIO())
        demo = Post.objects.filter(autor__username="equipo_datos")
        self.assertEqual(demo.count(), 6)
        self.assertEqual(demo.exclude(imagen="").exclude(imagen=None).count(), 4)
        self.assertEqual(self.client.get(reverse("lista_posts")).status_code, 200)
