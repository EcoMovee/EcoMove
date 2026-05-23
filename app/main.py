from fastapi import FastAPI
from app.api.v1.vehiculo_router import router as vehiculo_router
from app.api.v1.usuario_router import router as usuario_router
from database.database import init_db

# Inicializar base de datos
init_db()

app = FastAPI(
    title="EcoMove API",
    description="API REST para gestión de vehículos eléctricos y usuarios",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Incluir routers
app.include_router(vehiculo_router, prefix="/api/v1")
app.include_router(usuario_router)

@app.get("/")
def root():
    return {
        "success": True,
        "message": "Bienvenido a EcoMove API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "usuarios": "/api/v1/usuarios",
            "vehiculos": "/api/v1/vehiculos"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "EcoMove API"}