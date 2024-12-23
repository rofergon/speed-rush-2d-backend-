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
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Forzar recolección de basura
gc.collect()

# Pre-cargar modelo rembg con configuración de memoria limitada
logger.info("Pre-cargando modelo rembg...")
try:
    os.environ['ONNXRUNTIME_MEMORY_LIMIT'] = '256'  # Limitar memoria de ONNX a 256MB
    rembg_session = new_session()
    logger.info("Modelo rembg pre-cargado exitosamente")
except Exception as e:
    logger.error(f"Error pre-cargando modelo rembg: {str(e)}")

app = FastAPI(
    title="Speed Rush 2D Car Generator",
    description="API para generar sprites de carros 2D usando IA"
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
    logger.info("Endpoint raíz accedido")
    return {"message": "Bienvenido a Speed Rush 2D Car Generator API"}

@app.get("/health")
async def health_check():
    logger.info("Health check realizado")
    return {
        "status": "healthy", 
        "memory_usage": f"{gc.get_count()} objetos rastreados",
        "rembg_model": os.path.exists("/root/.u2net/u2net.onnx")
    }

# Manejador global de excepciones
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no manejado: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor", "error": str(exc)}
    )

# Limpiar memoria periódicamente
@app.middleware("http")
async def cleanup_memory(request: Request, call_next):
    response = await call_next(request)
    gc.collect()  # Forzar recolección de basura después de cada petición
    return response
