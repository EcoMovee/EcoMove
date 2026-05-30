from domain.usuario_domain import Usuario
from repository.usuario_repository import UsuarioRepository
import bcrypt
import re
from datetime import datetime, date, timedelta
from core.constants import ErrorCodes
from core.security import verify_password, create_access_token

class UsuarioService:
    def __init__(self):
        self.repository = UsuarioRepository()
    
    # ========== HU-001: REGISTRO ==========
    def register(self, nombre: str, correo: str, contrasena: str, telefono: str, fecha_nacimiento: str = None) -> Usuario:
        correo = correo.lower().strip()
        
        if self.repository.get_by_email(correo):
            raise ValueError(ErrorCodes.EMAIL_EXISTS)
        
        self._validate_password(contrasena)
        self._validate_phone(telefono)
        
        edad_validada = None
        if fecha_nacimiento:
            edad_validada = self._validate_age(fecha_nacimiento)
        
        salt = bcrypt.gensalt(rounds=10)
        hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), salt)
        
        usuario = Usuario(
            nombre=nombre.strip(),
            correo=correo,
            telefono=telefono,
            contrasena_hash=hashed_password.decode('utf-8'),
            fecha_nacimiento=edad_validada,
            rol="usuario",
            estado=True
        )
        
        return self.repository.create(usuario)
    
    # ========== HU-002: LOGIN ==========
    def login(self, email: str, password: str) -> dict:
        email = email.lower().strip()
        usuario = self.repository.get_by_email(email)
        
        if not usuario:
            raise ValueError(ErrorCodes.INVALID_CREDENTIALS)
        
        if not usuario.estado:
            raise ValueError(ErrorCodes.USER_INACTIVE)
        
        if usuario.bloqueado_hasta and usuario.bloqueado_hasta > datetime.now():
            minutos_restantes = int((usuario.bloqueado_hasta - datetime.now()).total_seconds() / 60)
            raise ValueError(f"{ErrorCodes.ACCOUNT_BLOCKED}|{minutos_restantes}")
        
        if not verify_password(password, usuario.contrasena_hash):
            nuevos_intentos = (usuario.intentos_fallidos or 0) + 1
            self.repository.update_intentos_fallidos(usuario.id, nuevos_intentos)
            
            if nuevos_intentos >= 3:
                bloqueado_hasta = datetime.now() + timedelta(minutes=15)
                self.repository.update_bloqueo(usuario.id, bloqueado_hasta)
                raise ValueError(f"{ErrorCodes.ACCOUNT_BLOCKED}|15")
            
            intentos_restantes = 3 - nuevos_intentos
            raise ValueError(f"{ErrorCodes.INVALID_CREDENTIALS}|{intentos_restantes}")
        
        self.repository.reset_intentos_y_bloqueo(usuario.id)
        
        token_data = {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "rol": usuario.rol,
            "email": usuario.correo
        }
        token = create_access_token(token_data)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expira_en_segundos": 7200,
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "email": usuario.correo,
                "rol": usuario.rol
            }
        }
    
    # ========== HU-003: ACTUALIZAR PERFIL ==========
    def actualizar_perfil(self, user_id: int, nombre: str = None, telefono: str = None, 
                          contrasena_actual: str = None, nueva_contrasena: str = None) -> dict:
        """
        Actualiza el perfil del usuario.
        - Permite actualizar nombre y teléfono
        - No permite actualizar email
        - Cambio de contraseña opcional (requiere contraseña actual)
        """
        usuario = self.repository.get_by_id(user_id)
        
        if not usuario:
            raise ValueError(ErrorCodes.USER_NOT_FOUND)
        
        # Validar teléfono si viene
        if telefono:
            self._validate_phone(telefono)
        
        # Actualizar nombre
        if nombre:
            if len(nombre.strip()) < 2:
                raise ValueError("El nombre debe tener al menos 2 caracteres")
            usuario.nombre = nombre.strip()
        
        # Actualizar teléfono
        if telefono:
            usuario.telefono = telefono
        
        # Cambiar contraseña si se proporciona
        if nueva_contrasena:
            if not contrasena_actual:
                raise ValueError("Debe proporcionar la contraseña actual para cambiarla")
            
            if not verify_password(contrasena_actual, usuario.contrasena_hash):
                raise ValueError(ErrorCodes.INVALID_CURRENT_PASSWORD)
            
            # Validar nueva contraseña
            self._validate_password(nueva_contrasena)
            
            # Encriptar nueva contraseña
            salt = bcrypt.gensalt(rounds=10)
            usuario.contrasena_hash = bcrypt.hashpw(nueva_contrasena.encode('utf-8'), salt).decode('utf-8')
        
        # Guardar cambios
        self.repository.update(user_id, usuario)
        
        return {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.correo,
            "telefono": usuario.telefono,
            "rol": usuario.rol
        }
    
    # ========== VALIDACIONES ==========
    def _validate_password(self, password: str) -> None:
        """Validar requisitos de contraseña"""
        errors = []
        if len(password) < 8:
            errors.append("mínimo 8 caracteres")
        if not re.search(r'[A-Z]', password):
            errors.append("al menos una mayúscula")
        if not re.search(r'[0-9]', password):
            errors.append("al menos un número")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("al menos un carácter especial")
        if errors:
            raise ValueError(f"La contraseña debe tener: {', '.join(errors)}")
    
    def _validate_phone(self, phone: str) -> None:
        """Validar formato de teléfono internacional"""
        if not re.match(r'^\+\d{1,3}\d{7,15}$', phone):
            raise ValueError("El teléfono debe tener código de país y entre 7 y 15 dígitos. Ejemplo: +573001234567")
    
    def _validate_age(self, birth_date_str: str) -> date:
        """Validar que el usuario sea mayor de 18 años"""
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                raise ValueError("Debes ser mayor de 18 años para registrarte")
            return birth_date
        except ValueError as e:
            if "mayor de 18" in str(e):
                raise
            raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")