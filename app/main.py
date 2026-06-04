from fastapi import FastAPI
from api.v1.usuario_router import router as usuario_router
from api.v1.vehiculo_router import router as vehiculo_router
from api.v1.reserva_router import router as reserva_router
from repository.usuario_repository import UsuarioRepository
import bcrypt
from domain.usuario_domain import Usuario
from app.api.v1.usuario_router import router as usuario_router
from app.api.v1.vehiculo_router import router as vehiculo_router
from app.repository.usuario_repository import UsuarioRepository
import bcrypt
from app.domain.usuario_domain import Usuario

app = FastAPI(
    title="EcoMove API",
    description="API para el sistema de movilidad sostenible EcoMove",
    version="1.0.0"
)

app.include_router(usuario_router, prefix="/api/v1")
app.include_router(vehiculo_router, prefix="/api/v1")
app.include_router(reserva_router)

# ========== CREAR ADMINISTRADOR INICIAL ==========
repo = UsuarioRepository()

# Verificar si ya existe
admin_existe = False
for u in repo._usuarios:
    if u.correo == "admin@ecomove.com":
        admin_existe = True
        print(f"✅ Administrador ya existe: {u.correo}")
        break

if not admin_existe:
    hashed = bcrypt.hashpw("Admin123!".encode('utf-8'), bcrypt.gensalt())
    admin = Usuario(
        nombre="Administrador",
        correo="admin@ecomove.com",
        telefono="+573001234567",
        contrasena_hash=hashed.decode('utf-8'),
        rol="administrador",
        estado=True
    )
    repo.create(admin)
    print("✅ Administrador creado: admin@ecomove.com / Contraseña: Admin123!")

# ========== FIN ADMIN ==========

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