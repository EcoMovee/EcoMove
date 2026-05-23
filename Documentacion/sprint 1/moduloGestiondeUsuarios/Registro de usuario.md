# [HU-001] Registro de usuario

## 📖 Historia de Usuario

*Como* usuario no registrado de EcoMove,

*Quiero* crear una cuenta en la plataforma proporcionando mi nombre, email, teléfono y contraseña,

*Para* acceder al sistema y poder reservar vehículos eléctricos.

## 🔁 Flujo Esperado

- El usuario envía sus datos (nombre, email, contraseña, teléfono) al endpoint POST /api/v1/usuarios.

- El sistema valida que todos los campos requeridos estén presentes.

- El sistema verifica que el email no esté registrado previamente.

- El sistema valida que la contraseña cumpla los requisitos de seguridad.

- El sistema encripta la contraseña con bcrypt.

- El sistema inserta un nuevo registro en la tabla usuarios.

- El sistema retorna una respuesta JSON con el formato estándar de EcoMove.

## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint POST /api/v1/usuarios para registro de usuarios.

- [ ] Se valida que los campos nombre, email, password y telefono sean obligatorios.

- [ ] Se valida que el email tenga formato válido (usuario@dominio.com).

- [ ] El campo contraseña valida mínimo 8 caracteres, al menos una mayúscula, un número y un carácter especial.

- [ ] El sistema verifica que el correo no esté registrado antes de crear la cuenta.

- [ ] Se valida que el email no exista previamente en la tabla usuarios.


### 2. 📤 *Estructura de la información*

- [ ] Se responde con la siguiente estructura en JSON para registro exitoso:

```json
{
  "success": true,
  "statusCode": 201,
  "message": "Usuario creado correctamente",
  "data": {
    "id": 1,
    "nombre": "Juan Perez",
    "email": "juan@example.com",
    "telefono": "+573001234567"
  }
}
```

- [ ]  Respuesta de error por correo duplicado:

```json
{
  "success": false,
  "statusCode": 400,
  "message": "El email ya está registrado",
  "error": {
    "code": "EMAIL_EXISTS",
    "details": "El email juan@example.com ya existe en el sistema"
  }
}
```
- [ ]   Respuesta de error por formato inválido:

```json
{
  "success": false,
  "statusCode": 400,
  "message": "Datos inválidos",
  "error": {
    "code": "INVALID_DATA",
    "details": "La contraseña debe tener mínimo 8 caracteres, una mayúscula, un número y un carácter especial"
  }
}
```
## 🔧 Notas Técnicas

### Reglas de negocio
- la plataforma solo permite el registro de usuarios mayores de 18 años.

### Base de datos (tabla `usuarios`)
- La tabla debe incluir las siguientes columnas:
  - `id`: SERIAL / AUTO_INCREMENT (PK)
  - `nombre`: VARCHAR(100), NOT NULL
  - `email`: VARCHAR(100), UNIQUE, NOT NULL
  - `telefono`: VARCHAR(20), NOT NULL
  - `contrasena_hash`: VARCHAR(255), NOT NULL
  - `rol`: ENUM('usuario', 'administrador'), DEFAULT 'usuario'
  - `estado`: BOOLEAN, DEFAULT TRUE
  - `fecha_registro`: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP
  - `intentos_fallidos`: INT, DEFAULT 0
  - `bloqueado_hasta`: TIMESTAMP, NULLABLE

### Seguridad
- Usar la librería `bcrypt` con `saltRounds = 10` para encriptar la contraseña.
- Normalizar el email a minúsculas antes de guardarlo y antes de buscar duplicados.

### Manejo de errores
- Los códigos de error (`EMAIL_EXISTS`, `INVALID_DATA`) deben ser constantes definidas en un archivo de errores del sistema.

## 🚀 Endpoint – Registro de usuario

- **Método HTTP:** `POST`

- **Ruta:** `/api/v1/usuarios`

