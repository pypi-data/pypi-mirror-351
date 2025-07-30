# FastAPI Frame

[![PyPI version](https://badge.fury.io/py/fastapi-frame.svg)](https://badge.fury.io/py/fastapi-frame)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-frame.svg)](https://pypi.org/project/fastapi-frame/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un template/esqueleto de proyecto FastAPI sin dependencias. Proporciona una estructura de archivos organizada para proyectos FastAPI con entidades Framework y Endpoint personalizadas.

## ⚠️ Importante

Este paquete es un **template sin dependencias funcionales**. Los archivos incluidos son un esqueleto de proyecto que necesitarás personalizar e instalar las dependencias requeridas según tus necesidades.

## 🚀 Características

- ✨ **Estructura de proyecto organizada** para FastAPI
- 🏗️ **Arquitectura modular** con separación clara de responsabilidades
- 📁 **Entidades personalizadas** (Framework y Endpoint en lugar de categorías/productos)
- 📊 **Esquemas de base de datos** preparados para personalizar
- 🔄 **Templates de controladores** y middleware
- 📝 **Estructura OpenAPI** preparada
- 🛡️ **Templates de seguridad** incluidos

## 📦 Instalación

```bash
pip install fastapi-frame
```

## 🎯 Uso como template

Después de instalar, los archivos estarán disponibles en tu entorno Python:

```python
# Los archivos se instalan en: site-packages/fastapi/
# Puedes acceder a la estructura del proyecto en:
import fastapi

# Ver la ubicación de los archivos
print(fastapi.__file__)  # Muestra dónde están los archivos

# Para usar como template:
# 1. Instala las dependencias que necesites (fastapi, sqlmodel, etc.)
# 2. Copia los archivos que quieras usar de la estructura
# 3. Personaliza según tus necesidades
```

## 📋 Dependencias recomendadas

Este template no incluye dependencias. Instala las que necesites:

```bash
pip install fastapi starlette pydantic sqlmodel sqlalchemy uvicorn

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 🏗️ Estructura del proyecto

```
fastapi-frame/
├── dependencies/          # Gestión de dependencias y BD
│   ├── entities/         # Modelos de datos (Framework, Endpoint)
│   └── registry.py       # Registro de base de datos
├── openapi/              # Controladores de API
│   ├── core.py          # Endpoints principales
│   └── tasks.py         # Gestión de tareas
├── middleware/           # Middleware personalizado
└── security/            # Utilidades de seguridad
```

## 🔍 Funcionalidades principales

### 1. Gestión de Frameworks
```python
from fastapi_frame.dependencies import Framework, FrameworkTypes

# Crear un nuevo framework
framework = Framework(
    name="FastAPI REST API",
    type=FrameworkTypes.API_FRAMEWORK
)
```

### 2. Endpoints dinámicos
```python
from fastapi_frame.dependencies import Endpoint

# Definir endpoint
endpoint = Endpoint(
    name="/users",
    method="GET",
    description="Obtener lista de usuarios",
    framework_id=1
)
```

### 3. Búsqueda inteligente
```python
# Búsqueda por texto
response = await client.post("/api/v1/search/text", json={
    "query": "api rest fastapi"
})
```

## 🛠️ Desarrollo

### Requisitos
- Python 3.8+
- FastAPI 0.100.0+
- SQLModel 0.0.8+

### Configuración de desarrollo
```bash
git clone https://github.com/tu-usuario/fastapi-frame.git
cd fastapi-frame
pip install -e ".[dev]"
```

### Ejecutar tests
```bash
pytest
```

### Formatear código
```bash
black .
isort .
```

## 📚 Documentación

La documentación completa está disponible en [GitHub](https://github.com/tu-usuario/fastapi-frame#readme).

### Ejemplos de uso

#### Configuración básica de base de datos
```python
import os
from fastapi_frame.dependencies import DatabaseRegistry

# Configurar variables de entorno
os.environ["DB_HOST"] = "localhost"
os.environ["DB_USER"] = "user"
os.environ["DB_PASSWORD"] = "password"
os.environ["DB_NAME"] = "fastapi_templates"

# Inicializar
DatabaseRegistry.initialize()
```

#### Usar los routers incluidos
```python
from fastapi import FastAPI
from fastapi_frame.openapi import core_router, tasks_router

app = FastAPI()
app.include_router(core_router, prefix="/api/v1", tags=["core"])
app.include_router(tasks_router, prefix="/api/v1", tags=["tasks"])
```

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🔗 Enlaces útiles

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 📧 Contacto

- **Autor**: Tu Nombre
- **Email**: tu.email@example.com
- **GitHub**: [@tu-usuario](https://github.com/tu-usuario)

---

⭐ ¡No olvides dar una estrella al proyecto si te ha sido útil!
