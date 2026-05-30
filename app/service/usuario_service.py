from domain.usuario_domain import Usuario
from repository.usuario_repository import UsuarioRepository
import bcrypt
import re
from datetime import datetime, date
from core.constants import ErrorCodes

class UsuarioService:
    def __init__(self):
        self.repository = UsuarioRepository()
    
    def register(self, nombre: str, correo: str, contrasena: str, telefono: str, fecha_nacimiento: str = None) -> Usuario:
        """
        Registra un nuevo usuario.
        
        Validaciones:
        - Email único (normalizado a minúsculas)
        - Contraseña: 8+ chars, mayúscula, número, carácter especial
        - Teléfono: +código país + 7-15 dígitos
        - Edad: mayor de 18 años
        """
        
        # Normalizar email a minúsculas
        correo = correo.lower().strip()
        
        # 1. Validar que el email no esté registrado
        existing_user = self.repository.get_by_email(correo)
        if existing_user:
            raise ValueError(ErrorCodes.EMAIL_EXISTS)
        
        # 2. Validar contraseña
        self._validate_password(contrasena)
        
        # 3. Validar teléfono
        self._validate_phone(telefono)
        
        # 4. Validar edad (mayor de 18)
        edad_validada = None
        if fecha_nacimiento:
            edad_validada = self._validate_age(fecha_nacimiento)
        
        # 5. Encriptar contraseña con bcrypt (saltRounds=10)
        salt = bcrypt.gensalt(rounds=10)
        hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), salt)
        
        # 6. Crear objeto usuario
        usuario = Usuario(
            nombre=nombre.strip(),
            correo=correo,
            telefono=telefono,
            contrasena_hash=hashed_password.decode('utf-8'),
            fecha_nacimiento=edad_validada,
            rol="usuario",
            estado=True
        )
        
        # 7. Guardar en base de datos
        return self.repository.create(usuario)
    
    def _validate_password(self, password: str) -> None:
        """Validar requisitos de contraseña según documentación"""
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
            if isinstance(birth_date_str, str):
                birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            else:
                birth_date = birth_date_str
            
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if age < 18:
                raise ValueError("Debes ser mayor de 18 años para registrarte")
            
            return birth_date
        except ValueError as e:
            if "mayor de 18" in str(e):
                raise
            raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")