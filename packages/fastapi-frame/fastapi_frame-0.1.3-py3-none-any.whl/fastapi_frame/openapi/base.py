'''
API para la gestión de tareas.
Este módulo proporciona endpoints para consultar el estado y los resultados de tareas de inferencia.
'''

from . import APIRouter, HTTPException, status
from pydantic import BaseModel
from utils import get_logger

from services import ResultService
from db import Framework, Endpoint, DatabaseRegistry
from sqlmodel import select

logger = get_logger("backend_tasks_controller")

router = APIRouter()


class TaskStatus(BaseModel):
    """Estado de una tarea."""
    status: str


@router.get(
    "/tasks/{task_id}/result",
    status_code=status.HTTP_200_OK,
    responses={
        202: {"model": TaskStatus, "description": "Tarea pendiente"},
        404: {"model": TaskStatus, "description": "Tarea no encontrada"},
    },
)
async def get_task_result(task_id: str):
    """
    Consulta el resultado de una tarea de inferencia.
    Args:
        task_id: Identificador único de la tarea.
    Returns:
        Si la tarea está completada, devuelve los frameworks predichos y los endpoints asociados.
        Si la tarea aún está en proceso, devuelve un estado "pending" con código HTTP 202.
        Si la tarea no existe, devuelve un error 404.
    """
    logger.info(f"Consultando resultado de tarea: {task_id}")
    result_service = ResultService()

    if not result_service.has_result(task_id):
        logger.debug(f"Tarea {task_id} aún en proceso")
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="La tarea aún está en proceso",
        )

    frameworks_predictions = result_service.get_result(task_id)
    logger.debug(f"Tarea {task_id} completada con {len(frameworks_predictions)} predicciones")

    # Filtrar predicciones por umbral de confianza (podría configurarse desde variables de entorno)
    confidence_threshold = 0.05  # Umbral configurable - lowered to show more results
    filtered_predictions = [p for p in frameworks_predictions if p.score >= confidence_threshold]
    logger.debug(f"Aplicado filtro de confianza {confidence_threshold}: {len(filtered_predictions)} predicciones válidas")

    if not filtered_predictions:
        logger.info(f"Tarea {task_id} - No hay predicciones que superen el umbral")
        return {"frameworks": [], "endpoints": []}

    # Obtener frameworks predichos
    framework_ids = [p.label for p in filtered_predictions]
    logger.debug(f"IDs de frameworks predichos: {framework_ids}")

    # Buscar endpoints asociados a los frameworks predichos
    session = DatabaseRegistry.session()
    frameworks = session.exec(
        select(Framework).where(Framework.id.in_(framework_ids))
    ).all()

    # Obtener nombres de frameworks
    framework_names = [framework.name for framework in frameworks]
    logger.debug(f"Nombres de frameworks encontrados: {framework_names}")

    # Buscar endpoints de los frameworks
    endpoints = session.exec(
        select(Endpoint).where(Endpoint.framework_id.in_(framework_ids))
    ).all()

    logger.info(f"Tarea {task_id} completada exitosamente - {len(framework_names)} frameworks, {len(endpoints)} endpoints")

    return {
        "frameworks": framework_names,
        "endpoints": [
            {"id": e.id, "name": e.name, "method": e.method}
            for e in endpoints
        ],
    }
