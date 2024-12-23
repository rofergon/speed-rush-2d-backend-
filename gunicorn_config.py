import multiprocessing

# Configuración del servidor
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5

# Configuración de logging
accesslog = "-"
errorlog = "-"
loglevel = "info" 