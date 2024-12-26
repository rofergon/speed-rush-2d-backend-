#!/bin/bash

# Función para verificar variable de entorno
check_env_var() {
    if [ -z "${!1}" ]; then
        echo "Error: La variable de entorno $1 no está configurada"
        exit 1
    fi
}

# Verificar variables de entorno requeridas
echo "Verificando variables de entorno..."
check_env_var "OPENAI_API_KEY"
check_env_var "STABILITY_API_KEY"
check_env_var "LIGHTHOUSE_API_KEY"

echo "Todas las variables de entorno requeridas están configuradas"

# Iniciar la aplicación
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" 