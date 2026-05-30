from typing import List, Optional
from domain.usuario_domain import Usuario
from datetime import datetime

class UsuarioRepository:
    def __init__(self):
        self._usuarios: List[Usuario] = []
        self._counter = 1
    
    def create(self, usuario: Usuario) -> Usuario:
        """Crear un nuevo usuario en la base de datos en memoria"""
        usuario.id = self._counter
        self._counter += 1
        self._usuarios.append(usuario)
        return usuario
    
    def get_by_email(self, correo: str) -> Optional[Usuario]:
        """Obtener usuario por email (case-insensitive)"""
        for usuario in self._usuarios:
            if usuario.correo == correo.lower():
                return usuario
        return None
    
    def get_by_id(self, id: int) -> Optional[Usuario]:
        """Obtener usuario por ID"""
        for usuario in self._usuarios:
            if usuario.id == id:
                return usuario
        return None
    
    # HU-002: métodos para control de intentos fallidos
    def update_intentos_fallidos(self, user_id: int, intentos: int) -> None:
        """Actualiza el contador de intentos fallidos"""
        for usuario in self._usuarios:
            if usuario.id == user_id:
                usuario.intentos_fallidos = intentos
                break
    
    def update_bloqueo(self, user_id: int, bloqueado_hasta: Optional[datetime]) -> None:
        """Actualiza la fecha de bloqueo del usuario"""
        for usuario in self._usuarios:
            if usuario.id == user_id:
                usuario.bloqueado_hasta = bloqueado_hasta
                break
    
    def reset_intentos_y_bloqueo(self, user_id: int) -> None:
        """Resetea intentos fallidos y elimina bloqueo"""
        for usuario in self._usuarios:
            if usuario.id == user_id:
                usuario.intentos_fallidos = 0
                usuario.bloqueado_hasta = None
                break