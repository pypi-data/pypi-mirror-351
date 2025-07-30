from . import APIRouter, Body, UploadFile, File, HTTPException
from sqlmodel import select
from db import DatabaseRegistry, Framework, Endpoint
from utils import get_logger
import requests
import os
import unicodedata
import re

logger = get_logger("backend_core_controller")

router = APIRouter()

# Configuración del servicio de inferencia
INFERENCE_SERVICE_URL = os.getenv("INFERENCE_SERVICE_URL", "http://inference-dev:80")


@router.get("/health")
def health_check():
    logger.debug("Health check solicitado")
    return {"status": "ok"}


@router.get("/frameworks")
def get_frameworks():
    logger.info("Solicitando lista de frameworks")
    session = DatabaseRegistry.session()
    frameworks = session.exec(select(Framework)).all()
    logger.debug(f"Encontrados {len(frameworks)} frameworks")
    return {"frameworks": [{"id": f.id, "name": f.name} for f in frameworks]}


@router.get("/endpoints")
def get_endpoints():
    logger.info("Solicitando lista de endpoints")
    session = DatabaseRegistry.session()
    endpoints = session.exec(select(Endpoint)).all()
    logger.debug(f"Encontrados {len(endpoints)} endpoints")
    return {"endpoints": [{"id": e.id, "name": e.name, "method": e.method} for e in endpoints]}


@router.post("/search/text")
def search_text(payload: dict = Body(...)):
    query = payload.get("query", "").lower()
    logger.info(f"Búsqueda de texto solicitada - query: '{query}'")

    # Normalizar texto: quitar tildes y signos de puntuación
    def normalize(text):
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore').decode('utf-8')
        text = re.sub(r'[\W_]+', ' ', text)
        return text.lower()
    query_norm = normalize(query)
    tokens = query_norm.split()

    # Diccionario de palabras clave por framework
    framework_keywords = {
        "web_framework": ["web", "framework", "http", "server"],
        "api_framework": ["api", "rest", "fastapi", "endpoint"],
        "microservice": ["microservice", "micro", "service", "distributed"],
        "async_framework": ["async", "asyncio", "await", "asynchronous"],
        "middleware": ["middleware", "interceptor", "filter"],
        "other": ["other", "otros"]
    }

    # Buscar coincidencias de palabras clave
    matched = set()
    for framework, keywords in framework_keywords.items():
        for kw in keywords:
            if kw in tokens:
                matched.add(framework)
    logger.debug(f"Frameworks encontrados: {matched}")

    session = DatabaseRegistry.session()
    all_frameworks = session.exec(select(Framework)).all()
    endpoints = session.exec(select(Endpoint)).all()

    # Obtener ids de frameworks coincidentes ignorando mayúsculas/minúsculas y tildes
    def normalize_framework_name(name):
        name = unicodedata.normalize('NFD', name)
        name = name.encode('ascii', 'ignore').decode('utf-8')
        return name.lower()
    matched_ids = [f.id for f in all_frameworks if normalize_framework_name(f.name) in matched]
    filtered = [e for e in endpoints if e.framework_id in matched_ids]

    # búsqueda por palabra en nombre o descripción (palabra completa, no subcadena) ---
    # Para cada endpoint, separar el nombre y descripción en palabras y buscar
    # coincidencias exactas con las palabras de la query
    extra_endpoints = []
    query_words = set(tokens)
    for e in endpoints:
        name_words = set(normalize(e.name).split())
        desc_words = set(normalize(e.description or '').split())
        # Coincidencia si alguna palabra de la query está exactamente en el nombre o descripción
        if query_words & (name_words | desc_words):
            if e not in filtered:
                extra_endpoints.append(e)
    filtered.extend(extra_endpoints)

    logger.info(f"Búsqueda completada - {len(matched)} frameworks, {len(filtered)} endpoints")

    # Devolver nombres de framework reales (capitalizados) para la respuesta
    matched_names = [f.name for f in all_frameworks if f.id in matched_ids]
    # Si no se detectó ningún framework pero hay endpoints, añadir el framework de cada endpoint a frameworks (únicas)
    if not matched_names and filtered:
        matched_names = list({next((f.name for f in all_frameworks if f.id == e.framework_id),
                                   None) for e in filtered if e.framework_id})
    return {
        "frameworks": matched_names,
        "endpoints": [
            {
                "id": e.id,
                "name": e.name,
                "method": e.method,
                "framework": next((f.name for f in all_frameworks if f.id == e.framework_id), None)
            }
            for e in filtered
        ]
    }


@router.post("/search/image")
async def search_image(file: UploadFile = File(...)):
    """
    Recibe una imagen enviada por el usuario, encola una tarea de inferencia y devuelve un task_id.
    """
    logger.info(f"Búsqueda por imagen solicitada - archivo: {file.filename}")
    try:
        # Verificar que el archivo sea una imagen
        if not file.content_type or not file.content_type.startswith("image/"):
            logger.warning(f"Archivo inválido recibido - tipo: {file.content_type}")
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

        # Preparar el archivo para enviarlo al servicio de inferencia
        file_data = await file.read()
        logger.debug(f"Imagen leída - tamaño: {len(file_data)} bytes")

        # Enviar la imagen al servicio de inferencia
        files = {"file": (file.filename, file_data, file.content_type)}
        logger.debug(f"Enviando imagen al servicio de inferencia: {INFERENCE_SERVICE_URL}")
        response = requests.post(
            f"{INFERENCE_SERVICE_URL}/infer/image",
            files=files,
            timeout=30
        )

        if response.status_code != 200:
            logger.error(f"Error del servicio de inferencia - status: {response.status_code}")
            raise HTTPException(
                status_code=500,
                detail="Error al procesar la imagen en el servicio de inferencia"
            )

        result = response.json()
        logger.info(f"Tarea de inferencia creada exitosamente - task_id: {result['task_id']}")
        return {"task_id": result["task_id"]}
    except HTTPException as e:
        raise e
    except requests.RequestException as e:
        logger.error(f"Error de conexión con servicio de inferencia: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error de conexión con el servicio de inferencia: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error interno en búsqueda por imagen: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
