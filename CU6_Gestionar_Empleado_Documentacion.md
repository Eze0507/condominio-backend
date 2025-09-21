# CU6: Gestionar Empleado - Documentación

## Resumen
Se ha implementado exitosamente el Caso de Uso 6 "Gestionar Empleado" basado en el diagrama ERD proporcionado. La implementación incluye modelos, serializers, vistas y URLs para la gestión completa de empleados, cargos, nóminas y detalles de nómina.

## Modelos Implementados

### 1. Persona (Tabla Base)
- **Propósito**: Tabla base para todas las personas en el sistema
- **Campos principales**:
  - `id`, `nombre`, `apellido`, `telefono`, `foto`
  - `estado`, `sexo`, `tipo`, `fecha_registro`
  - `CI` (único), `fecha_nacimiento`
- **Relaciones**: Base para Empleado y otros actores del sistema

### 2. Cargo
- **Propósito**: Posiciones/cargos de los empleados
- **Campos principales**:
  - `id`, `nombre` (único), `descripcion`
  - `salario_base`, `estado`, `fecha_creacion`

### 3. Empleado
- **Propósito**: Empleados que heredan de Persona
- **Campos principales**:
  - Relación OneToOne con Persona
  - `direccion`, `sueldo`, `fecha_ingreso`, `fecha_salida`
  - `estado_empleado`, `numero_empleado` (único)
  - Relación ForeignKey con Cargo
  - `supervisor` (self-referencing)

### 4. Nomina
- **Propósito**: Nóminas de empleados
- **Campos principales**:
  - `id`, `empleado`, `fecha`, `periodo_inicio`, `periodo_fin`
  - `estado`, `total`, `cantidad_horas`
  - `fecha_creacion`, `fecha_pago`

### 5. DetalleNomina
- **Propósito**: Detalles de cada nómina
- **Campos principales**:
  - `id`, `nomina`, `tipo`, `descripcion`
  - `sueldo_base`, `beneficios`, `descuentos`, `monto`, `cantidad`

## Serializers Implementados

### Archivo: `administracion/serializers/serializersEmpleado.py`

1. **PersonaSerializer**: Gestión completa de personas
2. **CargoSerializer**: Gestión de cargos
3. **EmpleadoSerializer**: Gestión completa de empleados (incluye persona)
4. **EmpleadoListSerializer**: Vista simplificada para listados
5. **NominaSerializer**: Gestión de nóminas
6. **NominaCreateSerializer**: Creación de nóminas con detalles
7. **DetalleNominaSerializer**: Gestión de detalles de nómina
8. **EmpleadoStatsSerializer**: Estadísticas de empleados

## Vistas Implementadas

### Archivo: `administracion/views.py`

1. **PersonaViewSet**: CRUD completo para personas
2. **CargoViewSet**: CRUD completo para cargos
3. **EmpleadoViewSet**: CRUD completo para empleados con acciones adicionales:
   - `estadisticas/`: Obtener estadísticas de empleados
   - `{id}/nominas/`: Obtener nóminas de un empleado
   - `{id}/activar/`: Activar empleado
   - `{id}/desactivar/`: Desactivar empleado
4. **NominaViewSet**: CRUD completo para nóminas con acciones:
   - `{id}/aprobar/`: Aprobar nómina
   - `{id}/pagar/`: Marcar como pagada
   - `{id}/cancelar/`: Cancelar nómina
5. **DetalleNominaViewSet**: CRUD completo para detalles de nómina

## URLs Disponibles

### Base URL: `/administracion/`

#### Personas
- `GET /personas/` - Listar personas
- `POST /personas/` - Crear persona
- `GET /personas/{id}/` - Obtener persona
- `PUT /personas/{id}/` - Actualizar persona
- `PATCH /personas/{id}/` - Actualizar parcialmente
- `DELETE /personas/{id}/` - Eliminar persona

#### Cargos
- `GET /cargos/` - Listar cargos
- `POST /cargos/` - Crear cargo
- `GET /cargos/{id}/` - Obtener cargo
- `PUT /cargos/{id}/` - Actualizar cargo
- `PATCH /cargos/{id}/` - Actualizar parcialmente
- `DELETE /cargos/{id}/` - Eliminar cargo

#### Empleados
- `GET /empleados/` - Listar empleados
- `POST /empleados/` - Crear empleado
- `GET /empleados/{id}/` - Obtener empleado
- `PUT /empleados/{id}/` - Actualizar empleado
- `PATCH /empleados/{id}/` - Actualizar parcialmente
- `DELETE /empleados/{id}/` - Eliminar empleado
- `GET /empleados/estadisticas/` - Estadísticas de empleados
- `GET /empleados/{id}/nominas/` - Nóminas del empleado
- `POST /empleados/{id}/activar/` - Activar empleado
- `POST /empleados/{id}/desactivar/` - Desactivar empleado

