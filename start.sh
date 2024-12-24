#!/bin/bash

echo "Iniciando script de arranque..."

# Función para manejar errores
handle_error() {
    echo "Error: $1"
    exit 1
}

# Crear directorio para el modelo si no existe
mkdir -p /root/.u2net || handle_error "No se pudo crear el directorio del modelo"

# Verificar si el modelo ya existe
if [ ! -f "/root/.u2net/u2net.onnx" ]; then
    echo "Descargando modelo rembg..."
    # Descargar el modelo usando curl con reintentos
    curl -L --retry 3 --retry-delay 5 -o /root/.u2net/u2net.onnx https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx || handle_error "No se pudo descargar el modelo"
    echo "Modelo descargado exitosamente"
else
    echo "El modelo ya existe, verificando integridad..."
    # Verificar tamaño del archivo (el modelo debe ser mayor a 100MB)
    file_size=$(stat -f%z "/root/.u2net/u2net.onnx" 2>/dev/null || stat -c%s "/root/.u2net/u2net.onnx")
    if [ "$file_size" -lt 100000000 ]; then
        echo "El modelo parece estar corrupto, reintentando descarga..."
        rm -f /root/.u2net/u2net.onnx
        curl -L --retry 3 --retry-delay 5 -o /root/.u2net/u2net.onnx https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx || handle_error "No se pudo descargar el modelo"
    else
        echo "Modelo verificado correctamente"
    fi
fi

# Verificar variables de entorno requeridas
if [ -z "$PORT" ]; then
    echo "Usando puerto por defecto 8080"
    PORT=8080
fi

# Iniciar la aplicación
echo "Iniciando aplicación en puerto $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 120 --workers 1 --timeout 300 --log-level debug 