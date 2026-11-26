"""Cálculos de las herramientas para PyMEs, separados de las vistas para poder probarlos."""

from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal

CIEN = Decimal("100")


@dataclass
class PuntoEquilibrio:
    margen_unitario: Decimal  # precio - costo variable
    margen_porcentaje: Decimal  # margen / precio (0 a 1)
    unidades: Decimal  # unidades a vender para cubrir los costos fijos (redondeado hacia arriba)
    facturacion: Decimal  # ventas en $ necesarias
    unidades_objetivo: Decimal | None = None  # unidades para lograr la ganancia deseada
    facturacion_objetivo: Decimal | None = None


def punto_equilibrio(costos_fijos, precio, costo_variable, ganancia_deseada=None):
    margen = precio - costo_variable
    if margen <= 0:
        raise ValueError("El precio tiene que ser mayor que el costo variable por unidad.")
    unidades = (costos_fijos / margen).to_integral_value(rounding=ROUND_CEILING)
    resultado = PuntoEquilibrio(
        margen_unitario=margen,
        margen_porcentaje=margen / precio,
        unidades=unidades,
        facturacion=unidades * precio,
    )
    if ganancia_deseada:
        u = ((costos_fijos + ganancia_deseada) / margen).to_integral_value(rounding=ROUND_CEILING)
        resultado.unidades_objetivo = u
        resultado.facturacion_objetivo = u * precio
    return resultado


@dataclass
class PrecioMargen:
    costo: Decimal
    precio: Decimal  # precio de venta sin IVA
    margen: Decimal  # ganancia / precio (0 a 1)
    markup: Decimal  # ganancia / costo (0 a ...)
    ganancia: Decimal
    precio_con_iva: Decimal | None = None


def precio_desde_margen(costo, margen_porcentaje, iva_porcentaje=None):
    """Precio necesario para obtener un margen sobre el precio de venta."""
    margen = margen_porcentaje / CIEN
    if not (0 <= margen < 1):
        raise ValueError("El margen tiene que estar entre 0 % y 99,9 %.")
    precio = costo / (1 - margen)
    return _armar(costo, precio, iva_porcentaje)


def margen_desde_precio(costo, precio, iva_porcentaje=None):
    if precio <= 0:
        raise ValueError("El precio tiene que ser mayor que cero.")
    return _armar(costo, precio, iva_porcentaje)


def _armar(costo, precio, iva_porcentaje):
    ganancia = precio - costo
    resultado = PrecioMargen(
        costo=costo,
        precio=precio,
        margen=ganancia / precio,
        markup=(ganancia / costo) if costo else Decimal("0"),
        ganancia=ganancia,
    )
    if iva_porcentaje:
        resultado.precio_con_iva = precio * (1 + iva_porcentaje / CIEN)
    return resultado


@dataclass
class Descuento:
    margen_actual: Decimal  # 0 a 1
    margen_con_descuento: Decimal  # 0 a 1
    aumento_ventas_necesario: Decimal  # 0 a ... (0,5 = vender 50 % más unidades)


def impacto_descuento(margen_porcentaje, descuento_porcentaje):
    """Cuánto más hay que vender para ganar lo mismo después de un descuento.

    Con margen m y descuento d (ambos sobre el precio), la ganancia por unidad pasa de m
    a (m - d) en proporción al precio original, entonces el volumen tiene que crecer
    d / (m - d) para mantener la misma ganancia total.
    """
    m = margen_porcentaje / CIEN
    d = descuento_porcentaje / CIEN
    if d >= m:
        raise ValueError(
            "Con ese descuento vendés al costo o a pérdida: no hay volumen que compense la ganancia."
        )
    return Descuento(margen_actual=m, margen_con_descuento=(m - d) / (1 - d), aumento_ventas_necesario=d / (m - d))
