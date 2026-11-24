"""
Carga publicaciones de ejemplo para probar el blog desde una base vacía.

Uso:
    python manage.py cargar_datos_demo

Crea un autor de ejemplo ("equipo_dcb", sin contraseña utilizable) y seis
publicaciones. Cuatro tienen una imagen de portada generada con Pillow y dos
no tienen imagen, para mostrar que los templates funcionan en ambos casos.
El comando se puede ejecutar varias veces: no duplica contenido.
"""

import io
import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from PIL import Image, ImageDraw

from posts.models import Categoria, Post
from usuarios.models import Profile

AUTOR_DEMO = "equipo_dcb"

POSTS = [
    {
        "titulo": "Qué es un KPI y por qué tu negocio necesita tres, no treinta",
        "subtitulo": "Medir todo es lo mismo que no medir nada",
        "categoria": "gestion-y-kpis",
        "imagen": True,
        "contenido": (
            "Un KPI (indicador clave de desempeño) es un número que te dice si el negocio va "
            "hacia donde querés. La palabra importante es «clave»: no es cualquier dato, es el "
            "que te ayuda a decidir.\n\n"
            "Un error muy común en las PyMEs es armar una planilla con treinta indicadores. "
            "Nadie la mira, y si alguien la mira no sabe por dónde empezar.\n\n"
            "Para empezar, elegí tres:\n"
            "1. Uno de ventas: por ejemplo, ticket promedio o ventas por semana.\n"
            "2. Uno de rentabilidad: margen bruto por producto o por rubro.\n"
            "3. Uno de clientes: cuántos vuelven a comprar en los próximos 60 días.\n\n"
            "Cada KPI necesita tres cosas: una definición clara (cómo se calcula), una meta "
            "(cuánto querés que dé) y una frecuencia (cada cuánto lo mirás). Sin esas tres "
            "cosas es solo un número lindo.\n\n"
            "Consejo criollo: si un indicador no te hizo cambiar ninguna decisión en los "
            "últimos tres meses, probablemente no es clave."
        ),
    },
    {
        "titulo": "Excel vs Power BI: cuándo conviene cada uno",
        "subtitulo": "No son rivales, son herramientas para momentos distintos",
        "categoria": "power-bi",
        "imagen": True,
        "contenido": (
            "La pregunta aparece siempre: ¿paso todo a Power BI o sigo con Excel? La respuesta "
            "corta es «depende de para qué».\n\n"
            "Excel conviene cuando:\n"
            "- Necesitás cargar o corregir datos a mano.\n"
            "- Hacés cálculos puntuales o simulaciones («¿qué pasa si subo el precio un 10 %?»).\n"
            "- Trabaja una sola persona y el volumen de datos es chico.\n\n"
            "Power BI conviene cuando:\n"
            "- Los datos vienen de varias fuentes (sistema de ventas, planillas, banco).\n"
            "- Varias personas tienen que ver el mismo tablero actualizado.\n"
            "- Querés filtrar y explorar sin romper fórmulas.\n\n"
            "En la práctica, muchas PyMEs usan las dos: Excel (con Power Query) para preparar "
            "y ordenar los datos, y Power BI para mostrarlos. Lo importante es que los datos "
            "estén limpios: un tablero hermoso con datos sucios sigue mintiendo."
        ),
    },
    {
        "titulo": "Tablas dinámicas: el superpoder escondido de Excel",
        "subtitulo": "Resumí miles de filas en segundos, sin una sola fórmula",
        "categoria": "excel",
        "imagen": False,
        "contenido": (
            "Si tenés una planilla con las ventas del año, fila por fila, una tabla dinámica te "
            "permite responder preguntas como «¿cuánto vendí por mes y por vendedor?» en un "
            "par de clics.\n\n"
            "Paso a paso:\n"
            "1. Asegurate de que tus datos tengan encabezados y no tengan filas vacías en el medio.\n"
            "2. Convertilos en tabla con Ctrl + T. Así, cuando agregues filas, la tabla dinámica las toma.\n"
            "3. Insertar → Tabla dinámica.\n"
            "4. Arrastrá «Fecha» a filas, «Vendedor» a columnas e «Importe» a valores.\n\n"
            "Listo: tenés un resumen que podés reorganizar arrastrando campos. Si los datos "
            "cambian, clic derecho → Actualizar.\n\n"
            "Este post no tiene imagen a propósito: sirve para comprobar que el blog se ve bien "
            "también cuando una publicación no tiene portada."
        ),
    },
    {
        "titulo": "Promedio vs mediana: no te dejes engañar por un número",
        "subtitulo": "Un solo cliente grande puede cambiarte toda la foto",
        "categoria": "estadistica",
        "imagen": True,
        "contenido": (
            "Imaginá un comercio con diez clientes. Nueve compran $10.000 por mes y uno compra "
            "$500.000. El promedio da $59.000. ¿Es representativo? Para nada.\n\n"
            "La mediana es el valor del medio cuando ordenás los datos. En este ejemplo es "
            "$10.000, que describe mucho mejor al cliente típico.\n\n"
            "¿Cuándo usar cada una?\n"
            "- Promedio: cuando los datos son parejos y no hay valores extremos.\n"
            "- Mediana: cuando hay casos muy grandes o muy chicos (ventas, sueldos, tiempos de entrega).\n\n"
            "En Excel: =PROMEDIO(rango) y =MEDIANA(rango). En pandas: df['ventas'].mean() y "
            "df['ventas'].median().\n\n"
            "Regla práctica: calculá los dos. Si dan muy distinto, hay valores extremos y "
            "conviene mirarlos de cerca antes de decidir."
        ),
    },
    {
        "titulo": "SQL para no programadores: tu primera consulta",
        "subtitulo": "SELECT, FROM y WHERE alcanzan para empezar",
        "categoria": "sql",
        "imagen": False,
        "contenido": (
            "Casi todos los sistemas de gestión guardan la información en una base de datos. "
            "SQL es el idioma para preguntarle cosas.\n\n"
            "La estructura básica tiene tres partes:\n\n"
            "SELECT cliente, total\n"
            "FROM ventas\n"
            "WHERE fecha >= '2026-01-01';\n\n"
            "- SELECT: qué columnas querés ver.\n"
            "- FROM: de qué tabla.\n"
            "- WHERE: con qué condición filtrás.\n\n"
            "Con agregar GROUP BY ya podés resumir: «total vendido por cliente» es "
            "SELECT cliente, SUM(total) FROM ventas GROUP BY cliente;\n\n"
            "No hace falta saber programar para escribir estas consultas, y te ahorran horas "
            "de exportar y copiar planillas."
        ),
    },
    {
        "titulo": "Tu primera limpieza de datos con pandas",
        "subtitulo": "Duplicados, espacios de más y fechas mal cargadas",
        "categoria": "python",
        "imagen": True,
        "contenido": (
            "Antes de analizar, hay que limpiar. Una base de clientes típica tiene nombres "
            "repetidos, mayúsculas mezcladas y fechas en formatos distintos.\n\n"
            "Con pandas, cinco líneas resuelven mucho:\n\n"
            "import pandas as pd\n"
            "df = pd.read_excel('clientes.xlsx')\n"
            "df['nombre'] = df['nombre'].str.strip().str.title()\n"
            "df['fecha_alta'] = pd.to_datetime(df['fecha_alta'], dayfirst=True, errors='coerce')\n"
            "df = df.drop_duplicates(subset=['cuit'])\n\n"
            "Qué hace cada paso:\n"
            "- strip() saca los espacios de más y title() unifica las mayúsculas.\n"
            "- to_datetime convierte las fechas; las que no se pueden leer quedan vacías para revisarlas.\n"
            "- drop_duplicates elimina clientes repetidos usando el CUIT como referencia.\n\n"
            "Guardá siempre una copia del archivo original antes de limpiar."
        ),
    },
]

