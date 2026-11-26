from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Consulta, PerfilProfesional, Servicio
from .templatetags.formato import moneda, numero_ar, porcentaje, texto_enriquecido


class FormatoTest(TestCase):
    def test_numeros_en_formato_argentino(self):
        self.assertEqual(numero_ar(1234567), "1.234.567")
        self.assertEqual(moneda(1234.5), "$ 1.234,50")
        self.assertEqual(porcentaje(0.256), "25,6 %")

    def test_texto_enriquecido_listas_y_escape(self):
        html = texto_enriquecido("Intro\n\n- uno\n- dos\n\n1. a\n2. b\n\n<script>x</script>")
        self.assertIn("<ul><li>uno</li><li>dos</li></ul>", html)
        self.assertIn("<ol><li>a</li><li>b</li></ol>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)


class PaginasTest(TestCase):
    def setUp(self):
        perfil = PerfilProfesional.cargar()
        perfil.bio = "Soy analista de datos.\n\n- Excel\n- Power BI"
        perfil.habilidades = "SQL\nPython"
        perfil.email = "dami@example.com"
        perfil.save()
        self.servicio = Servicio.objects.create(nombre="Tablero en Power BI", resumen="Resumen", destacado=True)
        Servicio.objects.create(nombre="Servicio inactivo", resumen="x", activo=False)

    def test_perfil_es_unico(self):
        otro = PerfilProfesional(nombre="Otro")
        otro.save()
        self.assertEqual(PerfilProfesional.objects.count(), 1)

    def test_portada(self):
        respuesta = self.client.get(reverse("inicio"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Tablero en Power BI")
        self.assertContains(respuesta, reverse("diagnostico"))

    def test_sobre_mi(self):
        respuesta = self.client.get(reverse("sobre_mi"))
        self.assertContains(respuesta, "Soy analista de datos.")
        self.assertContains(respuesta, "<li>Excel</li>", html=True)
        self.assertContains(respuesta, "Python")

    def test_servicios_muestra_solo_activos(self):
        respuesta = self.client.get(reverse("servicios"))
        self.assertContains(respuesta, "Tablero en Power BI")
        self.assertNotContains(respuesta, "Servicio inactivo")

    def test_whatsapp_solo_si_hay_numero(self):
        self.assertNotContains(self.client.get(reverse("inicio")), "wa.me")
        perfil = PerfilProfesional.cargar()
        perfil.whatsapp = "+54 9 387 123-4567"
        perfil.save()
        self.assertContains(self.client.get(reverse("inicio")), "https://wa.me/5493871234567")

    def test_blog_sigue_funcionando_en_su_nueva_ruta(self):
        self.assertEqual(reverse("lista_posts"), "/blog/")
        self.assertEqual(self.client.get("/blog/").status_code, 200)


class ContactoTest(TestCase):
    def setUp(self):
        perfil = PerfilProfesional.cargar()
        perfil.email = "dami@example.com"
        perfil.save()
        self.servicio = Servicio.objects.create(nombre="Limpieza de datos", resumen="x")

    def datos(self, **extra):
        return {
            "nombre": "Ana",
            "email": "ana@pyme.com",
            "empresa": "Ferretería Ana",
            "servicio": self.servicio.pk,
            "mensaje": "Necesito ordenar mis ventas.",
            **extra,
        }

    def test_formulario_prellenado_desde_servicio_y_mensaje(self):
        respuesta = self.client.get(reverse("contacto"), {"servicio": self.servicio.slug, "mensaje": "Hola", "origen": "diagnóstico"})
        self.assertEqual(respuesta.context["form"].initial["servicio"], self.servicio)
        self.assertContains(respuesta, "Hola")
        self.assertContains(respuesta, 'value="diagnóstico"')

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_consulta_se_guarda_y_avisa_por_email(self):
        respuesta = self.client.post(reverse("contacto"), self.datos(origen="diagnóstico de datos"), follow=True)
        self.assertContains(respuesta, "Recibí tu consulta")
        consulta = Consulta.objects.get()
        self.assertEqual(consulta.servicio, self.servicio)
        self.assertEqual(consulta.origen, "diagnóstico de datos")
        self.assertEqual(consulta.estado, "nueva")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Ana", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ["dami@example.com"])

    def test_campos_obligatorios(self):
        respuesta = self.client.post(reverse("contacto"), {"nombre": "", "email": "no-es-email", "mensaje": ""})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Consulta.objects.count(), 0)

    def test_bot_con_campo_trampa_no_se_guarda(self):
        respuesta = self.client.post(reverse("contacto"), self.datos(sitio_web="http://spam.com"), follow=True)
        self.assertContains(respuesta, "Recibí tu consulta")
        self.assertEqual(Consulta.objects.count(), 0)

    @override_settings(EMAIL_BACKEND="no.existe.Backend")
    def test_falla_del_correo_no_rompe_el_formulario(self):
        with self.assertLogs("sitio.views", level="ERROR"):
            respuesta = self.client.post(reverse("contacto"), self.datos(), follow=True)
        self.assertContains(respuesta, "Recibí tu consulta")
        self.assertEqual(Consulta.objects.count(), 1)

    def test_consultas_visibles_solo_en_admin(self):
        self.client.post(reverse("contacto"), self.datos())
        url = reverse("admin:sitio_consulta_changelist")
        self.assertEqual(self.client.get(url).status_code, 302)  # anónimo → login del admin
