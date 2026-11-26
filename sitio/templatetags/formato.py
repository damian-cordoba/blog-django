"""Filtros de presentación propios del sitio."""

import re
from decimal import Decimal, InvalidOperation

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

_LISTA = re.compile(r"^[-•]\s+")
_NUMERADA = re.compile(r"^\d+[.)]\s+")


@register.filter
def texto_enriquecido(texto):
    """Convierte texto simple en HTML seguro.

    - Los bloques se separan con una línea en blanco.
    - Un bloque cuyas líneas empiezan con "- " se convierte en lista.
    - Un bloque cuyas líneas empiezan con "1. " se convierte en lista numerada.
    - Una línea que empieza con "## " se convierte en subtítulo.
    Todo el texto se escapa antes, así que no se puede inyectar HTML.
    """
    if not texto:
        return ""
    html = []
    for bloque in re.split(r"\n\s*\n", str(texto).strip()):
        lineas = [linea.strip() for linea in bloque.splitlines() if linea.strip()]
        if not lineas:
            continue
        if len(lineas) == 1 and lineas[0].startswith("## "):
            html.append(f"<h3>{escape(lineas[0][3:])}</h3>")
        elif all(_LISTA.match(linea) for linea in lineas):
            items = "".join(f"<li>{escape(_LISTA.sub('', linea))}</li>" for linea in lineas)
            html.append(f"<ul>{items}</ul>")
        elif all(_NUMERADA.match(linea) for linea in lineas):
            items = "".join(f"<li>{escape(_NUMERADA.sub('', linea))}</li>" for linea in lineas)
            html.append(f"<ol>{items}</ol>")
        else:
            html.append("<p>" + "<br>".join(escape(linea) for linea in lineas) + "</p>")
    return mark_safe("\n".join(html))


def _formatear(valor, decimales):
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        return valor
    texto = f"{numero:,.{decimales}f}"  # 1,234,567.89
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")  # 1.234.567,89


@register.filter
def numero_ar(valor, decimales=0):
    """1234567.5 → 1.234.568 (formato argentino)."""
    return _formatear(valor, int(decimales))


@register.filter
def moneda(valor):
    """1234.5 → $ 1.234,50"""
    texto = _formatear(valor, 2)
    return f"$ {texto}" if texto != valor else valor


@register.filter
def porcentaje(valor, decimales=1):
    """0.256 → 25,6 %"""
    try:
        return f"{_formatear(Decimal(str(valor)) * 100, int(decimales))} %"
    except (InvalidOperation, TypeError, ValueError):
        return valor
