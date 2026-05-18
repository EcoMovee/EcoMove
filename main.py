from fastapi import FastAPI
from api.vehiculo_router import router

app = FastAPI(
    title="EcoMove API",
    description="API REST para gestión de vehículos eléctricos",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "¡EcoMove API funcionando! 🚀"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "EcoMove API"}