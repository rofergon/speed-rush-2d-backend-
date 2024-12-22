from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import car_generation

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
    return {"message": "Bienvenido a Speed Rush 2D Car Generator API"}
