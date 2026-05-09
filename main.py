from fastapi import FastAPI
from app.api.routers import router

# Crear la aplicación
app = FastAPI(
    title="EcoMove API",
    description="API para el sistema EcoMove",
    version="1.0.0"
)

# Incluir las rutas del router
app.include_router(router)