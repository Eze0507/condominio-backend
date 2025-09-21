# CU9: Gestionar Propietarios - Documentación

## Resumen
Se ha implementado exitosamente el Caso de Uso 9 "Gestionar Propietarios" en el paquete residencial, aprovechando la clase `Persona` como base y asegurando que **NO tenga autenticación** como se solicitó. La implementación incluye modelos, serializers, vistas y URLs para la gestión completa de propietarios, bloques, unidades y contratos.

## Modelos Implementados

### 1. Propietario (Hereda de Persona)
- **Propósito**: Propietarios que heredan de la tabla base Persona
- **Campos principales**:
  - Relación OneToOne con Persona
  - `tipo_propietario` (Propietario, Copropietario, Arrendatario)
  - `estado_propietario`, `porcentaje_propiedad`
  - `email_alternativo`, `telefono_alternativo`
  - `observaciones`, `fecha_registro_propietario`
- **Relaciones**: Base para Contratos

### 2. Bloque
- **Propósito**: Bloques del condominio
- **Campos principales**:
  - `id`, `nombre` (único), `descripcion`
  - `numero_pisos`, `estado`, `fecha_creacion`

### 3. Unidad
- **Propósito**: Unidades dentro de los bloques
- **Campos principales**:
  - `id`, `numero`, `codigo` (único), `descripcion`
  - `tipo_unidad` (Apartamento, Casa, Local, Estacionamiento)
  - `estado` (Disponible, Ocupada, Mantenimiento, Reservada)
  - Relación ForeignKey con Bloque
  - `numero_piso`, `area_m2`

### 4. Contrato
- **Propósito**: Contratos de propiedad/arrendamiento
- **Campos principales**:
  - `id`, `numero_contrato` (único), `fecha_inicio`, `fecha_fin`
  - `cuota_mensual`, `monto_total`, `impuesto`
  - `tipo_contrato` (Propiedad, Arrendamiento, Comodato)
  - `estado` (Activo, Inactivo, Vencido, Suspendido, Cancelado)
  - Relaciones con Propietario y Unidad
  - `documento`, `observaciones`

## Serializers Implementados

### Archivo: `residencial/serializers/serializersPropietario.py`

1. **PropietarioSerializer**: Gestión completa de propietarios
2. **PropietarioCreateSerializer**: Creación de propietarios con datos de persona incluidos
3. **PropietarioListSerializer**: Vista simplificada para listados
4. **BloqueSerializer**: Gestión de bloques
5. **UnidadSerializer**: Gestión de unidades
6. **ContratoSerializer**: Gestión de contratos
7. **PropietarioStatsSerializer**: Estadísticas de propietarios

## Vistas Implementadas

### Archivo: `residencial/views.py`

**IMPORTANTE**: Todas las vistas están marcadas como **SIN AUTENTICACIÓN** - Acceso libre

1. **PropietarioViewSet**: CRUD completo para propietarios con acciones adicionales:
   - `estadisticas/`: Obtener estadísticas de propietarios
   - `{id}/contratos/`: Obtener contratos de un propietario
   - `{id}/activar/`: Activar propietario
   - `{id}/desactivar/`: Desactivar propietario

2. **BloqueViewSet**: CRUD completo para bloques con acciones:
   - `{id}/unidades/`: Obtener unidades de un bloque

3. **UnidadViewSet**: CRUD completo para unidades con acciones:
   - `{id}/contratos/`: Obtener contratos de una unidad

4. **ContratoViewSet**: CRUD completo para contratos con acciones:
   - `{id}/activar/`: Activar contrato
   - `{id}/cancelar/`: Cancelar contrato
   - `{id}/suspender/`: Suspender contrato

## URLs Disponibles

### Base URL: `/api/residencial/`

#### Propietarios
- `GET /propietarios/` - Listar propietarios
- `POST /propietarios/` - Crear propietario
- `GET /propietarios/{id}/` - Obtener propietario
- `PUT /propietarios/{id}/` - Actualizar propietario
- `PATCH /propietarios/{id}/` - Actualizar parcialmente
- `DELETE /propietarios/{id}/` - Eliminar propietario
- `GET /propietarios/estadisticas/` - Estadísticas de propietarios
- `GET /propietarios/{id}/contratos/` - Contratos del propietario
- `POST /propietarios/{id}/activar/` - Activar propietario
- `POST /propietarios/{id}/desactivar/` - Desactivar propietario

#### Bloques
- `GET /bloques/` - Listar bloques
- `POST /bloques/` - Crear bloque
- `GET /bloques/{id}/` - Obtener bloque
- `PUT /bloques/{id}/` - Actualizar bloque
- `PATCH /bloques/{id}/` - Actualizar parcialmente
- `DELETE /bloques/{id}/` - Eliminar bloque
- `GET /bloques/{id}/unidades/` - Unidades del bloque

#### Unidades
- `GET /unidades/` - Listar unidades
- `POST /unidades/` - Crear unidad
- `GET /unidades/{id}/` - Obtener unidad
- `PUT /unidades/{id}/` - Actualizar unidad
- `PATCH /unidades/{id}/` - Actualizar parcialmente
- `DELETE /unidades/{id}/` - Eliminar unidad
- `GET /unidades/{id}/contratos/` - Contratos de la unidad

