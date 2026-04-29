# [HU-002] Inicio de sesión

## 📖 Historia de Usuario

*Como* usuario registrado de EcoMove,

*Quiero* iniciar sesión con mi email y contraseña,

*Para* acceder a las funcionalidades de la plataforma y obtener un token de autenticación.

## 🔁 Flujo Esperado

- El usuario envía sus credenciales (email y contraseña) al endpoint POST /api/v1/usuarios/login.

- El sistema busca el usuario por email en la tabla usuarios.

- Si el usuario no existe o está inactivo, retorna error genérico.

- Si el usuario está bloqueado por múltiples intentos fallidos, retorna error de bloqueo.

- El sistema compara la contraseña ingresada con el hash almacenado usando bcrypt.

- Si la contraseña es incorrecta, incrementa el contador de intentos fallidos.

- Después de 3 intentos fallidos consecutivos, bloquea la cuenta por 15 minutos.

- Si la contraseña es correcta, resetea el contador de intentos fallidos.

- El sistema genera un token JWT que expira en 2 horas.

- El sistema retorna el token y los datos del usuario.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint POST /api/v1/usuarios/login para la autenticación.

- [ ] Se validan que los campos email y password sean obligatorios.

- [ ] Se busca al usuario por email en la tabla usuarios.

- [ ] Si el usuario no existe, retorna error genérico "Credenciales inválidas" (mismo mensaje que contraseña incorrecta).

- [ ] Si el usuario tiene estado = false, retorna error "Usuario desactivado".

- [ ] Si bloqueado_hasta > NOW(), retorna error de cuenta bloqueada.

- [ ] Se compara la contraseña usando bcrypt.compare().

- [ ] Se implementa un contador de intentos fallidos por usuario.

- [ ] Después de 3 intentos fallidos, se bloquea la cuenta por 15 minutos.

- [ ] Al iniciar sesión exitosamente, se resetea intentos_fallidos = 0 y bloqueado_hasta = NULL.

- [ ] Se genera un token JWT con expiración de 2 horas que incluye id, rol y nombre en el payload.


### 2. 📤 *Estructura de la información*

- [ ] Se responde con la siguiente estructura en JSON para inicio de sesión exitoso:

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Inicio de sesión exitoso",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "usuario": {
      "id": 1,
      "nombre": "Juan Perez",
      "email": "juan@example.com",
      "rol": "usuario"
    },
    "expira_en_segundos": 7200
  }
}
```

- [ ]  Si las credenciales son inválidas, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 401,
  "message": "Credenciales inválidas",
  "intentos_restantes": 2
}
```
- [ ]   Si la cuenta está bloqueada, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 403,
  "message": "Cuenta bloqueada por múltiples intentos fallidos",
  "data": {
    "desbloqueo_en": "2025-01-15T10:30:00Z",
    "minutos_restantes": 15
  }
}
```

- [ ]   Si el usuario está desactivado, el sistema retorna:

```json
{
  "success": false,
  "statusCode": 401,
  "message": "Usuario desactivado. Contacte al administrador"
}
```
## 🔧 Notas Técnicas

### Base de datos (tabla `usuarios`)
- Se requieren las siguientes columnas adicionales a las ya definidas en HU-001:
  - intentos_fallidos: INT, DEFAULT 0
  - bloqueado_hasta: TIMESTAMP, NULLABLE

### Seguridad
- Usar la librería bcrypt con saltRounds = 10 para la comparación de contraseñas (bcrypt.compare()).
- Usar jsonwebtoken (JWT) con algoritmo HS256.
- El secreto JWT debe estar en variable de entorno: JWT_SECRET (mínimo 32 caracteres).
- El payload del token debe incluir: { id, rol, nombre, iat, exp }.
- Tiempo de expiración: 7200 segundos (2 horas).

### Manejo de errores
- El mensaje "Credenciales inválidas" debe ser IDÉNTICO tanto si el email no existe como si la contraseña es incorrecta (por seguridad, para evitar enumeración de usuarios).
- Los códigos de error sugeridos: INVALID_CREDENTIALS, ACCOUNT_BLOCKED, USER_INACTIVE.

## 🚀 Endpoint –  Inicio de sesión

- **Método HTTP:** `POST`

- **Ruta:** `/api/v1/usuarios/login`

📤 Ejemplo de Request JSON

```json
{
  "email": "juan@example.com",
  "password": "Pass123!"
}
```
📤 Ejemplo de Respuesta JSON Exitosa

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Inicio de sesión exitoso",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwicm9sIjoidXN1YXJpbyIsIm5vbWJyZSI6Ikp1YW4gUGVyZXoiLCJpYXQiOjE3MzY5NTA0MDAsImV4cCI6MTczNjk1NzYwMH0...",
    "usuario": {
      "id": 1,
      "nombre": "Juan Perez",
      "email": "juan@example.com",
      "rol": "usuario"
    },
    "expira_en_segundos": 7200
  }
}
```
📤 Ejemplo de Respuesta JSON Error (Credenciales inválidas)

