from urllib.parse import urlencode

from django.shortcuts import render
from django.urls import reverse

from . import calculos
from .diagnostico import evaluar
from .forms import DescuentoForm, DiagnosticoForm, PrecioMargenForm, PuntoEquilibrioForm
from .models import ResultadoDiagnostico

HERRAMIENTAS = [
    {
        "url": "punto_equilibrio",
        "icono": "⚖️",
        "titulo": "Punto de equilibrio",
        "descripcion": "Cuántas unidades tenés que vender por mes para cubrir tus costos fijos.",
    },
    {
        "url": "precio_margen",
        "icono": "🏷️",
        "titulo": "Precio y margen",
        "descripcion": "Calculá el precio según el margen que buscás, o tu margen real a partir del precio. Con margen vs. markup.",
    },
    {
        "url": "descuento",
        "icono": "📉",
        "titulo": "¿Conviene ese descuento?",
        "descripcion": "Cuánto más tenés que vender para ganar lo mismo después de una promoción.",
    },
    {
        "url": "diagnostico",
        "icono": "🩺",
        "titulo": "Diagnóstico de datos",
        "descripcion": "10 preguntas para saber qué tan bien usa los datos tu negocio, con recomendaciones.",
    },
]


def indice(request):
    return render(request, "herramientas/indice.html", {"herramientas": HERRAMIENTAS})


def _contacto(origen, mensaje):
    return reverse("contacto") + "?" + urlencode({"origen": origen, "mensaje": mensaje})


def punto_equilibrio(request):
    form = PuntoEquilibrioForm(request.GET or None)
    resultado = None
    if form.is_valid():
        d = form.cleaned_data
        resultado = calculos.punto_equilibrio(d["costos_fijos"], d["precio"], d["costo_variable"], d["ganancia_deseada"])
    return render(
        request,
        "herramientas/punto_equilibrio.html",
        {"titulo_pagina": "Punto de equilibrio", "subtitulo_pagina": "¿Cuánto tengo que vender para no perder plata?", "form": form, "resultado": resultado, "contacto_url": _contacto("calculadora: punto de equilibrio", "Usé la calculadora de punto de equilibrio y quiero analizar los números de mi negocio.")},
    )


def precio_margen(request):
    form = PrecioMargenForm(request.GET or None)
    resultado = None
    if form.is_valid():
        d = form.cleaned_data
        if d["modo"] == "margen":
            resultado = calculos.precio_desde_margen(d["costo"], d["margen"], d["iva"])
        else:
            resultado = calculos.margen_desde_precio(d["costo"], d["precio"], d["iva"])
    return render(
        request,
        "herramientas/precio_margen.html",
        {"titulo_pagina": "Precio y margen", "subtitulo_pagina": "El precio justo para el margen que buscás", "form": form, "resultado": resultado, "contacto_url": _contacto("calculadora: precio y margen", "Usé la calculadora de precio y margen y quiero ordenar los costos y precios de mis productos.")},
    )


def descuento(request):
    form = DescuentoForm(request.GET or None)
    resultado = None
    if form.is_valid():
        resultado = calculos.impacto_descuento(form.cleaned_data["margen"], form.cleaned_data["descuento"])
    return render(
        request,
        "herramientas/descuento.html",
        {"titulo_pagina": "¿Conviene ese descuento?", "subtitulo_pagina": "Cuánto más hay que vender para ganar lo mismo", "form": form, "resultado": resultado, "contacto_url": _contacto("calculadora: descuento", "Usé la calculadora de descuentos y quiero evaluar mis promociones con datos.")},
    )


def diagnostico(request):
    resultado = None
    if request.method == "POST":
        form = DiagnosticoForm(request.POST)
        if form.is_valid():
            resultado = evaluar(form.cleaned_data)
            ResultadoDiagnostico.objects.create(
                puntaje=resultado["puntaje"], nivel=resultado["nivel"], respuestas=form.cleaned_data
            )
    else:
        form = DiagnosticoForm()

    contacto_url = None
    if resultado:
        contacto_url = _contacto(
            "diagnóstico de datos",
            f"Hice el diagnóstico de datos: nivel {resultado['nivel']} ({resultado['puntaje']}/{resultado['maximo']} puntos). "
            "Quiero conversar sobre cómo mejorar.",
        )
    return render(
        request,
        "herramientas/diagnostico.html",
        {"form": form, "resultado": resultado, "contacto_url": contacto_url},
    )