#### Nóminas
- `GET /nominas/` - Listar nóminas
- `POST /nominas/` - Crear nómina
- `GET /nominas/{id}/` - Obtener nómina
- `PUT /nominas/{id}/` - Actualizar nómina
- `PATCH /nominas/{id}/` - Actualizar parcialmente
- `DELETE /nominas/{id}/` - Eliminar nómina
- `POST /nominas/{id}/aprobar/` - Aprobar nómina
- `POST /nominas/{id}/pagar/` - Marcar como pagada
- `POST /nominas/{id}/cancelar/` - Cancelar nómina

#### Detalles de Nómina
- `GET /detalles-nomina/` - Listar detalles
- `POST /detalles-nomina/` - Crear detalle
- `GET /detalles-nomina/{id}/` - Obtener detalle
- `PUT /detalles-nomina/{id}/` - Actualizar detalle
- `PATCH /detalles-nomina/{id}/` - Actualizar parcialmente
- `DELETE /detalles-nomina/{id}/` - Eliminar detalle

## Filtros y Búsquedas Disponibles

### Personas
- Búsqueda: `nombre`, `apellido`, `CI`, `telefono`
- Filtros: `tipo` (E=Empleado, R=Residente, V=Visitante, A=Administrador)
- Ordenamiento: `nombre`, `apellido`, `fecha_registro`, `CI`

### Cargos
- Búsqueda: `nombre`, `descripcion`
- Filtros: `estado` (true/false)
- Ordenamiento: `nombre`, `salario_base`, `fecha_creacion`

### Empleados
- Búsqueda: `persona__nombre`, `persona__apellido`, `persona__CI`, `numero_empleado`, `cargo__nombre`
- Filtros: `estado`, `cargo`, `sueldo_min`, `sueldo_max`
- Ordenamiento: `persona__apellido`, `persona__nombre`, `fecha_ingreso`, `sueldo`, `estado_empleado`

### Nóminas
- Búsqueda: `empleado__persona__nombre`, `empleado__persona__apellido`, `empleado__numero_empleado`
- Filtros: `empleado`, `estado`, `fecha_inicio`, `fecha_fin`
- Ordenamiento: `fecha`, `periodo_inicio`, `periodo_fin`, `total`, `estado`

## Características Especiales

### Validaciones Implementadas
- Cédula única para personas
- Número de empleado único
- Fechas de nacimiento no futuras
- Fecha de salida posterior a fecha de ingreso
- Sueldos positivos
- Nóminas únicas por empleado y período

### Funcionalidades Automáticas
- Generación automática de número de empleado (EMP0001, EMP0002, etc.)
- Cálculo automático del total de nóminas
- Establecimiento automático del tipo de persona como 'E' para empleados
- Timestamps automáticos para fechas de creación

### Estados y Flujos
- **Empleados**: Activo, Inactivo, Vacaciones, Suspendido
- **Nóminas**: Pendiente → Aprobada → Pagada / Cancelada

## Paso a Paso para Usar el Sistema

### 1. Crear Cargos
```bash
POST /administracion/cargos/
{
    "nombre": "Administrador",
    "descripcion": "Administrador del condominio",
    "salario_base": 5000.00
}
```

### 2. Crear Empleado
```bash
POST /administracion/empleados/
{
    "persona": {
        "nombre": "Juan",
        "apellido": "Pérez",
        "telefono": "123456789",
        "sexo": "M",
        "CI": "12345678",
        "fecha_nacimiento": "1990-01-01"
    },
    "direccion": "Calle Principal 123",
    "sueldo": 5000.00,
    "fecha_ingreso": "2024-01-01",
    "cargo": 1
}
```

### 3. Crear Nómina
```bash
POST /administracion/nominas/
{
    "empleado": 1,
    "fecha": "2024-01-31",
    "periodo_inicio": "2024-01-01",
    "periodo_fin": "2024-01-31",
    "cantidad_horas": 160,
    "detalles": [
        {
            "tipo": "S",
            "descripcion": "Salario base",
            "sueldo_base": 5000.00,
            "monto": 5000.00,
            "cantidad": 1
        }
    ]
}
```

### 4. Aprobar y Pagar Nómina
```bash
POST /administracion/nominas/1/aprobar/
POST /administracion/nominas/1/pagar/
```

## Migraciones Ejecutadas
- ✅ `administracion.0001_initial` - Creación de todas las tablas

## Dependencias Instaladas
- ✅ `Pillow` - Para el manejo de imágenes en el campo `foto`

## Próximos Pasos Recomendados
1. Crear datos de prueba (fixtures)
2. Implementar permisos y autenticación específica
3. Agregar reportes y exportaciones
4. Implementar notificaciones para cambios de estado
5. Agregar validaciones de negocio adicionales

---
**Fecha de implementación**: $(date)
**Desarrollador**: Asistente AI
**Versión**: 1.0
