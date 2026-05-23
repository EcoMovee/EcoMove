def create_vehiculo(self, data: VehiculoCreate) -> Vehiculo:
    # Validar tipo
    if data.tipo not in VehicleTypes.ALLOWED:
        raise HTTPException(
            status_code=HttpStatus.BAD_REQUEST,
            detail={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Datos inválidos",
                "error": {
                    "code": ErrorCodes.INVALID_DATA,
                    "details": ErrorMessages.INVALID_VEHICLE_TYPE
                }
            }
        )
    
    # Validar tarifaPorHora > 0
    if data.tarifaPorHora <= 0:
        raise HTTPException(
            status_code=HttpStatus.BAD_REQUEST,
            detail={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Datos inválidos",
                "error": {
                    "code": ErrorCodes.INVALID_DATA,
                    "details": ErrorMessages.INVALID_TARIFA
                }
            }
        )
    
    # Verificar que el vehículo no exista
    existing = self.repo.get_by_modelo(data.modelo)
    if existing:
        raise HTTPException(
            status_code=HttpStatus.BAD_REQUEST,
            detail={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": ErrorMessages.VEHICLE_ALREADY_EXISTS,
                "error": {
                    "code": ErrorCodes.VEHICLE_ALREADY_EXISTS,
                    "details": f"El vehículo con modelo {data.modelo} ya existe en el sistema"
                }
            }
        )
    
    # Crear el vehículo
    new_vehiculo = self.repo.create(data)
    
    if not new_vehiculo:
        raise HTTPException(
            status_code=HttpStatus.SERVICE_UNAVAILABLE,
            detail={
                "success": False,
                "statusCode": HttpStatus.SERVICE_UNAVAILABLE,
                "message": ErrorMessages.DB_CONNECTION_ERROR,
                "error": {
                    "code": ErrorCodes.DB_CONNECTION_ERROR,
                    "details": "No se pudo completar la operación"
                }
            }
        )
    
    return new_vehiculo