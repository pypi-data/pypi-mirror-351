"""
Ejemplo de uso del paquete fastapi-templates-framework

Este ejemplo muestra cómo usar las entidades Framework y Endpoint
para crear una aplicación FastAPI con templates organizados.
"""

from fastapi import FastAPI, HTTPException
from fastapi_templates_framework.dependencies.entities import Framework, Endpoint, FrameworkTypes
from fastapi_templates_framework.dependencies.registry import FrameworkRegistry
from typing import List

# Crear la aplicación FastAPI
app = FastAPI(
    title="FastAPI Templates Framework Demo",
    description="Demostración del paquete fastapi-templates-framework",
    version="0.1.0"
)

# Crear instancia del registro de frameworks
framework_registry = FrameworkRegistry()

# Datos de ejemplo
frameworks_data = [
    {"id": 1, "name": "FastAPI", "type": FrameworkTypes.API_FRAMEWORK},
    {"id": 2, "name": "Django", "type": FrameworkTypes.WEB_FRAMEWORK},
    {"id": 3, "name": "Flask", "type": FrameworkTypes.MICROSERVICE},
    {"id": 4, "name": "Starlette", "type": FrameworkTypes.ASYNC_FRAMEWORK},
]

endpoints_data = [
    {"id": 1, "name": "/users", "method": "GET", "framework_id": 1},
    {"id": 2, "name": "/users", "method": "POST", "framework_id": 1},
    {"id": 3, "name": "/products", "method": "GET", "framework_id": 1},
    {"id": 4, "name": "/auth/login", "method": "POST", "framework_id": 2},
    {"id": 5, "name": "/api/health", "method": "GET", "framework_id": 3},
]

# Convertir datos a objetos
frameworks = [Framework(**data) for data in frameworks_data]
endpoints = [Endpoint(**data) for data in endpoints_data]

@app.get("/")
async def root():
    """Endpoint raíz con información del paquete"""
    return {
        "message": "FastAPI Templates Framework Demo",
        "package": "fastapi-templates-framework",
        "version": "0.1.0",
        "endpoints": {
            "frameworks": "/frameworks",
            "endpoints": "/endpoints",
            "frameworks_by_type": "/frameworks/type/{framework_type}",
            "endpoints_by_framework": "/frameworks/{framework_id}/endpoints"
        }
    }

@app.get("/frameworks", response_model=List[Framework])
async def get_frameworks():
    """Obtener todos los frameworks disponibles"""
    return frameworks

@app.get("/frameworks/{framework_id}", response_model=Framework)
async def get_framework(framework_id: int):
    """Obtener un framework específico por ID"""
    framework = next((f for f in frameworks if f.id == framework_id), None)
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    return framework

@app.get("/frameworks/type/{framework_type}")
async def get_frameworks_by_type(framework_type: FrameworkTypes):
    """Obtener frameworks por tipo"""
    filtered_frameworks = [f for f in frameworks if f.type == framework_type]
    return filtered_frameworks

@app.get("/endpoints", response_model=List[Endpoint])
async def get_endpoints():
    """Obtener todos los endpoints disponibles"""
    return endpoints

@app.get("/frameworks/{framework_id}/endpoints")
async def get_endpoints_by_framework(framework_id: int):
    """Obtener endpoints de un framework específico"""
    framework_endpoints = [e for e in endpoints if e.framework_id == framework_id]
    return framework_endpoints

@app.post("/frameworks", response_model=Framework)
async def create_framework(framework: Framework):
    """Crear un nuevo framework"""
    # Asignar nuevo ID
    new_id = max([f.id for f in frameworks], default=0) + 1
    framework.id = new_id
    frameworks.append(framework)
    return framework

@app.post("/endpoints", response_model=Endpoint)
async def create_endpoint(endpoint: Endpoint):
    """Crear un nuevo endpoint"""
    # Verificar que el framework existe
    framework_exists = any(f.id == endpoint.framework_id for f in frameworks)
    if not framework_exists:
        raise HTTPException(status_code=400, detail="Framework not found")
    
    # Asignar nuevo ID
    new_id = max([e.id for e in endpoints], default=0) + 1
    endpoint.id = new_id
    endpoints.append(endpoint)
    return endpoint

if __name__ == "__main__":
    import uvicorn
    print("Iniciando FastAPI Templates Framework Demo...")
    print("Documentación disponible en: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
