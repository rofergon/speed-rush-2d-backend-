from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from .routes import car_generation
import os
import gc
from rembg import new_session

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar a DEBUG para más información
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Registrar información del entorno
logger.info(f"Iniciando aplicación en el entorno: {os.getenv('RAILWAY_ENVIRONMENT', 'local')}")
logger.info(f"Puerto configurado: {os.getenv('PORT', '8080')}")
logger.info(f"Python path: {os.getenv('PYTHONPATH')}")

try:
    # Forzar recolección de basura
    gc.collect()

    # Pre-cargar modelo rembg con configuración de memoria limitada
    logger.info("Pre-cargando modelo rembg...")
    os.environ['ONNXRUNTIME_MEMORY_LIMIT'] = '256'  # Limitar memoria de ONNX a 256MB
    rembg_session = new_session()
    logger.info("Modelo rembg pre-cargado exitosamente")
except Exception as e:
    logger.error(f"Error pre-cargando modelo rembg: {str(e)}")
    rembg_session = None

# Crear aplicación FastAPI
app = FastAPI(
    title="Speed Rush 2D Car Generator",
    description="API para generar sprites de carros 2D usando IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(car_generation.router, prefix="/api/cars", tags=["cars"])

@app.get("/")
async def root():
    """Endpoint raíz que muestra información básica de la API."""
    logger.info("Endpoint raíz accedido")
    return {
        "message": "Bienvenido a Speed Rush 2D Car Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "local"),
        "port": os.getenv("PORT", "8080")
    }

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API."""
    try:
        from .config import settings
        config_status = "OK"
    except Exception as e:
        logger.error(f"Error en configuración: {str(e)}")
        config_status = f"Error: {str(e)}"

    health_info = {
        "status": "healthy",
        "config_status": config_status,
        "memory_usage": f"{gc.get_count()} objetos rastreados",
        "rembg_model": "Cargado" if rembg_session else "No cargado",
        "environment": os.getenv("RAILWAY_ENVIRONMENT_NAME", "local"),
        "port": os.getenv("PORT", "8080")
    }
    
    logger.info(f"Health check realizado: {health_info}")
    return health_info

# Manejador global de excepciones
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Manejador global de excepciones para la API."""
    error_msg = f"Error no manejado: {str(exc)}"
    logger.error(error_msg, exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "error": str(exc),
            "path": request.url.path,
            "method": request.method,
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "local")
        }
    )

# Limpiar memoria periódicamente
@app.middleware("http")
async def cleanup_memory(request: Request, call_next):
    """Middleware para limpiar la memoria después de cada petición."""
    try:
        response = await call_next(request)
        gc.collect()
        return response
    except Exception as e:
        logger.error(f"Error en middleware: {str(e)}", exc_info=True)
        raise
