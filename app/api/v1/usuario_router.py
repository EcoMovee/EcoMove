from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from service.usuario_service import UsuarioService
from core.constants import ErrorCodes, HttpStatus
from core.dependencies import get_current_user
from app.service.usuario_service import UsuarioService
from app.core.constants import ErrorCodes, HttpStatus
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["Usuarios"])
service = UsuarioService()

# ========== MODELOS ==========
class RegistroUsuarioRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    correo: str = Field(...)
    contrasena: str = Field(..., min_length=8)
    telefono: str = Field(...)
    fecha_nacimiento: Optional[str] = None

class LoginRequest(BaseModel):
    email: str = Field(...)
    password: str = Field(...)

class ActualizarPerfilRequest(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    telefono: Optional[str] = None
    contrasena_actual: Optional[str] = None
    nueva_contrasena: Optional[str] = None

# NUEVO MODELO PARA HU-004
class DesactivarUsuarioRequest(BaseModel):
    motivo: Optional[str] = Field(None, description="Motivo de la desactivación")


# ========== ENDPOINTS ==========
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


@router.post("/usuarios/login")
async def login(login_data: LoginRequest):
    try:
        resultado = service.login(
            email=login_data.email,
            password=login_data.password
        )
        return {
            "success": True,
            "statusCode": HttpStatus.OK,
            "message": "Inicio de sesión exitoso",
            "data": resultado
        }
    except ValueError as e:
        error_msg = str(e)
        
        if error_msg.startswith(ErrorCodes.ACCOUNT_BLOCKED):
            partes = error_msg.split("|")
            minutos_restantes = int(partes[1]) if len(partes) > 1 else 15
            return JSONResponse(
                status_code=HttpStatus.FORBIDDEN,
                content={
                    "success": False,
                    "statusCode": HttpStatus.FORBIDDEN,
                    "message": "Cuenta bloqueada por múltiples intentos fallidos",
                    "data": {"minutos_restantes": minutos_restantes}
                }
            )
        
        if error_msg.startswith(ErrorCodes.INVALID_CREDENTIALS):
            partes = error_msg.split("|")
            intentos_restantes = int(partes[1]) if len(partes) > 1 else None
            response = {
                "success": False,
                "statusCode": HttpStatus.UNAUTHORIZED,
                "message": "Credenciales inválidas"
            }
            if intentos_restantes is not None:
                response["intentos_restantes"] = intentos_restantes
            return JSONResponse(
                status_code=HttpStatus.UNAUTHORIZED,
                content=response
            )
        
        if error_msg == ErrorCodes.USER_INACTIVE:
            return JSONResponse(
                status_code=HttpStatus.UNAUTHORIZED,
                content={
                    "success": False,
                    "statusCode": HttpStatus.UNAUTHORIZED,
                    "message": "Usuario desactivado. Contacte al administrador"
                }
            )
        
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Error en el inicio de sesión",
                "error": {
                    "code": ErrorCodes.INVALID_DATA,
                    "details": error_msg
                }
            }
        )


