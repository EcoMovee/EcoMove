class ErrorCodes:
    """Códigos de error del sistema"""
    # HU-001
    EMAIL_EXISTS = "EMAIL_EXISTS"
    INVALID_DATA = "INVALID_DATA"
    INVALID_EMAIL = "INVALID_EMAIL"
    INVALID_PASSWORD = "INVALID_PASSWORD"
    INVALID_PHONE = "INVALID_PHONE"
    UNDERAGE_USER = "UNDERAGE_USER"
    
    # HU-002
    USER_NOT_FOUND = "USER_NOT_FOUND"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCOUNT_BLOCKED = "ACCOUNT_BLOCKED"
    USER_INACTIVE = "USER_INACTIVE"

class HttpStatus:
    """Códigos HTTP"""
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500

class ErrorMessages:
    """Mensajes de error"""
    EMAIL_EXISTS = "El email ya está registrado"
    INVALID_DATA = "Datos inválidos"
    USER_NOT_FOUND = "Usuario no encontrado"

class SuccessMessages:
    """Mensajes de éxito"""
    USER_CREATED = "Usuario creado correctamente"
    LOGIN_SUCCESS = "Inicio de sesión exitoso"