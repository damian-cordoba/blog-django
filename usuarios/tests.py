import io
import shutil
import tempfile
from pathlib import Path

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Profile

MEDIA_TEMPORAL = tempfile.mkdtemp()


def avatar_de_prueba():
    buffer = io.BytesIO()
    Image.new("RGB", (50, 50), (240, 180, 41)).save(buffer, format="PNG")
    return SimpleUploadedFile("avatar.png", buffer.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class UsuariosTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMPORAL, ignore_errors=True)

    def registrar(self, username="nuevo", email="nuevo@example.com"):
        return self.client.post(reverse("registro"), {
            "username": username,
            "email": email,
            "first_name": "Nuevo",
            "last_name": "Usuario",
            "password1": "Clave-segura-123",
            "password2": "Clave-segura-123",
        })

    def test_registro_crea_usuario_perfil_e_inicia_sesion(self):
        respuesta = self.registrar()
        self.assertRedirects(respuesta, reverse("lista_posts"))
        usuario = User.objects.get(username="nuevo")
        self.assertTrue(Profile.objects.filter(user=usuario).exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), usuario.pk)

    def test_registro_rechaza_email_repetido(self):
        self.registrar()
        self.client.logout()
        respuesta = self.registrar(username="otro", email="NUEVO@example.com")
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(User.objects.filter(username="otro").exists())

    def test_registro_rechaza_contrasenias_distintas(self):
        self.client.post(reverse("registro"), {
            "username": "x", "email": "x@example.com",
            "password1": "Clave-segura-123", "password2": "Otra-clave-456",
        })
        self.assertFalse(User.objects.filter(username="x").exists())

    def test_login_y_logout(self):
        User.objects.create_user("ana", "ana@example.com", "Clave-segura-123")
        respuesta = self.client.post(reverse("login"), {"username": "ana", "password": "Clave-segura-123"})
        self.assertRedirects(respuesta, reverse("lista_posts"))
        self.assertIn("_auth_user_id", self.client.session)

        inicio = self.client.get(reverse("lista_posts"))
        self.assertContains(inicio, "Salir")
        self.assertNotContains(inicio, "Registrarse")

        respuesta = self.client.post(reverse("logout"))
        self.assertRedirects(respuesta, reverse("lista_posts"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_con_clave_incorrecta(self):
        User.objects.create_user("ana", "ana@example.com", "Clave-segura-123")
        respuesta = self.client.post(reverse("login"), {"username": "ana", "password": "mal"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_redirige_a_next(self):
        User.objects.create_user("ana", "ana@example.com", "Clave-segura-123")
        respuesta = self.client.post(
            reverse("login"),
            {"username": "ana", "password": "Clave-segura-123", "next": reverse("crear_post")},
        )
        self.assertRedirects(respuesta, reverse("crear_post"))

    def test_anonimo_ve_ingresar_y_registrarse(self):
        respuesta = self.client.get(reverse("lista_posts"))
        self.assertContains(respuesta, "Ingresar")
        self.assertContains(respuesta, "Registrarse")
        self.assertNotContains(respuesta, "Nuevo post")

    def test_perfil_publico_accesible(self):
        User.objects.create_user("ana", "ana@example.com", "Clave-segura-123")
        respuesta = self.client.get(reverse("perfil_autor", kwargs={"username": "ana"}))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "@ana")
        self.assertNotContains(respuesta, "Editar perfil")

    def test_mi_perfil_y_editar_perfil_requieren_login(self):
        for nombre in ["mi_perfil", "editar_perfil"]:
            url = reverse(nombre)
            self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}")
        url = reverse("editar_perfil")
        respuesta = self.client.post(url, {"email": "x@example.com", "bio": "hackeado"})
        self.assertRedirects(respuesta, f"{reverse('login')}?next={url}")

    def test_editar_perfil_con_avatar(self):
        usuario = User.objects.create_user("ana", "ana@example.com", "Clave-segura-123")
        self.client.login(username="ana", password="Clave-segura-123")
        respuesta = self.client.post(reverse("editar_perfil"), {
            "first_name": "Ana",
            "last_name": "Gómez",
            "email": "ana@example.com",
            "bio": "Analista de datos.",
            "sitio_web": "https://example.com",
            "avatar": avatar_de_prueba(),
        })
        self.assertRedirects(respuesta, reverse("mi_perfil"))
        usuario.refresh_from_db()
        self.assertEqual(usuario.first_name, "Ana")
        self.assertEqual(usuario.profile.bio, "Analista de datos.")
        self.assertTrue(Path(usuario.profile.avatar.path).exists())

        perfil = self.client.get(reverse("mi_perfil"))
        self.assertContains(perfil, usuario.profile.avatar.url)
        self.assertContains(perfil, "Editar perfil")
