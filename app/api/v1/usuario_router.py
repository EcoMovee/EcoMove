from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from service.usuario_service import UsuarioService
from core.constants import ErrorCodes, HttpStatus

router = APIRouter(prefix="/api/v1", tags=["Usuarios"])
service = UsuarioService()

class RegistroUsuarioRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo del usuario")
    correo: str = Field(..., description="Correo electrónico (debe ser único)")
    contrasena: str = Field(..., min_length=8, description="Contraseña (mínimo 8 caracteres, mayúscula, número, carácter especial)")
    telefono: str = Field(..., description="Teléfono con código de país, ej: +573001234567")
    fecha_nacimiento: Optional[str] = Field(None, description="Fecha de nacimiento (YYYY-MM-DD) para validar mayoría de edad")

@router.post("/usuarios", status_code=status.HTTP_201_CREATED)
async def registrar_usuario(usuario_data: RegistroUsuarioRequest):
    """
    Registra un nuevo usuario en el sistema.
    
    Validaciones:
    - Nombre: mínimo 2 caracteres
    - Correo: formato válido y único
    - Contraseña: mínimo 8 caracteres, al menos una mayúscula, un número y un carácter especial
    - Teléfono: código de país + 7-15 dígitos
    - Fecha de nacimiento: mayor de 18 años
    """
    try:
        nuevo_usuario = service.register(
            nombre=usuario_data.nombre,
            correo=usuario_data.correo,
            contrasena=usuario_data.contrasena,
            telefono=usuario_data.telefono,
            fecha_nacimiento=usuario_data.fecha_nacimiento
        )
        
        return {
            "success": True,
            "statusCode": HttpStatus.CREATED,
            "message": "Usuario creado correctamente",
            "data": {
                "id": nuevo_usuario.id,
                "nombre": nuevo_usuario.nombre,
                "email": nuevo_usuario.correo,
                "telefono": nuevo_usuario.telefono
            }
        }
    
    except ValueError as e:
        error_msg = str(e)
        
        if error_msg == ErrorCodes.EMAIL_EXISTS:
            return JSONResponse(
                status_code=HttpStatus.BAD_REQUEST,
                content={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "El email ya está registrado",
                    "error": {
                        "code": ErrorCodes.EMAIL_EXISTS,
                        "details": f"El email {usuario_data.correo} ya existe en el sistema"
                    }
                }
            )
        
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Datos inválidos",
                "error": {
                    "code": ErrorCodes.INVALID_DATA,
                    "details": error_msg
                }
            }
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=HttpStatus.INTERNAL_ERROR,
            content={
                "success": False,
                "statusCode": HttpStatus.INTERNAL_ERROR,
                "message": "Error interno del servidor",
                "error": {
                    "code": "INTERNAL_ERROR",
                    "details": str(e)
                }
            }
        )