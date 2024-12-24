#!/bin/bash

echo "Iniciando script de arranque..."

# Verificar que el modelo existe
if [ ! -f "/root/.u2net/u2net.onnx" ]; then
    echo "Error: Modelo rembg no encontrado"
    exit 1
fi

# Verificar variables de entorno requeridas
if [ -z "$PORT" ]; then
    echo "Usando puerto por defecto 8080"
    PORT=8080
fi

# Activar el entorno virtual
source /opt/venv/bin/activate

# Iniciar la aplicación
echo "Iniciando aplicación en puerto $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 120 --workers 1 --timeout 300 --log-level debug 