import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Obtener la ruta base del proyecto (donde está el .env)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / '.env'

print(f"Buscando archivo .env en: {ENV_FILE}")
print(f"El archivo existe: {ENV_FILE.exists()}")

# Intentar cargar .env de múltiples formas
dotenv_path = find_dotenv()
print(f"Dotenv encontrado en: {dotenv_path}")

# Cargar variables de entorno
load_dotenv(ENV_FILE)

# Imprimir todas las variables de entorno (sin mostrar valores sensibles)
print("Variables de entorno cargadas:")
for key in os.environ:
    if 'KEY' in key:
        print(f"{key}=***[HIDDEN]***")
    else:
        print(f"{key}={os.environ[key]}")

# Configuración
class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise Exception(
            f"No se encontró OPENAI_API_KEY en las variables de entorno.\n"
            f"Archivo .env buscado en: {ENV_FILE}\n"
            f"Archivo existe: {ENV_FILE.exists()}\n"
            f"Contenido del directorio:\n"
            f"{[f.name for f in BASE_DIR.iterdir()]}"
        )

settings = Settings()
