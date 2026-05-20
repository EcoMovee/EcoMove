from fastapi import FastAPI
from app.api.v1.vehiculo_router import router

app = FastAPI(
    title="EcoMove API",
    description="API REST para gestión de vehículos eléctricos",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "¡EcoMove API funcionando! 🚀"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "EcoMove API"}