COLORES = {
    "gestion-y-kpis": ((10, 37, 64), (240, 180, 41)),
    "power-bi": ((40, 35, 20), (242, 200, 17)),
    "excel": ((16, 80, 50), (120, 220, 150)),
    "estadistica": ((60, 30, 90), (255, 160, 200)),
    "sql": ((20, 50, 90), (130, 190, 255)),
    "python": ((30, 60, 100), (255, 212, 59)),
}


def generar_portada(slug_categoria, semilla):
    """Dibuja una portada simple tipo gráfico (sin texto) y la devuelve en bytes JPG."""
    fondo, acento = COLORES.get(slug_categoria, ((10, 37, 64), (240, 180, 41)))
    ancho, alto = 1200, 630
    img = Image.new("RGB", (ancho, alto), fondo)
    dibujo = ImageDraw.Draw(img)
    aleatorio = random.Random(semilla)

    for x in range(0, ancho, 60):
        dibujo.line([(x, 0), (x, alto)], fill=tuple(min(c + 18, 255) for c in fondo))
    for i, x in enumerate(range(90, ancho - 60, 110)):
        h = aleatorio.randint(120, 420)
        dibujo.rectangle([x, alto - h, x + 60, alto], fill=tuple(min(c + 45, 255) for c in fondo))
    puntos, y = [], alto * 0.6
    for x in range(0, ancho + 50, 75):
        y = max(80, min(alto - 80, y + aleatorio.uniform(-70, 55)))
        puntos.append((x, y))
    dibujo.line(puntos, fill=acento, width=8)
    for px, py in puntos[1::2]:
        dibujo.ellipse([px - 10, py - 10, px + 10, py + 10], fill=acento)

    salida = io.BytesIO()
    img.save(salida, format="JPEG", quality=82)
    return salida.getvalue()


class Command(BaseCommand):
    help = "Carga un autor y publicaciones de ejemplo (no duplica si ya existen)."

    def handle(self, *args, **options):
        autor, creado = User.objects.get_or_create(
            username=AUTOR_DEMO,
            defaults={"first_name": "Equipo", "last_name": "Datos en Criollo", "email": "demo@example.com"},
        )
        if creado:
            autor.set_unusable_password()  # cuenta solo para mostrar contenido
            autor.save()
        perfil, _ = Profile.objects.get_or_create(user=autor)
        if not perfil.bio:
            perfil.bio = "Cuenta de ejemplo con artículos introductorios sobre datos para PyMEs."
            perfil.save()

        ahora = timezone.now()
        nuevos = 0
        for indice, datos in enumerate(POSTS):
            if Post.objects.filter(titulo=datos["titulo"]).exists():
                continue
            categoria = Categoria.objects.filter(slug=datos["categoria"]).first()
            post = Post(
                titulo=datos["titulo"],
                subtitulo=datos["subtitulo"],
                contenido=datos["contenido"],
                categoria=categoria,
                autor=autor,
            )
            if datos["imagen"]:
                contenido = generar_portada(datos["categoria"], indice)
                post.imagen.save(f"demo-{datos['categoria']}.jpg", ContentFile(contenido), save=False)
            post.save()
            # Escalonamos las fechas para que el listado se vea como un blog real.
            Post.objects.filter(pk=post.pk).update(
                creado=ahora - timedelta(days=(len(POSTS) - indice) * 3),
                actualizado=ahora - timedelta(days=(len(POSTS) - indice) * 3),
            )
            nuevos += 1

        self.stdout.write(self.style.SUCCESS(f"Datos de ejemplo listos: {nuevos} publicaciones nuevas."))
