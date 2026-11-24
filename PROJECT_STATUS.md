# Estado del proyecto — Datos en Criollo

Última actualización: 24/11/2026

## Estado general

El código está **completo y verificado localmente**. Ya está copiado en la carpeta del proyecto, con su historial de Git incluido.

**Pendiente para terminar la entrega:** publicar el repositorio en GitHub (push) y hacer la verificación remota.

## Fase actual

Fase 5: Git y GitHub. Falta el push, que tiene que hacer el autor desde su PC.

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

## Archivos del proyecto

- Configuración: `config/settings.py`, `config/urls.py`, `.env.example`, `.gitignore`, `.gitattributes`, `requirements.txt`.
- App `posts`: modelos, formularios, vistas, URLs, señales, context processor, migraciones 0001 y 0002, comando `cargar_datos_demo`, templates y tests.
- App `usuarios`: modelo `Profile`, formularios, vistas, URLs, señales, migración 0001, templates y tests.
- `templates/`: `base.html`, `acerca.html`, `403.html`, `404.html` y los parciales.
- `static/`: CSS (`clean-blog.css`, `custom.css`), JS e imágenes.
- `README.md` y este archivo.

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

**Sin verificar todavía:**
- Instalación en Windows en la PC del autor.
- El repositorio publicado en GitHub.

## Próximas tareas

1. En la carpeta del proyecto: crear el venv, instalar dependencias, crear `.env`, ejecutar `migrate` y probar con `runserver`.
2. Crear en GitHub el repositorio público `blog-django`, vacío.
3. Reemplazar `<usuario>` por el usuario de GitHub en el README y hacer commit.
4. Hacer `git remote add origin ...` y `git push -u origin main`.
5. Verificar el repositorio público: README visible, archivos presentes y ningún `.env`, `venv/`, `db.sqlite3` ni `media/` subido.
6. Entregar la URL directa del repositorio.