@router.put("/usuarios/{id}")
async def actualizar_perfil(
    id: int,
    perfil_data: ActualizarPerfilRequest,
    current_user_id: int = Depends(get_current_user)
):
    if current_user_id != id:
        return JSONResponse(
            status_code=HttpStatus.FORBIDDEN,
            content={
                "success": False,
                "statusCode": HttpStatus.FORBIDDEN,
                "message": "No tiene permiso para modificar este usuario"
            }
        )
    
    try:
        resultado = service.actualizar_perfil(
            user_id=id,
            nombre=perfil_data.nombre,
            telefono=perfil_data.telefono,
            contrasena_actual=perfil_data.contrasena_actual,
            nueva_contrasena=perfil_data.nueva_contrasena
        )
        return {
            "success": True,
            "statusCode": HttpStatus.OK,
            "message": "Usuario actualizado correctamente",
            "data": resultado
        }
    except ValueError as e:
        error_msg = str(e)
        
        if error_msg == ErrorCodes.USER_NOT_FOUND:
            return JSONResponse(
                status_code=HttpStatus.NOT_FOUND,
                content={
                    "success": False,
                    "statusCode": HttpStatus.NOT_FOUND,
                    "message": "Usuario no encontrado",
                    "error": {
                        "code": "USER_NOT_FOUND",
                        "details": "No existe un usuario con el ID proporcionado"
                    }
                }
            )
        
        if error_msg == ErrorCodes.INVALID_CURRENT_PASSWORD:
            return JSONResponse(
                status_code=HttpStatus.BAD_REQUEST,
                content={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "Contraseña actual incorrecta",
                    "error": {
                        "code": "INVALID_CURRENT_PASSWORD",
                        "details": "La contraseña actual no coincide con nuestros registros"
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


# ========== HU-004: DESACTIVAR USUARIO ==========
@router.patch("/usuarios/estado/{id}")
async def desactivar_usuario(
    id: int,
    request_data: DesactivarUsuarioRequest = None,
    current_user_id: int = Depends(get_current_user)
):
    """
    Desactiva un usuario (solo administradores).
    
    - Solo administradores pueden ejecutar esta acción
    - No permite desactivarse a sí mismo
    - Valida que el usuario exista y esté activo
    - Valida que no sea el último administrador activo
    - Valida que no tenga reservas activas
    """
    motivo = request_data.motivo if request_data else None
    
    try:
        resultado = service.desactivar_usuario(
            admin_id=current_user_id,
            user_id=id,
            motivo=motivo
        )
        return {
            "success": True,
            "statusCode": HttpStatus.OK,
            "message": "Usuario desactivado exitosamente",
            "data": resultado
        }
    except ValueError as e:
        error_msg = str(e)
        
        if error_msg == ErrorCodes.ADMIN_REQUIRED:
            return JSONResponse(
                status_code=HttpStatus.FORBIDDEN,
                content={
                    "success": False,
                    "statusCode": HttpStatus.FORBIDDEN,
                    "message": "Acceso denegado. Se requieren privilegios de administrador",
                    "error": {
                        "code": "ADMIN_REQUIRED",
                        "details": "Solo los administradores pueden desactivar usuarios"
                    }
                }
            )
        
        if error_msg == ErrorCodes.CANNOT_DESACTIVATE_SELF:
            return JSONResponse(
                status_code=HttpStatus.FORBIDDEN,
                content={
                    "success": False,
                    "statusCode": HttpStatus.FORBIDDEN,
                    "message": "No puede desactivarse a sí mismo",
                    "error": {
                        "code": "CANNOT_DESACTIVATE_SELF",
                        "details": "Un administrador no puede desactivar su propia cuenta"
                    }
                }
            )
        
        if error_msg == ErrorCodes.USER_NOT_FOUND:
            return JSONResponse(
                status_code=HttpStatus.NOT_FOUND,
                content={
                    "success": False,
                    "statusCode": HttpStatus.NOT_FOUND,
                    "message": "Usuario no encontrado",
                    "error": {
                        "code": "USER_NOT_FOUND",
                        "details": "No existe un usuario con el ID proporcionado"
                    }
                }
            )
        
        if error_msg == ErrorCodes.USER_ALREADY_INACTIVE:
            return JSONResponse(
                status_code=HttpStatus.BAD_REQUEST,
                content={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "El usuario ya está inactivo",
                    "error": {
                        "code": "USER_ALREADY_INACTIVE",
                        "details": f"El usuario con ID {id} ya se encuentra desactivado"
                    }
                }
            )
        
        if error_msg == ErrorCodes.LAST_ADMIN_CANNOT_BE_DEACTIVATED:
            return JSONResponse(
                status_code=HttpStatus.FORBIDDEN,
                content={
                    "success": False,
                    "statusCode": HttpStatus.FORBIDDEN,
                    "message": "No se puede desactivar al único administrador activo",
                    "error": {
                        "code": "LAST_ADMIN_CANNOT_BE_DEACTIVATED",
                        "details": "El sistema debe tener al menos un administrador activo"
                    }
                }
            )
        
        if error_msg == ErrorCodes.USER_HAS_ACTIVE_RESERVATIONS:
            return JSONResponse(
                status_code=HttpStatus.BAD_REQUEST,
                content={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "No se puede desactivar un usuario con reservas activas",
                    "error": {
                        "code": "USER_HAS_ACTIVE_RESERVATIONS",
                        "details": "El usuario tiene reservas en curso. Cancélelas antes de desactivar."
                    }
                }
            )
        
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Error al desactivar usuario",
                "error": {
                    "code": ErrorCodes.INVALID_DATA,
                    "details": error_msg
                }
            }
        )
@router.get("/debug/usuarios")
async def debug_usuarios():
    from repository.usuario_repository import UsuarioRepository
    repo = UsuarioRepository()
    return {
        "usuarios": [
            {"id": u.id, "email": u.correo, "rol": u.rol, "estado": u.estado}
            for u in repo._usuarios
        ]
    }    