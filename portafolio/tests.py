import io
import shutil
import tempfile

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Herramienta, ImagenProyecto, Proyecto

MEDIA_TEMPORAL = tempfile.mkdtemp()


def imagen():
    buffer = io.BytesIO()
    Image.new("RGB", (30, 20), (10, 37, 64)).save(buffer, format="PNG")
    return SimpleUploadedFile("captura.png", buffer.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class ProyectosTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMPORAL, ignore_errors=True)

    def setUp(self):
        self.excel = Herramienta.objects.create(nombre="Excel")
        self.pbi = Herramienta.objects.create(nombre="Power BI")
        self.caso = Proyecto.objects.create(
            titulo="Sistema para lubricentro",
            tipo="cliente",
            resumen="Resumen del caso",
            problema="- Problema uno\n- Problema dos",
            solucion="Solución",
            destacado=True,
        )
        self.caso.herramientas.add(self.excel)
        self.tablero = Proyecto.objects.create(
            titulo="Tablero de ventas", tipo="personal", resumen="Otro", problema="p", solucion="s"
        )
        self.tablero.herramientas.add(self.pbi)
        self.oculto = Proyecto.objects.create(
            titulo="Borrador", resumen="x", problema="p", solucion="s", publicado=False
        )

    def test_slug_automatico(self):
        self.assertEqual(self.caso.slug, "sistema-para-lubricentro")

    def test_lista_muestra_solo_publicados(self):
        respuesta = self.client.get(reverse("lista_proyectos"))
        self.assertContains(respuesta, "Sistema para lubricentro")
        self.assertContains(respuesta, "Tablero de ventas")
        self.assertNotContains(respuesta, "Borrador")

    def test_filtro_por_herramienta(self):
        respuesta = self.client.get(reverse("lista_proyectos"), {"herramienta": "power-bi"})
        self.assertContains(respuesta, "Tablero de ventas")
        self.assertNotContains(respuesta, "Sistema para lubricentro")

    def test_filtro_por_tipo(self):
        respuesta = self.client.get(reverse("lista_proyectos"), {"tipo": "cliente"})
        self.assertContains(respuesta, "Sistema para lubricentro")
        self.assertNotContains(respuesta, "Tablero de ventas")

    def test_herramienta_inexistente_da_404(self):
        self.assertEqual(self.client.get(reverse("lista_proyectos"), {"herramienta": "nada"}).status_code, 404)

    def test_detalle_con_texto_enriquecido_y_contacto(self):
        respuesta = self.client.get(self.caso.get_absolute_url())
        self.assertContains(respuesta, "<li>Problema uno</li>", html=True)
        self.assertContains(respuesta, reverse("contacto") + "?origen=")

    def test_detalle_no_publicado_da_404(self):
        self.assertEqual(self.client.get(self.oculto.get_absolute_url()).status_code, 404)

    def test_galeria_e_imagen_de_portada(self):
        self.caso.portada = imagen()
        self.caso.save()
        ImagenProyecto.objects.create(proyecto=self.caso, imagen=imagen(), titulo="Tablero principal")
        respuesta = self.client.get(self.caso.get_absolute_url())
        self.assertContains(respuesta, "Tablero principal")
        self.assertContains(respuesta, self.caso.portada.url)

    def test_embed_solo_dominios_permitidos(self):
        self.caso.embed_url = "https://sitio-raro.com/tablero"
        with self.assertRaises(ValidationError):
            self.caso.full_clean()
        self.caso.embed_url = "https://app.powerbi.com/view?r=abc"
        self.caso.full_clean()
        self.caso.save()
        self.assertContains(self.client.get(self.caso.get_absolute_url()), "<iframe")

    def test_embed_rechaza_http(self):
        self.caso.embed_url = "http://app.powerbi.com/view?r=abc"
        with self.assertRaises(ValidationError):
            self.caso.full_clean()

    def test_portada_muestra_destacados(self):
        respuesta = self.client.get(reverse("inicio"))
        self.assertContains(respuesta, "Sistema para lubricentro")
        self.assertNotContains(respuesta, "Tablero de ventas")


class ContenidoProfesionalTest(TestCase):
    def test_comando_carga_y_no_duplica(self):
        call_command("cargar_contenido_profesional", stdout=io.StringIO())
        call_command("cargar_contenido_profesional", stdout=io.StringIO())
        self.assertEqual(Proyecto.objects.count(), 8)
        self.assertTrue(Proyecto.objects.filter(destacado=True).exists())
        for proyecto in Proyecto.objects.all():
            self.assertEqual(self.client.get(proyecto.get_absolute_url()).status_code, 200)

    def test_comando_respeta_ediciones_sin_actualizar(self):
        call_command("cargar_contenido_profesional", stdout=io.StringIO())
        caso = Proyecto.objects.first()
        caso.resumen = "Editado en el admin"
        caso.save()
        call_command("cargar_contenido_profesional", stdout=io.StringIO())
        caso.refresh_from_db()
        self.assertEqual(caso.resumen, "Editado en el admin")
        call_command("cargar_contenido_profesional", "--actualizar", stdout=io.StringIO())
        caso.refresh_from_db()
        self.assertNotEqual(caso.resumen, "Editado en el admin")
