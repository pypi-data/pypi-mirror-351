import os
from api import webhook_router
from controllers import core_router, tasks_router
from . import FastAPI
from contextlib import asynccontextmanager
from db import DatabaseRegistry
import logging

logger = logging.getLogger("")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(console_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializar la base de datos
    logger.info("Iniciando aplicación backend")
    logger.info("Inicializando la conexión a la base de datos...")
    DatabaseRegistry.initialize(
        os.getenv("DB_URL", "mysql+pymysql://user:password@db/nombre")
    )
    logger.info("Base de datos inicializada correctamente.")
    # Ya no se cargan datos de muestra desde JSON

    yield

    # Limpieza al cerrar la aplicación
    logger.info("Cerrando conexiones a la base de datos...")
    DatabaseRegistry.close()
    logger.info("Aplicación backend cerrada correctamente")


app = FastAPI(
    title="E-commerce Search API",
    lifespan=lifespan
)

# Configuración de la base de datos
# Usar la URL de conexión completa
DB_URL = os.getenv("DB_URL", "mysql+pymysql://user:password@db/ecommerce")

# Incluir routers de la API
logger.info("Configurando routers de la aplicación")
app.include_router(core_router)
app.include_router(webhook_router)
app.include_router(tasks_router)
logger.info("Routers configurados correctamente")
