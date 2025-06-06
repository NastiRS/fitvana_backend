# API de Blog - Documentación Completa

## Descripción General
Esta es una API REST desarrollada con FastAPI para gestionar un sistema de blog completo. La aplicación permite crear, leer, actualizar y eliminar blog posts, categorías, tags, secciones y anuncios, con relaciones complejas entre estas entidades.

## Arquitectura
- **Framework**: FastAPI
- **Base de datos**: SQLModel/SQLAlchemy
- **Patrón**: Repository Pattern
- **Autenticación**: No implementada (pendiente)

## URL Base
```
http://localhost:8000
```

## Entidades Principales

### 1. Blog Posts
Los blog posts son la entidad central del sistema.

**Campos:**
- `id`: UUID único
- `title`: Título del post (requerido)
- `content`: Contenido del post (requerido)
- `date`: Fecha de publicación
- `category_id`: ID de la categoría (requerido)
- `created_at`: Fecha de creación
- `updated_at`: Fecha de última actualización

**Relaciones:**
- Pertenece a una categoría (many-to-one)
- Puede tener múltiples tags (many-to-many)
- Puede tener múltiples secciones (one-to-many)
- Puede tener múltiples anuncios (many-to-many)

### 2. Categorías
Organizan los blog posts por temas.

**Campos:**
- `id`: UUID único
- `name`: Nombre de la categoría (requerido)
- `description`: Descripción opcional

### 3. Tags
Etiquetas para clasificar y filtrar contenido.

**Campos:**
- `id`: UUID único
- `name`: Nombre del tag (requerido)

### 4. Secciones
Partes individuales de un blog post para contenido estructurado.

**Campos:**
- `id`: UUID único
- `title`: Título de la sección (requerido)
- `content`: Contenido de la sección (requerido)
- `image_url`: URL de imagen opcional
- `position_order`: Orden de la sección (número)
- `blog_post_id`: ID del blog post al que pertenece

### 5. Anuncios
Anuncios que pueden asociarse a blog posts.

**Campos:**
- `id`: UUID único
- `name`: Nombre del anuncio (requerido)
- `url`: URL del anuncio (opcional)
- `image_url`: URL de imagen del anuncio (opcional)

## Endpoints de la API

### Health Check
- **GET** `/health` - Verificar estado de la API

### Blog Posts (`/v1/api/blog_posts`)

#### CRUD Básico
- **POST** `/v1/api/blog_posts` - Crear nuevo blog post
- **GET** `/v1/api/blog_posts` - Obtener todos los blog posts (con paginación)
- **GET** `/v1/api/blog_posts/{blog_post_id}` - Obtener blog post específico
- **PUT** `/v1/api/blog_posts/{blog_post_id}` - Actualizar blog post
- **DELETE** `/v1/api/blog_posts/{blog_post_id}` - Eliminar blog post

#### Gestión de Tags
- **POST** `/v1/api/blog_posts/{blog_post_id}/tags/{tag_id}` - Agregar tag a blog post
- **DELETE** `/v1/api/blog_posts/{blog_post_id}/tags/{tag_id}` - Quitar tag de blog post
- **GET** `/v1/api/blog_posts/{blog_post_id}/tags` - Obtener tags de un blog post

#### Gestión de Categorías
- **PUT** `/v1/api/blog_posts/{blog_post_id}/category/{category_id}` - Asignar categoría
- **GET** `/v1/api/blog_posts/{blog_post_id}/category` - Obtener categoría de un blog post

### Categorías (`/v1/api/categories`)

#### CRUD Básico
- **POST** `/v1/api/categories` - Crear nueva categoría
- **GET** `/v1/api/categories` - Obtener todas las categorías (con paginación)
- **GET** `/v1/api/categories/{category_id}` - Obtener categoría específica
- **PUT** `/v1/api/categories/{category_id}` - Actualizar categoría
- **DELETE** `/v1/api/categories/{category_id}` - Eliminar categoría

#### Relaciones
- **GET** `/v1/api/categories/{category_id}/blog_posts` - Obtener blog posts de una categoría

### Tags (`/v1/api/tags`)

#### CRUD Básico
- **POST** `/v1/api/tags` - Crear nuevo tag
- **GET** `/v1/api/tags` - Obtener todos los tags (con paginación)
- **GET** `/v1/api/tags/{tag_id}` - Obtener tag específico
- **PUT** `/v1/api/tags/{tag_id}` - Actualizar tag
- **DELETE** `/v1/api/tags/{tag_id}` - Eliminar tag

### Secciones (`/v1/api/sections`)

#### CRUD Básico
- **POST** `/v1/api/sections` - Crear nueva sección
- **GET** `/v1/api/sections` - Obtener todas las secciones (con paginación)
- **GET** `/v1/api/sections/{section_id}` - Obtener sección específica
- **PUT** `/v1/api/sections/{section_id}` - Actualizar sección
- **DELETE** `/v1/api/sections/{section_id}` - Eliminar sección

#### Relaciones
- **GET** `/v1/api/sections/blog_post/{blog_post_id}` - Obtener secciones de un blog post (ordenadas por position_order)

