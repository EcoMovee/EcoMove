from fastapi import FastAPI
from app.api.v1.pago_router import router as pago_router
from app.database.database import init_db

# Inicializar base de datos
init_db()

app = FastAPI(
    title="EcoMove API",
    description="API REST para procesamiento de pagos",
    version="1.0.0"
)

# Registrar solo el router de pagos
app.include_router(pago_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "EcoMove API - HU-013 Procesamiento de pagos funcionando 🚀"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "EcoMove API"}
