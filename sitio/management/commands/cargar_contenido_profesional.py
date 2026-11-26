"""
Carga el contenido profesional inicial: perfil, servicios y casos de estudio.

Uso:
    python manage.py cargar_contenido_profesional
    python manage.py cargar_contenido_profesional --actualizar   # pisa los textos con los de este archivo

Sin --actualizar, no modifica lo que ya existe (respeta lo que se haya editado en el admin).
Las imágenes (foto de perfil y capturas de los casos) se suben desde el panel /admin/.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from portafolio.models import Herramienta, Proyecto
from sitio.models import PerfilProfesional, Servicio

PERFIL = {
    "nombre": "Damián Emiliano Cordoba",
    "titular": "Analista de datos · BI y automatización para PyMEs",
    "bio_corta": (
        "Desde 2023 desarrollo soluciones de Business Intelligence y automatización para PyMEs como consultor "
        "independiente: sistemas en Excel, tableros en Power BI, SQL y Python."
    ),
    "bio": """Hola, soy Damián. Soy analista de datos y desde 2023 desarrollo soluciones de Business Intelligence y automatización para PyMEs como consultor independiente. Trabajo con Excel avanzado (VBA, Power Query, Power Pivot), Power BI, SQL y Python, y en el último año sumé automatizaciones con IA (n8n y APIs de modelos de lenguaje).

Empecé armando sistemas en Excel para negocios que llevaban la información «de memoria» o en planillas sueltas. El primero fue para un lubricentro en Tierra del Fuego: ventas con cálculo automático de netos, cuentas corrientes, stock, compras y pagos a proveedores, cheques, gastos y un dashboard con indicadores. Sigue en uso, con mantenimiento mensual, y por recomendación de ese cliente desarrollé otro para una rotisería de la misma ciudad.

Con el tiempo los proyectos crecieron. Para un estudio contable desarrollé en Python un sistema de pre-liquidación de IVA que descarga automáticamente los comprobantes de ARCA, aplica el criterio del contador, concilia contra las declaraciones juradas presentadas y muestra todo en un tablero de control. Para un salón de estética, migré su sistema en Excel a una app web con base de datos en la nube (JavaScript + Supabase), con agenda de turnos, fichas de clientes y dashboard.

