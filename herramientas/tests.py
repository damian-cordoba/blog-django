from decimal import Decimal as D

from django.test import TestCase
from django.urls import reverse

from . import calculos
from .diagnostico import PREGUNTAS, evaluar
from .models import ResultadoDiagnostico


class CalculosTest(TestCase):
    def test_punto_equilibrio(self):
        r = calculos.punto_equilibrio(D("850000"), D("12000"), D("7500"))
        self.assertEqual(r.margen_unitario, D("4500"))
        self.assertEqual(r.unidades, 189)  # 850000 / 4500 = 188,9 → 189
        self.assertEqual(r.facturacion, D("2268000"))

    def test_punto_equilibrio_con_ganancia(self):
        r = calculos.punto_equilibrio(D("1000"), D("10"), D("5"), D("500"))
        self.assertEqual(r.unidades, 200)
        self.assertEqual(r.unidades_objetivo, 300)

    def test_punto_equilibrio_precio_menor_al_costo(self):
        with self.assertRaises(ValueError):
            calculos.punto_equilibrio(D("1000"), D("5"), D("5"))

    def test_precio_desde_margen(self):
        r = calculos.precio_desde_margen(D("1000"), D("30"), D("21"))
        self.assertAlmostEqual(float(r.precio), 1428.5714, places=3)
        self.assertAlmostEqual(float(r.margen), 0.30, places=6)
        self.assertAlmostEqual(float(r.markup), 0.428571, places=5)
        self.assertAlmostEqual(float(r.precio_con_iva), 1728.5714, places=3)

    def test_margen_desde_precio(self):
        r = calculos.margen_desde_precio(D("100"), D("130"))
        self.assertAlmostEqual(float(r.markup), 0.30, places=6)
        self.assertAlmostEqual(float(r.margen), 0.230769, places=5)
        self.assertIsNone(r.precio_con_iva)

    def test_descuento(self):
        r = calculos.impacto_descuento(D("30"), D("15"))
        self.assertEqual(r.aumento_ventas_necesario, D("1"))  # hay que vender el doble

    def test_descuento_mayor_al_margen(self):
        with self.assertRaises(ValueError):
            calculos.impacto_descuento(D("20"), D("25"))


class VistasCalculadorasTest(TestCase):
    def test_indice(self):
        respuesta = self.client.get(reverse("herramientas"))
        self.assertContains(respuesta, "Punto de equilibrio")
        self.assertContains(respuesta, "Diagnóstico de datos")

    def test_formularios_vacios_muestran_explicacion(self):
        for nombre in ["punto_equilibrio", "precio_margen", "descuento"]:
            respuesta = self.client.get(reverse(nombre))
            self.assertEqual(respuesta.status_code, 200)
            self.assertIsNone(respuesta.context["resultado"])

    def test_punto_equilibrio_muestra_resultado(self):
        respuesta = self.client.get(
            reverse("punto_equilibrio"), {"costos_fijos": "850000", "precio": "12000", "costo_variable": "7500"}
        )
        self.assertContains(respuesta, "189 unidades")
        self.assertContains(respuesta, "$ 2.268.000,00")

    def test_punto_equilibrio_valida_precio(self):
        respuesta = self.client.get(
            reverse("punto_equilibrio"), {"costos_fijos": "1000", "precio": "10", "costo_variable": "12"}
        )
        self.assertContains(respuesta, "El precio tiene que ser mayor")
        self.assertIsNone(respuesta.context["resultado"])

    def test_precio_margen_ambos_modos(self):
        r1 = self.client.get(reverse("precio_margen"), {"modo": "margen", "costo": "1000", "margen": "30"})
        self.assertContains(r1, "$ 1.428,57")
        r2 = self.client.get(reverse("precio_margen"), {"modo": "precio", "costo": "100", "precio": "130"})
        self.assertContains(r2, "23,1 %")

    def test_precio_margen_pide_el_dato_del_modo(self):
        respuesta = self.client.get(reverse("precio_margen"), {"modo": "precio", "costo": "100"})
        self.assertContains(respuesta, "Ingresá el precio de venta")

    def test_descuento_vista(self):
        respuesta = self.client.get(reverse("descuento"), {"margen": "30", "descuento": "15"})
        self.assertContains(respuesta, "100,0 % más")

    def test_valores_negativos_rechazados(self):
        respuesta = self.client.get(
            reverse("punto_equilibrio"), {"costos_fijos": "-5", "precio": "10", "costo_variable": "5"}
        )
        self.assertIsNone(respuesta.context["resultado"])

    def test_resultado_ofrece_contacto(self):
        respuesta = self.client.get(reverse("descuento"), {"margen": "30", "descuento": "15"})
        self.assertContains(respuesta, reverse("contacto") + "?origen=")


class DiagnosticoTest(TestCase):
    def respuestas(self, valor):
        return {clave: str(valor) for clave, *_ in PREGUNTAS}

    def test_evaluar_niveles(self):
        self.assertEqual(evaluar(self.respuestas(0))["nivel"], "Inicial")
        self.assertEqual(evaluar(self.respuestas(1))["nivel"], "Inicial")  # 10 puntos
        self.assertEqual(evaluar(self.respuestas(2))["nivel"], "En desarrollo")
        self.assertEqual(evaluar(self.respuestas(3))["nivel"], "Avanzado")

    def test_recomendaciones_solo_para_respuestas_bajas(self):
        self.assertEqual(len(evaluar(self.respuestas(0))["recomendaciones"]), 4)
        self.assertEqual(evaluar(self.respuestas(3))["recomendaciones"], [])

    def test_formulario_incompleto(self):
        respuesta = self.client.post(reverse("diagnostico"), {"registro_ventas": "1"})
        self.assertContains(respuesta, "Te faltó responder")
        self.assertEqual(ResultadoDiagnostico.objects.count(), 0)

    def test_resultado_se_muestra_y_se_guarda_anonimo(self):
        respuesta = self.client.post(reverse("diagnostico"), self.respuestas(2))
        self.assertContains(respuesta, "En desarrollo")
        self.assertContains(respuesta, "20 de 30 puntos")
        resultado = ResultadoDiagnostico.objects.get()
        self.assertEqual(resultado.puntaje, 20)

    def test_opcion_invalida(self):
        datos = self.respuestas(2)
        datos["kpis"] = "9"
        respuesta = self.client.post(reverse("diagnostico"), datos)
        self.assertIsNone(respuesta.context["resultado"])
