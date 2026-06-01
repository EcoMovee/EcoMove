from fastapi import FastAPI
from app.api.v1.vehiculo_router import router as vehiculo_router
from app.core.security import create_access_token

app = FastAPI(
    title="EcoMove API - HU-005",
    description="Prueba de registro de vehículos",
    version="1.0.0"
)

app.include_router(vehiculo_router)

@app.get("/")
def root():
    return {"message": "EcoMove API - HU-005 funcionando 🚀"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "EcoMove - HU-005"}