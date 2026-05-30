from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from service.usuario_service import UsuarioService
from core.constants import ErrorCodes, HttpStatus

router = APIRouter(prefix="/api/v1", tags=["Usuarios"])
service = UsuarioService()

class RegistroUsuarioRequest(BaseModel):
    nombre: str
    correo: str
    contrasena: str
    telefono: str
    fecha_nacimiento: Optional[str] = None

@router.post("/usuarios", status_code=status.HTTP_201_CREATED)
async def registrar_usuario(usuario_data: RegistroUsuarioRequest):
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
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Datos inválidos",
                "error": {"code": ErrorCodes.INVALID_DATA, "details": str(e)}
            }
        )