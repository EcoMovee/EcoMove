from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from app.services.usuario_service import UsuarioService
from app.core.constants import ErrorCodes, HttpStatus

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
service = UsuarioService()

# Modelo Pydantic para el request body
class RegistroUsuarioRequest(BaseModel):
    nombre: str
    correo: str
    contrasena: str
    telefono: str
    fecha_nacimiento: Optional[str] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def registrar_usuario(usuario_data: RegistroUsuarioRequest):
    """Registrar un nuevo usuario en el sistema"""
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