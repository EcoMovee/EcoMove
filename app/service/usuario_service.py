from app.domain.usuario_domain import Usuario
from app.repository.usuario_repository import UsuarioRepository
import bcrypt
import re
from datetime import datetime, date, timedelta
from app.core.constants import ErrorCodes
from app.core.security import verify_password, create_access_token

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
            estado=True
        )
        
        # Determinar rol basado en el correo
        if correo == "admin@ecomove.com":
            usuario.rol = "administrador"
        else:
            usuario.rol = "usuario"
        
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
        usuario = self.repository.get_by_id(user_id)
        
        if not usuario:
            raise ValueError(ErrorCodes.USER_NOT_FOUND)
        
        if telefono:
            self._validate_phone(telefono)
        
        if nombre:
            if len(nombre.strip()) < 2:
                raise ValueError("El nombre debe tener al menos 2 caracteres")
            usuario.nombre = nombre.strip()
        
        if telefono:
            usuario.telefono = telefono
        
        if nueva_contrasena:
            if not contrasena_actual:
                raise ValueError("Debe proporcionar la contraseña actual para cambiarla")
            
            if not verify_password(contrasena_actual, usuario.contrasena_hash):
                raise ValueError(ErrorCodes.INVALID_CURRENT_PASSWORD)
            
            self._validate_password(nueva_contrasena)
            
            salt = bcrypt.gensalt(rounds=10)
            usuario.contrasena_hash = bcrypt.hashpw(nueva_contrasena.encode('utf-8'), salt).decode('utf-8')
        
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
        if not re.match(r'^\+\d{1,3}\d{7,15}$', phone):
            raise ValueError("El teléfono debe tener código de país y entre 7 y 15 dígitos. Ejemplo: +573001234567")
    
    def _validate_age(self, birth_date_str: str) -> date:
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
            # ========== HU-004: DESACTIVAR USUARIO ==========
    def desactivar_usuario(self, admin_id: int, user_id: int, motivo: str = None) -> dict:
        from datetime import datetime
        
        admin = self.repository.get_by_id(admin_id)
        if not admin or admin.rol != "administrador":
            raise ValueError("ADMIN_REQUIRED")
        
        if admin_id == user_id:
            raise ValueError("CANNOT_DESACTIVATE_SELF")
        
        usuario = self.repository.get_by_id(user_id)
        if not usuario:
            raise ValueError("USER_NOT_FOUND")
        
        if not usuario.estado:
            raise ValueError("USER_ALREADY_INACTIVE")
        
        estado_anterior = usuario.estado
        usuario.estado = False
        self.repository.update(user_id, usuario)
        
        return {
            "usuario_id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.correo,
            "estado_anterior": estado_anterior,
            "estado_nuevo": False,
            "fecha_desactivacion": datetime.now().isoformat()
        }