### Anuncios (`/v1/api/announcements`)

#### CRUD Básico
- **POST** `/v1/api/announcements` - Crear nuevo anuncio
- **GET** `/v1/api/announcements` - Obtener todos los anuncios (con paginación)
- **GET** `/v1/api/announcements/{announcement_id}` - Obtener anuncio específico
- **PUT** `/v1/api/announcements/{announcement_id}` - Actualizar anuncio
- **DELETE** `/v1/api/announcements/{announcement_id}` - Eliminar anuncio

#### Relaciones con Blog Posts
- **POST** `/v1/api/announcements/blog_post/{blog_post_id}/announcements/{announcement_id}` - Asociar anuncio a blog post
- **DELETE** `/v1/api/announcements/blog_post/{blog_post_id}/announcements/{announcement_id}` - Desasociar anuncio de blog post
- **GET** `/v1/api/announcements/{announcement_id}/blog_posts` - Obtener blog posts de un anuncio
- **GET** `/v1/api/announcements/blog_post/{blog_post_id}` - Obtener anuncios de un blog post

## Parámetros de Paginación
Todos los endpoints de listado soportan paginación:
- `skip`: Número de elementos a omitir (default: 0)
- `limit`: Número máximo de elementos a devolver (default: 100)

## Códigos de Estado HTTP
- `200`: Operación exitosa
- `201`: Recurso creado exitosamente
- `204`: Eliminación exitosa (sin contenido)
- `404`: Recurso no encontrado
- `500`: Error interno del servidor

## Ejemplos de Uso para Frontend

### Crear un Blog Post Completo
```javascript
// 1. Crear categoría
const category = await fetch('/v1/api/categories', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Tecnología',
    description: 'Posts sobre tecnología'
  })
});

// 2. Crear tags
const tag1 = await fetch('/v1/api/tags', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'JavaScript' })
});

// 3. Crear blog post
const blogPost = await fetch('/v1/api/blog_posts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'Mi primer post',
    content: 'Contenido del post...',
    category_id: category.id
  })
});

// 4. Agregar tags al blog post
await fetch(`/v1/api/blog_posts/${blogPost.id}/tags/${tag1.id}`, {
  method: 'POST'
});

// 5. Crear secciones
await fetch('/v1/api/sections', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'Introducción',
    content: 'Esta es la introducción...',
    position_order: 1,
    blog_post_id: blogPost.id
  })
});
```

### Obtener Blog Post Completo con Relaciones
```javascript
// Obtener blog post con todas sus relaciones
const blogPost = await fetch(`/v1/api/blog_posts/${blogPostId}`);

// Obtener secciones ordenadas
const sections = await fetch(`/v1/api/sections/blog_post/${blogPostId}`);

// Obtener anuncios asociados
const announcements = await fetch(`/v1/api/announcements/blog_post/${blogPostId}`);
```

## Funcionalidades Clave para el Frontend

### Dashboard de Administración
- Lista de todos los blog posts con filtros por categoría y tags
- Formularios CRUD para todas las entidades
- Gestión de relaciones entre entidades
- Vista previa de blog posts

### Blog Público
- Lista de blog posts publicados
- Vista individual de blog post con secciones ordenadas
- Filtrado por categorías y tags
- Visualización de anuncios asociados

### Gestión de Contenido
- Editor de blog posts con secciones múltiples
- Gestión de imágenes para secciones y anuncios
- Organización de contenido por categorías
- Sistema de etiquetado

## Consideraciones para el Frontend
1. **Manejo de UUIDs**: Todos los IDs son UUIDs, no números enteros
2. **Paginación**: Implementar paginación en todas las listas
3. **Validación**: La API devuelve errores detallados para validación
4. **Relaciones**: Algunas operaciones requieren múltiples llamadas a la API
5. **Orden de secciones**: Las secciones tienen un campo `position_order` para ordenamiento
6. **Fechas**: Manejar formatos de fecha ISO para `created_at`, `updated_at` y `date`

### Requisitos
- Python 3.13+
- uv (gestor de paquetes Python)

### Pasos para ejecutar la aplicación
1. Clonar el repositorio
2. Instalar dependencias: `uv sync`
3. Activar el entorno virtual: `source .venv/bin/activate` (Linux/Mac) o `.venv\Scripts\activate` (Windows)
4. Ejecutar la aplicación: `uvicorn src.main:app --reload`
5. Acceder a la documentación interactiva en: `http://localhost:8000/docs`

### Estructura del Proyecto
```
src/
├── core/           # Configuración de base de datos
├── domain/         # Modelos y esquemas
│   ├── models/     # Modelos SQLModel
│   └── schemas/    # Esquemas Pydantic
├── repository/     # Capa de acceso a datos
├── routers/        # Endpoints de la API
└── main.py         # Aplicación principal

tests/              # Pruebas unitarias
Front end Views/    # Vistas HTML de referencia
```

## Documentación Adicional
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

Este README proporciona toda la información necesaria para desarrollar un frontend completo que consuma esta API de blog. Incluye todos los endpoints disponibles, ejemplos de uso, y consideraciones importantes para la implementación del frontend.
