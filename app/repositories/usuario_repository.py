# app/repositories/usuario_repository.py
from typing import List, Optional
from database.database import get_db_context
from domain.usuario_domain import Usuario

class UsuarioRepository:
    
    def create(self, usuario: Usuario) -> Usuario:
        """Crear un nuevo usuario en la base de datos"""
        with get_db_context() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usuarios 
                (nombre, correo, telefono, contrasena_hash, rol, estado, fecha_nacimiento)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                usuario.nombre,
                usuario.correo.lower(),  # Normalizar email a minúsculas
                usuario.telefono,
                usuario.contrasena_hash,
                usuario.rol,
                usuario.estado,
                usuario.fecha_nacimiento
            ))
            usuario.id = cursor.lastrowid
            return usuario
    
    def get_by_email(self, correo: str) -> Optional[Usuario]:
        """Obtener usuario por email (normalizado a minúsculas)"""
        with get_db_context() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE correo = ?', (correo.lower(),))
            row = cursor.fetchone()
            if row:
                return self._row_to_usuario(row)
            return None
    
    def get_by_id(self, id: int) -> Optional[Usuario]:
        """Obtener usuario por ID"""
        with get_db_context() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE id = ?', (id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_usuario(row)
            return None
    
    def _row_to_usuario(self, row) -> Usuario:
        """Convertir fila de BD a objeto Usuario"""
        return Usuario(
            id=row['id'],
            nombre=row['nombre'],
            correo=row['correo'],
            telefono=row['telefono'],
            contrasena_hash=row['contrasena_hash'],
            rol=row['rol'],
            estado=bool(row['estado']),
            fecha_registro=row['fecha_registro'],
            intentos_fallidos=row['intentos_fallidos'],
            bloqueado_hasta=row['bloqueado_hasta'],
            fecha_nacimiento=row['fecha_nacimiento']
        )