#### Contratos
- `GET /contratos/` - Listar contratos
- `POST /contratos/` - Crear contrato
- `GET /contratos/{id}/` - Obtener contrato
- `PUT /contratos/{id}/` - Actualizar contrato
- `PATCH /contratos/{id}/` - Actualizar parcialmente
- `DELETE /contratos/{id}/` - Eliminar contrato
- `POST /contratos/{id}/activar/` - Activar contrato
- `POST /contratos/{id}/cancelar/` - Cancelar contrato
- `POST /contratos/{id}/suspender/` - Suspender contrato

## Filtros y Búsquedas Disponibles

### Propietarios
- Búsqueda: `persona__nombre`, `persona__apellido`, `persona__CI`, `email_alternativo`, `telefono_alternativo`
- Filtros: `tipo` (P=Propietario, C=Copropietario, A=Arrendatario), `estado`, `porcentaje_min`, `porcentaje_max`
- Ordenamiento: `persona__apellido`, `persona__nombre`, `fecha_registro_propietario`, `tipo_propietario`, `estado_propietario`, `porcentaje_propiedad`

### Bloques
- Búsqueda: `nombre`, `descripcion`
- Filtros: `estado` (true/false)
- Ordenamiento: `nombre`, `numero_pisos`, `fecha_creacion`

### Unidades
- Búsqueda: `numero`, `codigo`, `descripcion`, `bloque__nombre`
- Filtros: `bloque`, `estado`, `tipo`, `piso`
- Ordenamiento: `numero`, `codigo`, `numero_piso`, `area_m2`, `fecha_creacion`

### Contratos
- Búsqueda: `numero_contrato`, `propietario__persona__nombre`, `propietario__persona__apellido`, `unidad__numero`, `unidad__codigo`
- Filtros: `propietario`, `unidad`, `estado`, `tipo`, `fecha_inicio`, `fecha_fin`
- Ordenamiento: `fecha_inicio`, `fecha_fin`, `cuota_mensual`, `monto_total`, `estado`, `fecha_creacion`

## Características Especiales

### Validaciones Implementadas
- Cédula única para personas (heredada)
- Email alternativo único para propietarios
- Código de unidad único
- Número de contrato único
- Porcentaje de propiedad entre 0 y 100
- Fechas de nacimiento no futuras
- Fecha fin posterior a fecha inicio en contratos

### Funcionalidades Automáticas
- Establecimiento automático del tipo de persona como 'R' (Residente) para propietarios
- Timestamps automáticos para fechas de creación
- Cálculo automático de estado activo en contratos

### Estados y Flujos
- **Propietarios**: Activo, Inactivo, Suspendido, Pendiente
- **Unidades**: Disponible, Ocupada, En Mantenimiento, Reservada
- **Contratos**: Activo → Inactivo/Vencido/Suspendido/Cancelado

## Paso a Paso para Usar el Sistema

### 1. Crear Bloque
```bash
POST /api/residencial/bloques/
{
    "nombre": "Bloque A",
    "descripcion": "Bloque principal del condominio",
    "numero_pisos": 5,
    "estado": true
}
```

### 2. Crear Unidad
```bash
POST /api/residencial/unidades/
{
    "numero": "101",
    "codigo": "A-101",
    "descripcion": "Apartamento 101",
    "tipo_unidad": "A",
    "estado": "D",
    "bloque": 1,
    "numero_piso": 1,
    "area_m2": 85.50
}
```

### 3. Crear Propietario
```bash
POST /api/residencial/propietarios/
{
    "nombre": "María",
    "apellido": "González",
    "telefono": "987654321",
    "sexo": "F",
    "CI": "87654321",
    "fecha_nacimiento": "1985-05-15",
    "tipo_propietario": "P",
    "estado_propietario": "A",
    "porcentaje_propiedad": 100.00,
    "email_alternativo": "maria@email.com"
}
```

### 4. Crear Contrato
```bash
POST /api/residencial/contratos/
{
    "numero_contrato": "CONT-001",
    "fecha_inicio": "2024-01-01",
    "fecha_fin": "2024-12-31",
    "cuota_mensual": 500.00,
    "monto_total": 6000.00,
    "tipo_contrato": "P",
    "estado": "A",
    "propietario": 1,
    "unidad": 1
}
```

### 5. Obtener Estadísticas
```bash
GET /api/residencial/propietarios/estadisticas/
```

## Migraciones Ejecutadas
- ✅ `residencial.0001_initial` - Creación de todas las tablas

## Confirmación de NO Autenticación
**TODAS las vistas del CU9 están marcadas como SIN AUTENTICACIÓN**:
- ✅ PropietarioViewSet - **SIN autenticación**
- ✅ BloqueViewSet - **SIN autenticación**
- ✅ UnidadViewSet - **SIN autenticación**
- ✅ ContratoViewSet - **SIN autenticación**

## Relación con Persona
- Los propietarios **heredan completamente** de la tabla `Persona`
- Se establece automáticamente `tipo='R'` (Residente) al crear propietarios
- Acceso a todos los campos de persona: nombre, apellido, CI, teléfono, etc.

## Próximos Pasos Recomendados
1. Crear datos de prueba (bloques, unidades, propietarios)
2. Implementar reportes y exportaciones
3. Agregar validaciones de negocio adicionales
4. Implementar notificaciones para cambios de estado
5. Crear dashboard con estadísticas en tiempo real

---
**Fecha de implementación**: $(date)
**Desarrollador**: Asistente AI
**Versión**: 1.0
**Paquete**: residencial
**Autenticación**: NO REQUERIDA (Acceso libre)