📤 Ejemplo de Request JSON

```json
{
  "nombre": "Juan Perez",
  "correo": "juan@example.com",
  "telefono": "+573001234567",
  "contrasena": "Pass123!"
}
```
📤 Ejemplo de Respuesta JSON Exitosa

```json
{
  "success": true,
  "statusCode": 201,
  "message": "Usuario creado correctamente",
  "data": {
    "id": 1,
    "nombre": "Juan Perez",
    "email": "juan@example.com",
    "telefono": "+573001234567"
  }
}
```
📤 Ejemplo de Respuesta JSON Error

```json
{
  "success": false,
  "statusCode": 400,
  "message": "El email ya está registrado",
  "error": {
    "code": "EMAIL_EXISTS",
    "details": "El email juan@example.com ya existe en el sistema"
  }
}
```
## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

## ✅ Caso 1: Registro exitoso con todos los campos válidos

- **Precondición:**  El email juan@example.com no existe en la tabla usuarios.

- **Acción:** Ejecutar POST /api/v1/usuarios con el JSON de ejemplo.

- **Resultado esperado:**

- Código HTTP 201 Created

- success: true

- statusCode: 201

- message: "Usuario creado correctamente"

- La contraseña almacenada es un hash de bcrypt


## ✅ Caso 2: Validación de correo duplicado

- **Precondición:** El correo juan@example.com ya existe en la base de datos.

- **Acción:** Enviar POST con el mismo correo.

- **Resultado esperado:**

- Código HTTP 400 Bad Request

- success = false

- statusCode: 400

- message: "El correo electrónico ya está registrado"

- No se crea un nuevo usuario

## ❌ Caso 3: Formato de contraseña inválido

- **Precondición:** Ninguna.

- **Acción:** Enviar POST con contraseña "123456" (sin mayúscula, sin carácter especial).

- **Resultado esperado:**

- Código HTTP 400 Bad Request

- success = false

- statusCode: 400

- message: "La contraseña no cumple con los requisitos"


## ❌ Caso 4: Formato de teléfono inválido

- **Precondición:** Ninguna.

- **Acción:** Enviar POST con teléfono "123".

- **Resultado esperado:**

- Código HTTP 400 Bad Request

- success = false

- statusCode: 400

- message: "El teléfono debe tener código de país y entre 7 y 15 dígitos"

## ❌ Caso 5: Formato de correo inválido

- **Precondición:** Ninguna.

- **Acción:** Enviar POST con correo "juanexample.com".

- **Resultado esperado:**

- Código HTTP 400 Bad Request

- success = false

- statusCode: 400

- message: "El correo no tiene un formato válido"

## ✅ Caso 6: Verificar encriptación de contraseña

- **Precondición:** Registro exitoso.

- **Acción:** Consultar el usuario en la base de datos.

- **Resultado esperado:**

- La contraseña almacenada es un hash de bcrypt, no texto plano.

## ✅ Definición de Hecho

### Historia: [HU-001] Registro de usuario

### 📦 Alcance Funcional

- [ ] El endpoint POST /api/v1/usuarios está implementado.
- [ ] Las validaciones de formato funcionan correctamente.
- [ ] La validación de unicidad de correo funciona.
- [ ] La contraseña se encripta con bcrypt antes de guardarse.
- [ ] Las respuestas JSON cumplen con el contrato definido.

### 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para cada validación.
- [ ] Se ejecutaron pruebas de integración para el flujo completo.
- [ ] Se probaron todos los casos de error documentados.
- [ ] Se verificó que no se guardan contraseñas en texto plano.

### 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describe: Propósito del endpoint, Campos de entrada y salida
- [ ] Ejemplo de respuesta exitosa y de error.

### 🔐 Manejo de Errores

- [ ] Se devuelve código HTTP 400 para errores de validación.
- [ ] El campo `errores` en el JSON incluye mensajes claros.
- [ ] No se devuelve información sensible en los errores.