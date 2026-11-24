"""Carga las categorías base del blog para que existan desde el primer migrate."""

from django.db import migrations

CATEGORIAS = [
    ("Excel", "excel", "Fórmulas, tablas dinámicas y Power Query para el día a día."),
    ("Power BI", "power-bi", "Tableros y medidas DAX para entender tu negocio."),
    ("SQL", "sql", "Consultas para sacarle datos a tus sistemas."),
    ("Python", "python", "Automatización y análisis con pandas y amigos."),
    ("Estadística", "estadistica", "Conceptos para interpretar números sin engañarse."),
    ("Gestión y KPIs", "gestion-y-kpis", "Qué medir y cómo tomar decisiones con datos."),
]


def crear_categorias(apps, schema_editor):
    Categoria = apps.get_model("posts", "Categoria")
    for nombre, slug, descripcion in CATEGORIAS:
        Categoria.objects.get_or_create(
            slug=slug, defaults={"nombre": nombre, "descripcion": descripcion}
        )


def borrar_categorias(apps, schema_editor):
    Categoria = apps.get_model("posts", "Categoria")
    Categoria.objects.filter(slug__in=[slug for _, slug, _ in CATEGORIAS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_categorias, borrar_categorias),
    ]
