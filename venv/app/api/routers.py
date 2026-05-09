from fastapi import APIRouter

# Crear un router
router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": "development"
    }

@router.get("/")
async def root():
    return {"message": "Bienvenido a EcoMove API"}

@router.get("/vehiculos")
async def get_vehiculos():
    return {"vehiculos": []}

@router.post("/vehiculos")
async def create_vehiculo():
    return {"message": "Vehículo creado", "id": 1}