```json
{
  "success": false,
  "statusCode": 401,
  "message": "Credenciales inválidas",
  "intentos_restantes": 2
}
```
## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Inicio de sesión exitoso con credenciales válidas

- **Precondición:**  El usuario existe con email juan@example.com, contraseña Pass123!, estado = true, bloqueado_hasta = NULL.

- **Acción:** Ejecutar POST /api/v1/usuarios/login con credenciales correctas.

- **Resultado esperado:**

- Código HTTP 200 OK

- success: true

- statusCode: 200

- Se devuelve un token JWT válido

- intentos_fallidos se resetea a 0

- bloqueado_hasta se setea a NULL


## ❌ Caso 2: Contraseña incorrecta (primer intento)

- **Precondición:** El usuario existe, intentos_fallidos = 0.

- **Acción:** Ejecutar POST /api/v1/usuarios/login con contraseña incorrecta.

- **Resultado esperado:**

- Código HTTP 401 Unauthorized

- success = false

- statusCode: 401

- intentos_restantes: 2

- intentos_fallidos se incrementa a 1

## ❌ Caso 3: Tercer intento fallido (bloqueo)

- **Precondición:** El usuario existe, intentos_fallidos = 2.

- **Acción:** Ejecutar tercer intento con contraseña incorrecta.

- **Resultado esperado:**

- Código HTTP 403 Forbidden

- success = false

- statusCode: 403

- message: "Cuenta bloqueada por múltiples intentos fallidos"

- bloqueado_hasta = NOW() + 15 minutos

- intentos_fallidos = 3


## ❌ Caso 4: Intento de login durante bloqueo

- **Precondición:** El usuario está bloqueado (bloqueado_hasta > NOW()).

- **Acción:** Ejecutar POST /api/v1/usuarios/login con cualquier contraseña.

- **Resultado esperado:**

- Código HTTP 403 Forbidden

- success = false

- statusCode: 403

- El login se rechaza incluso con contraseña correcta

## ❌ Caso 5: Usuario desactivado

- **Precondición:** El usuario existe pero estado = false.

- **Acción:** Ejecutar POST /api/v1/usuarios/login con credenciales correctas.

- **Resultado esperado:**

- Código HTTP 401 Unauthorized

- success = false

- statusCode: 401

- message: "Usuario desactivado. Contacte al administrador"

## ❌ Caso 6: Email no existe (seguridad)

- **Precondición:** El email noexiste@example.com no está registrado.

- **Acción:** Ejecutar POST /api/v1/usuarios/login con ese email.

- **Resultado esperado:**

- Código HTTP 401 Unauthorized

- message: Credenciales inválidas" (sin revelar que el email no existe)

## ✅ Caso 7: Token JWT contiene datos correctos

- **Precondición:** Login exitoso.

- **Acción:** Decodificar el token JWT recibido.

- **Resultado esperado:**

- Payload contiene id, rol, nombre, iat, exp

- exp - iat = 7200 segundos

## ✅ Definición de Hecho

### Historia: [HU-001] Registro de usuario

### 📦 Alcance Funcional

- [ ] El endpoint POST /api/v1/usuarios/login está implementado.
- [ ] La búsqueda de usuario por email es case-insensitive.
- [ ] La validación de usuario activo funciona.
- [ ] La validación de bloqueo temporal funciona.
- [ ] La comparación de contraseña con bcrypt funciona.
- [ ] El contador de intentos fallidos persiste en base de datos.
- [ ] El bloqueo automático después de 3 fallos funciona.
- [ ] El token JWT se genera correctamente con expiración de 2 horas.

### 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para la generación de JWT.
- [ ] Se ejecutaron pruebas unitarias para bcrypt.compare.
- [ ] Se cubrieron los casos de error (credenciales inválidas, cuenta bloqueada, usuario inactivo).
- [ ] Se verificó que el mensaje de error es genérico para evitar enumeración de usuarios.
- [ ] Las pruebas funcionales están documentadas y pasadas.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describe:
    - Propósito del endpoint
    - Campos de entrada y salida
    - Ejemplo de respuesta exitosa
    - Ejemplo de error

### 🔐 Manejo de Errores

- [ ] Se devuelve código HTTP 401 para credenciales inválidas.
- [ ] Se devuelve código HTTP 403 para cuenta bloqueada.
- [ ] Se devuelve código HTTP 401 para usuario desactivado.
- [ ] Los mensajes de error son seguros (no revelan si el email existe o no).