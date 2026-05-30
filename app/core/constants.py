class ErrorCodes:
    """Códigos de error del sistema"""
    EMAIL_EXISTS = "EMAIL_EXISTS"
    INVALID_DATA = "INVALID_DATA"
    INVALID_EMAIL = "INVALID_EMAIL"
    INVALID_PASSWORD = "INVALID_PASSWORD"
    INVALID_PHONE = "INVALID_PHONE"
    UNDERAGE_USER = "UNDERAGE_USER"

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

class SuccessMessages:
    """Mensajes de éxito"""
    USER_CREATED = "Usuario creado correctamente"