# Modificaciones realizadas para el tema FastAPI

## Resumen de cambios

Se han modificado todos los archivos proporcionados para cambiar el tema de un sistema de e-commerce a un sistema de templates de FastAPI, manteniendo exactamente la misma estructura.

## Cambios realizados:

### 1. Entidades (dependencies/entities/)

#### category.py → Ahora define Framework
- **Antes**: `Category` con tipos de productos (CAMISETAS, TELEFONOS, etc.)
- **Ahora**: `Framework` con tipos de frameworks web (WEB_FRAMEWORK, API_FRAMEWORK, MICROSERVICE, etc.)
- **Enum cambiado**: `CategoryTypes` → `FrameworkTypes`

#### product.py → Ahora define Endpoint
- **Antes**: `Product` con campos `name`, `description`, `price`, `category_id`
- **Ahora**: `Endpoint` con campos `name`, `description`, `method`, `framework_id`
- **Cambio principal**: `price` (float) → `method` (str), `category_id` → `framework_id`

#### __init__.py
- **Exports actualizados**: `Category, Product, CategoryTypes` → `Framework, Endpoint, FrameworkTypes`

### 2. Registry (dependencies/registry.py)
- **Base de datos**: `DB_NAME` cambiado de "ecommerce" → "fastapi_templates"

### 3. Core API (openapi/core.py)

#### Endpoints modificados:
- `/categories` → `/frameworks`
- `/products` → `/endpoints`

#### Lógica de búsqueda actualizada:
- **Palabras clave**: Cambiadas de productos (camisetas, pantalones, etc.) a conceptos de FastAPI (web, api, microservice, async, middleware)
- **Campos de respuesta**: 
  - `categories` → `frameworks`
  - `products` → `endpoints`
  - `price` → `method`

#### Keywords de búsqueda:
```python
framework_keywords = {
    "web_framework": ["web", "framework", "http", "server"],
    "api_framework": ["api", "rest", "fastapi", "endpoint"],
    "microservice": ["microservice", "micro", "service", "distributed"],
    "async_framework": ["async", "asyncio", "await", "asynchronous"],
    "middleware": ["middleware", "interceptor", "filter"],
    "other": ["other", "otros"]
}
```

### 4. Tasks API (openapi/tasks.py)

#### Cambios en comentarios y variables:
- `categories_predictions` → `frameworks_predictions`
- `category_ids` → `framework_ids`
- `category_names` → `framework_names`
- `products` → `endpoints`

#### Respuesta JSON actualizada:
- `categories` → `frameworks`
- `products` → `endpoints`
- Campos de endpoint: `{"id", "name", "method"}` en lugar de `{"id", "name", "price"}`

## Estructura mantenida

- **Arquitectura**: Misma estructura de carpetas y módulos
- **Patrones**: Mismo patrón de imports, decoradores, y manejo de errores
- **Lógica**: Misma lógica de búsqueda y filtrado, solo cambiaron los datos temáticos
- **API**: Mismos endpoints HTTP, solo cambió el contenido semántico

## Temática resultante

El sistema ahora funciona como un explorador/buscador de templates y patrones de FastAPI:
- **Frameworks**: Diferentes tipos de frameworks web (FastAPI, microservicios, etc.)
- **Endpoints**: Endpoints HTTP con sus métodos (GET, POST, PUT, DELETE)
- **Búsquedas**: Por texto buscando conceptos de desarrollo web y APIs
- **Imágenes**: Inferencia para clasificar imágenes relacionadas con arquitecturas web

Todos los archivos mantienen la misma funcionalidad pero adaptada al dominio de desarrollo web con FastAPI.
