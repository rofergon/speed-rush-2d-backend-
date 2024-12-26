#!/bin/bash

# Función para verificar variable de entorno
check_env_var() {
    if [ -z "${!1}" ]; then
        echo "Error: La variable de entorno $1 no está configurada"
        exit 1
    fi
}

echo "Iniciando script de arranque..."

# Mostrar información del sistema
echo "Contenido del directorio actual:"
ls -la

echo "Estructura del proyecto:"
tree -L 2

echo "Variables de entorno disponibles:"
env | grep -v "KEY"

# Verificar variables de entorno requeridas
echo "Verificando variables de entorno..."
check_env_var "OPENAI_API_KEY"
check_env_var "STABILITY_API_KEY"
check_env_var "LIGHTHOUSE_API_KEY"

echo "Todas las variables de entorno requeridas están configuradas"

echo "Python path:"
echo $PYTHONPATH

echo "Verificando instalación de Python:"
which python3
python3 --version

echo "Verificando módulos instalados:"
pip list

# Iniciar la aplicación
echo "Iniciando aplicación..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --log-level debug 