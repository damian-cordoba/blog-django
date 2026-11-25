# Estado del proyecto — Datos en Criollo

Última actualización: 25/11/2026

## Estado general

**Entregado y publicado.** El repositorio público está en https://github.com/damian-cordoba/blog-django, con la versión de entrega marcada con el tag `v1.0-entrega`.

## Decisiones tomadas

- El proyecto se construyó desde cero: no existía un blog previo.
- Temática: divulgación de análisis de datos para PyMEs. Nombre: «Datos en Criollo» (al principio se llamaba «Datos en Criollo Básico»; se le sacó «Básico» antes de la entrega).
- Se incluyen búsqueda y categorías, ambas pedidas por el autor.
- Las vistas de posts son Class-Based Views con `LoginRequiredMixin`. Las de usuarios son funciones con `@login_required`, como en la teoría del curso.
- Solo el autor (o un usuario staff) puede editar o eliminar un post. Otro usuario recibe un 403.
- Perfil (`Profile`) con relación OneToOne y creación automática por señal.
- Diseño: plantilla Clean Blog de Start Bootstrap (MIT). Bootstrap JS va incluido en `static/`; los fondos de encabezado son propios.
- `db.sqlite3` y `media/` quedan excluidos del repositorio. Las categorías se cargan con una migración de datos y el contenido de ejemplo con el comando `cargar_datos_demo`.
- Dependencias fijadas: Django 5.2.19 (LTS), Pillow 13.0.0 (requiere Python 3.11 o superior) y python-decouple 3.8.

## Pruebas ejecutadas

Pruebas ejecutadas el 24/11/2026 en Linux con Python 3.13:

| Verificación | Resultado |
|---|---|
| `python manage.py check` | Sin problemas |
| `python manage.py makemigrations --check --dry-run` | Sin cambios pendientes |
| `python manage.py migrate` sobre una base vacía | OK |
| `python manage.py test` | 33 pruebas OK |
| Instalación limpia: `git clone` → venv → `pip install -r requirements.txt` → `.env` → `migrate` → `runserver` | OK |
| Imágenes servidas en desarrollo (`/media/...`) | 200 |
| Visitante anónimo en `/posts/crear/` | Redirige a `/cuentas/login/?next=...` |
| Flujo en navegador real (Chrome): login → crear post con imagen → ver detalle → otro autor intenta editar | OK (403 para el post ajeno) |
| Vista móvil (390 px) | OK |
| Búsqueda de `print()` de depuración y rutas absolutas | No se encontraron |

Verificación del repositorio publicado (25/11/2026): el repositorio es público, `main` y el tag `v1.0-entrega` están en GitHub, y no se subieron `.env`, `venv/`, `db.sqlite3` ni `media/`.
