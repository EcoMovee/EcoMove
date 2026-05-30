from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

# Configuración (en producción, usar variables de entorno)
SECRET_KEY = "tu-secret-key-muy-segura-cambiar-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 días

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Crear un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifica que el token sea válido (cualquier usuario autenticado).
    No verifica rol específico.
    Retorna el payload del token si es válido.
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "statusCode": 401,
                "message": "No autenticado",
                "error": {
                    "code": "UNAUTHORIZED",
                    "details": "Token expirado"
                }
            }
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "statusCode": 401,
                "message": "No autenticado",
                "error": {
                    "code": "UNAUTHORIZED",
                    "details": "Token no válido"
                }
            }
        )


def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifica que el usuario sea administrador.
    Retorna el payload del token si es admin, lanza error si no.
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("rol") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "success": False,
                    "statusCode": 403,
                    "message": "Acceso denegado. Se requieren privilegios de administrador",
                    "error": {
                        "code": "FORBIDDEN",
                        "details": "Solo administradores pueden realizar esta acción"
                    }
                }
            )
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "statusCode": 401,
                "message": "Token expirado",
                "error": {
                    "code": "UNAUTHORIZED",
                    "details": "El token ha expirado"
                }
            }
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "statusCode": 401,
                "message": "Token inválido",
                "error": {
                    "code": "UNAUTHORIZED",
                    "details": "El token no es válido"
                }
            }
        )