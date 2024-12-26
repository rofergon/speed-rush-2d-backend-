import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

def load_environment():
    """Cargar variables de entorno de diferentes fuentes."""
    # 1. Intentar cargar desde .env local
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        logger.info(f"Cargando variables de entorno desde {env_file}")
        load_dotenv(env_file)
    
    # 2. Intentar cargar usando find_dotenv()
    dotenv_path = find_dotenv()
    if dotenv_path:
        logger.info(f"Cargando variables de entorno desde {dotenv_path}")
        load_dotenv(dotenv_path)
    
    # Registrar variables encontradas (sin mostrar valores sensibles)
    logger.info("Variables de entorno cargadas:")
    for key in os.environ:
        if any(secret in key.lower() for secret in ['key', 'password', 'secret', 'token']):
            logger.info(f"{key}=***[HIDDEN]***")
        else:
            logger.info(f"{key}={os.environ[key]}")

# Cargar variables de entorno
load_environment()

class Settings:
    """Configuración de la aplicación."""
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    STABILITY_API_KEY: str = os.getenv("STABILITY_API_KEY")
    LIGHTHOUSE_API_KEY: str = os.getenv("LIGHTHOUSE_API_KEY")
    
    # Otras configuraciones
    PORT: int = int(os.getenv("PORT", "8000"))
    
    def validate(self):
        """Validar que todas las configuraciones requeridas estén presentes."""
        missing_vars = []
        
        # Verificar API keys requeridas
        if not self.OPENAI_API_KEY:
            missing_vars.append("OPENAI_API_KEY")
        if not self.STABILITY_API_KEY:
            missing_vars.append("STABILITY_API_KEY")
        if not self.LIGHTHOUSE_API_KEY:
            missing_vars.append("LIGHTHOUSE_API_KEY")
        
        if missing_vars:
            error_msg = (
                f"Faltan las siguientes variables de entorno requeridas: {', '.join(missing_vars)}\n"
                f"Por favor, configura estas variables en Railway o en el archivo .env\n"
                f"Variables de entorno encontradas: {list(os.environ.keys())}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

# Crear instancia de configuración
settings = Settings()

# Validar configuración
try:
    settings.validate()
    logger.info("Configuración validada exitosamente")
except ValueError as e:
    logger.error(f"Error de configuración: {str(e)}")
    raise
