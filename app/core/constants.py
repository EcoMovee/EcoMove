class VehicleTypes:
    CARRO = "carro"
    MOTO = "moto"
    BICICLETA = "bicicleta"
    ALLOWED = [CARRO, MOTO, BICICLETA]

class VehicleConfig:
    TARIFA_MINIMA = 0.01
    MODELO_MIN_LENGTH = 3
    UBICACION_MIN_LENGTH = 3
    NIVEL_BATERIA_DEFAULT = 100

class HttpStatus:
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    SERVICE_UNAVAILABLE = 503

class ErrorMessages:
    INVALID_VEHICLE_TYPE = "El tipo debe ser carro, moto o bicicleta"
    INVALID_TARIFA = "La tarifa por hora debe ser mayor a 0"
    VEHICLE_ALREADY_EXISTS = "El vehículo ya está registrado"
    UNAUTHORIZED = "Token no proporcionado"
    FORBIDDEN = "Acceso denegado. Se requieren privilegios de administrador"
    DB_CONNECTION_ERROR = "Error de conexión a la base de datos"
    MODELO_REQUIRED = "El modelo es obligatorio"
    UBICACION_REQUIRED = "La ubicación es obligatoria"

class ErrorCodes:
    INVALID_DATA = "INVALID_DATA"
    VEHICLE_ALREADY_EXISTS = "VEHICLE_ALREADY_EXISTS"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    DB_CONNECTION_ERROR = "DB_CONNECTION_ERROR"

class SuccessMessages:
    VEHICLE_CREATED = "Vehículo creado correctamente"