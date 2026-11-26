# Estado del proyecto — Datos en Criollo

Última actualización: 26/11/2026

## Estado general

**Etapa 2 en curso: el blog se convirtió en sitio profesional.** La versión académica quedó entregada, aprobada y marcada con el tag `v1.0-entrega`. Repositorio: https://github.com/damian-cordoba/blog-django

Etapa 2 implementada y probada localmente:
- Marca personal: Sobre mí, Servicios y Contacto.
- Casos de estudio.
- Herramientas para PyMEs.

**Pendiente:**
- Cargar en el admin la foto de perfil, las capturas de los casos y el número de WhatsApp.
- Publicar el sitio en internet (PythonAnywhere).

## Decisiones tomadas

### Etapa 1 (entrega académica)
- El proyecto se construyó desde cero: no existía un blog previo.
- Temática: divulgación de análisis de datos para PyMEs. Nombre: «Datos en Criollo» (al principio se llamaba «Datos en Criollo Básico»; se le sacó «Básico» antes de la entrega).
- Se incluyen búsqueda y categorías, ambas pedidas por el autor.
- Las vistas de posts son Class-Based Views con `LoginRequiredMixin`. Las de usuarios son funciones con `@login_required`, como en la teoría del curso.
- Solo el autor (o un usuario staff) puede editar o eliminar un post. Otro usuario recibe un 403.
- Perfil (`Profile`) con relación OneToOne y creación automática por señal.
- Diseño: plantilla Clean Blog de Start Bootstrap (MIT). Bootstrap JS va incluido en `static/`; los fondos de encabezado son propios.
- `db.sqlite3` y `media/` quedan excluidos del repositorio. Las categorías se cargan con una migración de datos y el contenido de ejemplo con el comando `cargar_datos_demo`.
- Dependencias fijadas: Django 5.2.19 (LTS), Pillow 13.0.0 (requiere Python 3.11 o superior) y python-decouple 3.8.

### Etapa 2 (sitio profesional)
- Alcance elegido por el autor: marca personal, casos de estudio y herramientas para PyMEs. Al final se publica en internet.
- Servicios presentados como freelance, a nombre del autor.
- La portada pasa a ser la página profesional. El blog se mueve a `/blog/`; los nombres de las URL no cambian, así que las pruebas y los enlaces siguen funcionando.
- La página «Acerca de» se reemplazó por «Sobre mí».
- Tres apps nuevas: `sitio`, `portafolio` y `herramientas`. Todo el contenido se edita desde el admin.
- El contenido inicial se tomó del portafolio del autor en Notion y se carga con `cargar_contenido_profesional`:
    - Las dos mentorías se unificaron en un solo servicio.
    - Se agregó «Sistemas de gestión en Excel», que es el servicio central según su biografía.
- Las imágenes de Notion no se pudieron descargar automáticamente. Se suben desde el admin.
- Sin dependencias nuevas.
- Seguridad:
    - El formulario de contacto tiene un campo trampa contra bots y el correo es opcional.
    - Los tableros embebidos solo aceptan enlaces https de dominios permitidos.
    - Los textos con listas se escapan antes de convertirse en HTML.

## Pruebas ejecutadas

### Etapa 2 (26/11/2026, Linux, Python 3.13)

| Verificación | Resultado |
|---|---|
| `python manage.py check` | Sin problemas |
| `python manage.py makemigrations --check --dry-run` | Sin cambios pendientes |
| `python manage.py test` | 82 pruebas OK |
| Todas las páginas nuevas | Responden 200 |
| Revisión visual en Chrome: portada, servicios, sobre mí, caso de estudio, calculadoras y diagnóstico | OK |
| Vista móvil (390 px) sin desbordes horizontales | OK, después de corregir el correo del pie |

### Etapa 1 (24/11/2026)

| Verificación | Resultado |
|---|---|
| Instalación limpia desde GitHub siguiendo el README | OK |
| `python manage.py test` | 33 pruebas OK |
| Flujo en navegador: login, crear post con imagen, permiso 403 en post ajeno | OK |

Verificación del repositorio publicado (25/11/2026): el repositorio es público, `main` y el tag `v1.0-entrega` están en GitHub, y no se subieron `.env`, `venv/`, `db.sqlite3` ni `media/`.

## Próximas tareas

1. Bajar los cambios a la PC del autor, ejecutar `migrate` y `cargar_contenido_profesional`, y subir los cambios a GitHub.
2. Cargar en el admin la foto de perfil, las capturas de los casos y el número de WhatsApp.
3. Publicar en PythonAnywhere con `DEBUG=False`.
4. Ideas pendientes de etapas futuras:
    - Markdown con código resaltado en los posts.
    - Vista previa al compartir y SEO (sitemap).
    - Panel «El blog en datos».
    - Plantillas descargables.
