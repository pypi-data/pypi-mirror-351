# FastAPI Templates Framework

[![PyPI version](https://badge.fury.io/py/fastapi-templates-framework.svg)](https://badge.fury.io/py/fastapi-templates-framework)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-templates-framework.svg)](https://pypi.org/project/fastapi-templates-framework/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un framework moderno y eficiente para el desarrollo rápido de APIs con FastAPI, que incluye templates, utilidades y patrones pre-configurados para acelerar el desarrollo de aplicaciones web.

## 🚀 Características

- ✨ **Templates pre-configurados** para diferentes tipos de APIs
- 🏗️ **Arquitectura modular** con separación clara de responsabilidades
- 🔍 **Sistema de búsqueda avanzado** para frameworks y endpoints
- 📊 **Gestión de base de datos** con SQLModel integrado
- 🔄 **Procesamiento asíncrono** de tareas
- 📝 **Documentación automática** con OpenAPI
- 🛡️ **Middleware de seguridad** incluido

## 📦 Instalación

```bash
pip install fastapi-templates-framework
```

Para desarrollo:
```bash
pip install fastapi-templates-framework[dev]
```

## 🎯 Uso rápido

```python
from fastapi import FastAPI
from fastapi_templates_framework import DatabaseRegistry, Framework, Endpoint

# Crear aplicación FastAPI
app = FastAPI(title="Mi API")

# Configurar base de datos
DatabaseRegistry.initialize()

# Importar routers
from fastapi_templates_framework.openapi import core_router
app.include_router(core_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 🏗️ Estructura del proyecto

```
fastapi-templates-framework/
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
from fastapi_templates_framework.dependencies import Framework, FrameworkTypes

# Crear un nuevo framework
framework = Framework(
    name="FastAPI REST API",
    type=FrameworkTypes.API_FRAMEWORK
)
```

### 2. Endpoints dinámicos
```python
from fastapi_templates_framework.dependencies import Endpoint

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
git clone https://github.com/tu-usuario/fastapi-templates-framework.git
cd fastapi-templates-framework
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

La documentación completa está disponible en [GitHub](https://github.com/tu-usuario/fastapi-templates-framework#readme).

### Ejemplos de uso

#### Configuración básica de base de datos
```python
import os
from fastapi_templates_framework.dependencies import DatabaseRegistry

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
from fastapi_templates_framework.openapi import core_router, tasks_router

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