Mi foco es convertir información dispersa en indicadores claros para decidir. Empiezo relevando cómo trabaja cada cliente, después modelo los datos, construyo la herramienta y acompaño con manuales de usuario y soporte.""",
    "ubicacion": "Salta, Argentina",
    "idiomas": "Español nativo · Inglés intermedio-avanzado",
    "disponibilidad": "Disponible para trabajo remoto",
    "habilidades": "\n".join(
        [
            "Excel avanzado: VBA, Power Query, Power Pivot",
            "Power BI y DAX",
            "SQL (PostgreSQL)",
            "Python: ETL, automatización y Django",
            "Automatización con IA: n8n y APIs de modelos de lenguaje",
            "Git / GitHub",
            "Dashboards e informes interactivos",
            "Consultoría en análisis de datos y productividad",
        ]
    ),
    "formacion": "\n".join(
        [
            "Diplomatura en Ciencia de Datos — Coderhouse (en curso)",
            "Certificaciones en SQL, AI Automation y Python — Coderhouse",
        ]
    ),
    "email": "dami.cordoba00@gmail.com",
    "linkedin": "https://www.linkedin.com/in/damian-emiliano-cordoba/",
    "github": "https://github.com/damian-cordoba",
}

SERVICIOS = [
    {
        "nombre": "Sistemas de gestión en Excel",
        "icono": "🧮",
        "resumen": "Un sistema a medida para registrar ventas, stock, clientes y cuentas corrientes, con indicadores automáticos.",
        "descripcion": "Para negocios que hoy llevan la información en planillas sueltas o de memoria. Diseño un sistema en Excel con formularios de carga, validaciones y tableros, pensado para que lo use cualquier persona del equipo.",
        "incluye": "Relevamiento del proceso\nFormularios de carga con validaciones (VBA)\nTablero de indicadores\nManual de usuario y soporte",
        "herramientas": "Excel, VBA, Power Query, Power Pivot",
        "modalidad": "proyecto",
        "destacado": True,
    },
    {
        "nombre": "Construcción de tablero (dashboard) en Power BI",
        "icono": "📊",
        "resumen": "Un tablero interactivo que reúne tus datos de distintas fuentes y muestra los KPIs que importan.",
        "descripcion": "Conecto tus fuentes (Excel, CSV, sistemas de gestión), modelo los datos en esquema estrella y construyo medidas DAX e indicadores comparativos para que veas la evolución del negocio de un vistazo.",
        "incluye": "Limpieza y modelado de datos\nMedidas DAX y comparativas interanuales\nDiseño orientado a la toma de decisiones\nDocumentación",
        "herramientas": "Power BI, Power Query, DAX",
        "modalidad": "ambas",
        "destacado": True,
    },
    {
        "nombre": "Construcción de tablero (dashboard) en Excel",
        "icono": "📈",
        "resumen": "Indicadores claros dentro de la herramienta que ya usás, sin licencias adicionales.",
        "descripcion": "Para equipos que trabajan en Excel y necesitan ver sus números ordenados: ventas, márgenes, stock o cobranzas, con tablas dinámicas, segmentadores y gráficos que se actualizan con un clic.",
        "herramientas": "Excel, Power Pivot, tablas dinámicas",
        "modalidad": "ambas",
    },
    {
        "nombre": "Reporte automatizado + ETL",
        "icono": "⚙️",
        "resumen": "Dejá de copiar y pegar: los reportes se arman solos a partir de tus archivos o sistemas.",
        "descripcion": "Automatizo la descarga, consolidación y limpieza de datos para que los informes periódicos se generen en minutos y sin errores manuales.",
        "herramientas": "Python, Power Query, SQL",
        "modalidad": "hora",
        "destacado": True,
    },
    {
        "nombre": "Limpieza de datos",
        "icono": "🧹",
        "resumen": "Bases de clientes, productos o ventas sin duplicados, con formatos unificados y listas para analizar.",
        "herramientas": "Excel, Power Query, Python, SQL",
        "modalidad": "hora",
    },
    {
        "nombre": "Consultoría en análisis de datos",
        "icono": "🧭",
        "resumen": "Te ayudo a definir qué medir, qué indicadores usar y cómo organizar la información para decidir mejor.",
        "modalidad": "hora",
        "destacado": True,
    },
    {
        "nombre": "Mentoría en Excel y análisis de datos",
        "icono": "🎓",
        "resumen": "Sesiones personalizadas para vos o tu equipo, desde fórmulas clave hasta Power Query y tableros.",
        "herramientas": "Excel, Power Query, Power BI",
        "modalidad": "hora",
    },
]

PROYECTOS = [
    {
        "titulo": "Sistema de gestión comercial para lubricentro",
        "tipo": "cliente",
        "sector": "Lubricentro",
        "periodo": "Diciembre 2025",
        "resumen": "Sistema en Excel y VBA que centraliza ventas, cuentas corrientes e indicadores de un lubricentro. Sigue en uso, con mantenimiento mensual.",
        "problema": "La operación diaria del negocio se registraba de forma manual y dispersa. Era difícil saber cuánto se vendía por período, cuánto debía cada cliente y cuál era el estado financiero real del negocio.",
        "solucion": "Desarrollé un sistema integral de gestión comercial en Excel automatizado con VBA, diseñado para el lubricentro:\n\n- Registro de ventas diarias con cálculo automático de netos.\n- Cuentas corrientes por cliente, con fechas y estados de pago automáticos.\n- Stock, compras y pagos a proveedores, cheques y gastos.\n- Dashboard dinámico con ventas totales, ingresos por período y deuda por cliente.",
        "resultados": "- Toda la operación centralizada en una única herramienta.\n- Menos errores en los registros manuales y mejor control de cuentas corrientes.\n- Ahorro de tiempo en tareas administrativas.\n- El sistema sigue en uso con mantenimiento mensual y, por recomendación del cliente, desarrollé otro para una rotisería de la misma ciudad.",
        "detalle_tecnico": "- Datos estructurados en tablas (ListObjects) con campos normalizados.\n- Validación de clientes y tipos de pago.\n- Automatización de registros con VBA y control de integridad para evitar duplicados.\n- Actualización automática de tablas dinámicas.",
        "nota": "Los datos y la identidad visual de las capturas fueron adaptados para preservar la confidencialidad del cliente.",
        "herramientas": ["Excel", "VBA", "Power Query", "DAX"],
        "destacado": True,
        "orden": 1,
    },
    {
        "titulo": "Sistema de pre-liquidación de IVA para estudio contable",
        "tipo": "cliente",
        "sector": "Estudio contable",
        "periodo": "Octubre 2026",
        "resumen": "Sistema en Python que descarga los comprobantes de ARCA, aplica el criterio del contador y genera un borrador de IVA conciliado contra las DDJJ.",
        "problema": "El equipo contable dedicaba muchas horas a descargar y clasificar comprobantes de cada cliente. La pregunta de cada mes era: ¿cuál es la posición de IVA de cada cliente y coincide con lo que se presentó?",
        "solucion": "Desarrollé un sistema en Python, con más de 20 módulos y más de 15.000 líneas de código:\n\n- Descarga automática (Playwright) de Mis Comprobantes emitidos y recibidos, Mis Retenciones, liquidaciones de granos, F. 931 y DDJJ presentadas.\n- Motor de pre-liquidación con maestro de proveedores y clasificación auditable según el criterio del contador.\n- Liquidación hasta el saldo final y conciliación contra las DDJJ presentadas.\n- Salidas: CSV para importar en IVA Simple y papeles de trabajo en Excel con fórmulas visibles.\n- App web local multi-PC sobre carpeta compartida, con respaldos automáticos.",
        "resultados": "- El equipo contable dedica su tiempo a revisar y validar en lugar de transcribir.\n- En validación con una muestra de 14 contribuyentes, con conciliación semanal junto al equipo contable.\n- El resultado es un borrador que revisa y presenta el contador.",
        "nota": "Por confidencialidad no se publican datos de clientes ni el código fuente.",
        "herramientas": ["Python", "Excel"],
        "destacado": True,
        "orden": 2,
    },
    {
        "titulo": "Sistema de gestión integral para salón de estética",
        "tipo": "cliente",
        "sector": "Salón de estética",
        "periodo": "Marzo 2026",
        "resumen": "Agenda de turnos, fichas de clientes e historial de servicios en un único sistema, con control automático de sobreturnos.",
        "problema": "La agenda, los datos de clientes y los servicios realizados estaban desorganizados. Eso generaba errores de turnos y no permitía conocer el historial de cada cliente durante la atención.",
        "solucion": "Desarrollé un sistema modular en Excel con VBA y formularios interactivos:\n\n- Gestión de clientes con identificación única.\n- Agenda de turnos por fecha, horario y estilista, con control automático de sobreturnos.\n- Historial de servicios por visita, con observaciones técnicas.\n- Ficha de cliente interactiva con frecuencia de visitas y preferencias.\n\nMás adelante, el sistema se migró a una app web con base de datos en la nube (JavaScript + Supabase).",
        "resultados": "- Información del negocio centralizada.\n- Menos errores operativos y mejor organización de la agenda.\n- Acceso inmediato al historial de cada cliente para una atención más personalizada.",
        "nota": "Los datos de las capturas fueron adaptados para preservar la confidencialidad del cliente.",
        "herramientas": ["Excel", "VBA", "Power Query", "Power Pivot"],
        "destacado": True,
        "orden": 3,
    },
    {
        "titulo": "DataPyme: automatización con IA para consultas comerciales",
        "tipo": "formacion",
        "sector": "Automatización con IA",
        "periodo": "Octubre 2026",
        "resumen": "Flujo en n8n donde la IA clasifica cada consulta y redacta la respuesta, pero ningún email sale sin aprobación humana en Slack.",
        "problema": "Las consultas comerciales llegaban por un formulario con información desordenada y se respondían a mano: tarde, con calidad despareja y sin registro. ¿Cómo responder más rápido sin perder el control humano sobre lo que se envía?",
        "solucion": "Proyecto final del módulo AI Automation de la Diplomatura (negocio ficticio, datos de prueba):\n\n- n8n Cloud: flujo principal de 53 nodos.\n- Airtable: 5 tablas relacionadas y un dashboard.\n- Claude: Haiku clasifica y Sonnet redacta, solo con el catálogo de servicios.\n- Slack: aprobación humana con botones, que expira a los 45 minutos.\n- Gmail: envío de la versión exacta aprobada.",
        "resultados": "- 11 ejecuciones reales de prueba, todas con el resultado esperado (duplicados, datos incompletos, fallos de API, rechazo, expiración).\n- Las consultas incompletas o duplicadas se resuelven sin llamar a la IA.\n- Costo aproximado de USD 0,013 por consulta, un 32 % menos que usar un solo modelo para todo.",
        "herramientas": ["n8n", "Airtable", "IA generativa"],
        "repositorio": "https://github.com/damian-cordoba/datapyme-ia-automation",
        "orden": 4,
    },
    {
        "titulo": "Análisis de ventas con PostgreSQL — Superstore 2015–2018",
        "tipo": "formacion",
        "sector": "Comercio minorista",
        "periodo": "Octubre 2026",
        "resumen": "9.800 líneas de venta normalizadas en un modelo de 4 tablas y 6 preguntas de negocio respondidas con SQL. El 20 % de los clientes genera el 48,5 % de las ventas.",
        "problema": "Un CSV plano de 9.800 líneas repetía en cada fila los datos del cliente, del pedido y del producto. La dirección necesitaba saber de dónde provienen los ingresos y qué decisiones comerciales, de surtido y de logística priorizar.",
        "solucion": "Cargué los datos en PostgreSQL, los normalicé en 4 tablas (clientes, pedidos, detalle_pedidos y productos) con claves, restricciones CHECK e índices, audité y limpié los datos dejando la evidencia en SQL, y respondí 6 preguntas de negocio con JOINs, CTEs y funciones de ventana.",
        "resultados": "- El 20 % de los clientes genera el 48,5 % de las ventas, sin dependencia de una sola cuenta.\n- El negocio crece por volumen, no por ticket: los pedidos subieron un 75 % mientras el ticket promedio bajó de USD 506,71 a USD 434,71.\n- Estacionalidad marcada: septiembre, noviembre y diciembre son los meses fuertes.\n- Recomendaciones: venta cruzada para subir el ticket, preparar la operación para el último cuatrimestre y fidelizar al segmento de mayor valor.",
        "herramientas": ["SQL", "PostgreSQL"],
        "repositorio": "https://github.com/damian-cordoba/capstone_project",
        "destacado": False,
        "orden": 5,
    },
    {
        "titulo": "Sales & Customer Analytics para Marketing",
        "tipo": "personal",
        "sector": "Comercio minorista",
        "periodo": "Agosto 2026",
        "resumen": "Tablero de 6 vistas en Power BI con 20 medidas DAX, segmentación de clientes por recencia y pronóstico de ventas a 7 días.",
        "problema": "El equipo de Marketing necesitaba entender qué pasaba con las ventas, quiénes las generaban, qué categorías y regiones concentraban la facturación y cómo se gestionaban los pedidos, para priorizar su foco comercial.",
        "solucion": "Construí un modelo en esquema estrella (una tabla de hechos y cuatro dimensiones) con una tabla de medidas propia: 20 medidas DAX y 4 columnas calculadas. El tablero recorre 6 vistas, de la lectura ejecutiva al detalle de cada pedido, e incluye un pronóstico de ventas a 7 días con intervalo de confianza del 95 %.",
        "resultados": "- KPIs de ventas, ticket promedio, clientes recurrentes y concentración en el top 20 %.\n- Segmentación de clientes en activos, tibios, en riesgo e inactivos para orientar acciones de retención.\n- Se descartaron a propósito métricas como CAC, ROI o LTV porque el dataset no tenía los datos para calcularlas con precisión.",
        "herramientas": ["Power BI", "DAX", "Power Query"],
        "orden": 6,
    },
    {
        "titulo": "Dashboard ejecutivo de ventas y rentabilidad",
        "tipo": "personal",
        "sector": "Análisis comercial",
        "periodo": "Junio 2026",
        "resumen": "Datos de Excel, CSV y PDF integrados en un modelo estrella de Power BI, con comparativas interanuales y mensuales.",
        "problema": "La información comercial estaba dispersa en fuentes heterogéneas (Excel, CSV y PDF), lo que impedía analizar ventas, costos y rentabilidad en conjunto y comparar períodos.",
        "solucion": "Consolidé las fuentes con Power Query en un modelo estrella con tabla calendario creada en lenguaje M, y desarrollé medidas DAX para los KPIs (ventas, costos, rentabilidad, unidades) con comparativas YoY y MoM. El informe tiene una vista ejecutiva, una de detalle con mapa geolocalizado y un tooltip personalizado.",
        "resultados": "- Una herramienta analítica para identificar tendencias por medio de pago, zona y tipo de producto.\n- Indicadores comparativos con formato condicional para detectar desvíos de un vistazo.",
        "herramientas": ["Power BI", "DAX", "Power Query", "Excel"],
        "orden": 7,
    },
    {
        "titulo": "Datos en Criollo — sitio web con Django",
        "tipo": "formacion",
        "sector": "Desarrollo web",
        "periodo": "Noviembre 2026",
        "resumen": "Este mismo sitio: blog, casos de estudio, herramientas para PyMEs y formulario de contacto, desarrollado con Django.",
        "problema": "Necesitaba un lugar propio para mostrar mi trabajo, compartir contenido útil para PyMEs y recibir consultas, más allá de un portafolio estático.",
        "solucion": "Nació como trabajo final de la materia Python de la Diplomatura y lo amplié como sitio profesional:\n\n- Blog con CRUD, categorías, búsqueda, usuarios y permisos por autor.\n- Casos de estudio y servicios administrables desde el panel.\n- Calculadoras para PyMEs y un diagnóstico de datos.\n- Formulario de contacto con consultas guardadas en el admin.",
        "resultados": "- Más de 80 pruebas automatizadas.\n- Código público, documentado y reproducible.",
        "herramientas": ["Python", "Django"],
        "repositorio": "https://github.com/damian-cordoba/blog-django",
        "orden": 8,
    },
]


class Command(BaseCommand):
    help = "Carga el perfil, los servicios y los casos de estudio iniciales."

    def add_arguments(self, parser):
        parser.add_argument(
            "--actualizar", action="store_true", help="Pisa los textos existentes con los de este comando."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        actualizar = options["actualizar"]

        perfil = PerfilProfesional.cargar()
        if actualizar or not perfil.bio:
            for campo, valor in PERFIL.items():
                setattr(perfil, campo, valor)
            perfil.save()

        for orden, datos in enumerate(SERVICIOS, start=1):
            datos = {"orden": orden, **datos}
            servicio = Servicio.objects.filter(nombre=datos["nombre"]).first()
            if servicio is None:
                Servicio.objects.create(**datos)
            elif actualizar:
                for campo, valor in datos.items():
                    setattr(servicio, campo, valor)
                servicio.save()

        for datos in PROYECTOS:
            datos = dict(datos)
            nombres = datos.pop("herramientas")
            proyecto = Proyecto.objects.filter(titulo=datos["titulo"]).first()
            if proyecto is None:
                proyecto = Proyecto.objects.create(**datos)
            elif actualizar:
                for campo, valor in datos.items():
                    setattr(proyecto, campo, valor)
                proyecto.save()
            else:
                continue
            herramientas = [Herramienta.objects.get_or_create(nombre=n)[0] for n in nombres]
            proyecto.herramientas.set(herramientas)

        self.stdout.write(
            self.style.SUCCESS(
                f"Contenido listo: {Servicio.objects.count()} servicios y {Proyecto.objects.count()} casos de estudio."
            )
        )
