"""
Archivo de constantes globales para EcoMove API
"""

# ── Configuración de autenticación ──
# En producción, estas variables deben estar en .env
JWT_SECRET_KEY = "tu-secret-key-aqui-cambiar-en-produccion"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24  # 24 horas

# ── Roles de usuario ──
class UserRoles:
    ADMIN = "admin"
    USER = "user"
    OPERADOR = "operador"

# ── Tipos de vehículo permitidos ──
class VehicleTypes:
    CARRO = "carro"
    MOTO = "moto"
    BICICLETA = "bicicleta"
    
    ALLOWED = [CARRO, MOTO, BICICLETA]

# ── Estados de vehículo ──
class VehicleStatus:
    DISPONIBLE = "disponible"
    EN_USO = "en_uso"
    MANTENIMIENTO = "mantenimiento"
    
    ALLOWED = [DISPONIBLE, EN_USO, MANTENIMIENTO]

# ── Configuración de vehículos ──
class VehicleConfig:
    NIVEL_BATERIA_DEFAULT = 100
    TARIFA_MINIMA = 0.01
    MODELO_MIN_LENGTH = 3
    UBICACION_MIN_LENGTH = 3

# ── Mensajes de error ──
class ErrorMessages:
    # Vehículos
    VEHICLE_NOT_FOUND = "Vehículo no encontrado"
    VEHICLE_ALREADY_EXISTS = "El vehículo ya está registrado"
    INVALID_VEHICLE_TYPE = f"El tipo debe ser uno de: {', '.join(VehicleTypes.ALLOWED)}"
    INVALID_TARIFA = "La tarifa por hora debe ser mayor a 0"
    INVALID_STATUS = f"Estado inválido. Permitidos: {', '.join(VehicleStatus.ALLOWED)}"
    MODELO_REQUIRED = "El modelo del vehículo es obligatorio"
    UBICACION_REQUIRED = "La ubicación es obligatoria"
    
    # Autenticación
    UNAUTHORIZED = "Token no proporcionado"
    INVALID_TOKEN = "Token inválido"
    FORBIDDEN = "Acceso denegado. Se requieren privilegios de administrador"
    
    # Base de datos
    DB_CONNECTION_ERROR = "Error de conexión a la base de datos"

# ── Mensajes de éxito ──
class SuccessMessages:
    VEHICLE_CREATED = "Vehículo creado correctamente"
    VEHICLE_DELETED = "Vehículo eliminado correctamente"
    VEHICLE_UPDATED = "Vehículo actualizado correctamente"

# ── Códigos de error ──
class ErrorCodes:
    # Vehículos
    VEHICLE_NOT_FOUND = "VEHICLE_NOT_FOUND"
    VEHICLE_ALREADY_EXISTS = "VEHICLE_ALREADY_EXISTS"
    INVALID_DATA = "INVALID_DATA"
    
    # Autenticación
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    
    # Base de datos
    DB_CONNECTION_ERROR = "DB_CONNECTION_ERROR"

# ── Códigos HTTP ──
class HttpStatus:
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503