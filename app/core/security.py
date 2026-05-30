from datetime import datetime, timedelta
from jose import jwt
import bcrypt
import os

SECRET_KEY = os.getenv("JWT_SECRET", "tu-clave-secreta-muy-segura-cambiarla-en-produccion-minimo-32-caracteres")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # 2 horas

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash usando bcrypt"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """Crea un token JWT con expiración de 2 horas"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decodifica un token JWT (para pruebas)"""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])