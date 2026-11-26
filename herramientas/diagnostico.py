"""Preguntas y puntaje del diagnóstico de datos para PyMEs."""

# Cada pregunta: (clave, área, texto, opciones de menor a mayor madurez, recomendación si sale baja)
PREGUNTAS = [
    (
        "registro_ventas",
        "Registro",
        "¿Cómo registran las ventas del día a día?",
        ["No se registran o se anotan en papel", "En planillas sueltas", "En una planilla única y ordenada", "En un sistema o software de gestión"],
        "Centralizá las ventas en un único registro estructurado: es la base de cualquier análisis.",
    ),
    (
        "stock",
        "Registro",
        "¿Saben cuánto stock tienen de cada producto?",
        ["No, lo vemos en el depósito", "Más o menos, lo contamos cada tanto", "Sí, aunque con diferencias frecuentes", "Sí, actualizado y confiable"],
        "Un control de stock simple evita quiebres y mercadería inmovilizada.",
    ),
    (
        "clientes",
        "Registro",
        "¿Tienen una base de clientes con su historial de compras?",
        ["No", "Solo contactos en el celular", "Una lista sin historial", "Sí, con lo que compró cada uno"],
        "Con el historial por cliente podés detectar quién deja de comprar y fidelizar a los mejores.",
    ),
    (
        "unica_fuente",
        "Calidad",
        "Si dos personas buscan el total vendido del mes, ¿llegan al mismo número?",
        ["Casi nunca", "A veces", "Casi siempre", "Siempre: hay una sola fuente de datos"],
        "Definí una única fuente de verdad para que todos trabajen con los mismos números.",
    ),
    (
        "tiempo_reportes",
        "Calidad",
        "¿Cuánto tiempo les lleva armar un informe de ventas o resultados?",
        ["No armamos informes", "Varios días", "Algunas horas", "Minutos, se actualiza solo"],
        "Automatizar la consolidación de datos libera horas cada mes para analizar en lugar de copiar y pegar.",
    ),
    (
        "kpis",
        "Análisis",
        "¿Tienen definidos indicadores clave (KPIs) con una meta?",
        ["No", "Miramos algunos números sin metas", "Algunos KPIs con meta", "Sí, con meta y responsable"],
        "Elegí 3 KPIs con meta y frecuencia de revisión: ventas, margen y clientes recurrentes.",
    ),
    (
        "rentabilidad",
        "Análisis",
        "¿Conocen el margen de ganancia de cada producto o servicio?",
        ["No", "De algunos, de memoria", "De la mayoría, calculado", "De todos, actualizado con los costos"],
        "Calcular el margen por producto muestra qué conviene impulsar y qué revisar. Probá la calculadora de precio y margen.",
    ),
    (
        "frecuencia",
        "Análisis",
        "¿Cada cuánto revisan los números del negocio?",
        ["Cuando hay un problema", "Una vez al año, con el contador", "Una vez por mes", "Todas las semanas"],
        "Una revisión mensual corta, siempre con los mismos indicadores, permite corregir a tiempo.",
    ),
    (
        "decisiones",
        "Decisiones",
        "Cuando toman una decisión importante (precios, compras, personal), ¿en qué se basan?",
        ["En la intuición", "En la experiencia, con algunos números", "En datos, cuando están a mano", "Siempre en datos actualizados"],
        "Antes de decidir, armá una vista mínima con los datos que afectan esa decisión.",
    ),
    (
        "visualizacion",
        "Decisiones",
        "¿Tienen un tablero o resumen visual del negocio?",
        ["No", "Gráficos sueltos en Excel", "Un tablero que se actualiza a mano", "Un tablero que se actualiza automáticamente"],
        "Un tablero simple en Excel o Power BI resume el negocio en una sola pantalla.",
    ),
]

NIVELES = [
    (
        10,
        "Inicial",
        "La información está dispersa o depende de la memoria. El primer paso es ordenar el registro de ventas, stock y clientes en un solo lugar.",
    ),
    (
        20,
        "En desarrollo",
        "Ya hay datos, pero cuesta consolidarlos y confiar en ellos. Con un poco de estructura y automatización se pueden convertir en indicadores para decidir.",
    ),
    (
        30,
        "Avanzado",
        "El negocio usa datos para decidir. El siguiente paso es automatizar reportes y medir con más detalle para encontrar oportunidades.",
    ),
]

PUNTAJE_MAXIMO = 3 * len(PREGUNTAS)


def evaluar(respuestas):
    """respuestas: dict clave -> índice de opción (0 a 3). Devuelve el resultado completo."""
    puntaje = sum(int(respuestas[clave]) for clave, *_ in PREGUNTAS)
    nivel, descripcion = next((n, d) for limite, n, d in NIVELES if puntaje <= limite)

    por_area = {}
    for clave, area, *_ in PREGUNTAS:
        total, cantidad = por_area.get(area, (0, 0))
        por_area[area] = (total + int(respuestas[clave]), cantidad + 1)
    areas = [
        {"nombre": area, "porcentaje": round(100 * total / (3 * cantidad))}
        for area, (total, cantidad) in por_area.items()
    ]

    # Recomendaciones para las respuestas más bajas (hasta 4).
    bajas = sorted(
        ((int(respuestas[clave]), recomendacion) for clave, _, _, _, recomendacion in PREGUNTAS if int(respuestas[clave]) <= 1),
        key=lambda x: x[0],
    )
    recomendaciones = [rec for _, rec in bajas[:4]]

    return {
        "puntaje": puntaje,
        "maximo": PUNTAJE_MAXIMO,
        "porcentaje": round(100 * puntaje / PUNTAJE_MAXIMO),
        "nivel": nivel,
        "descripcion": descripcion,
        "areas": areas,
        "recomendaciones": recomendaciones,
    }
