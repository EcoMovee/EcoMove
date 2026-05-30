from fastapi import FastAPI
from api.v1.usuario_router import router

app = FastAPI(
    title="EcoMove API",
    description="API para el sistema de movilidad sostenible EcoMove",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "success": True,
        "message": "Bienvenido a EcoMove API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "EcoMove API"}