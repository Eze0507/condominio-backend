# Funcionalidades Eliminadas - Para Implementación Futura

## Resumen
Este documento contiene la documentación completa de las funcionalidades eliminadas del sistema de condominio para ser implementadas en futuras versiones. Estas funcionalidades fueron removidas para simplificar el alcance del proyecto actual.

## Funcionalidades Eliminadas

### 1. Sistema de Nóminas (administracion)

#### Modelos Eliminados:
- **Nomina**: Gestión de nóminas de empleados
- **DetalleNomina**: Detalles de cada nómina

#### Campos del Modelo Nomina:
```python
class Nomina(models.Model):
    id = models.AutoField(primary_key=True)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha = models.DateField(verbose_name="Fecha de Nómina")
    periodo_inicio = models.DateField(verbose_name="Período Inicio")
    periodo_fin = models.DateField(verbose_name="Período Fin")
    estado = models.CharField(max_length=3, choices=ESTADO_CHOICES, default='P')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cantidad_horas = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_pago = models.DateTimeField(blank=True, null=True)
    
    ESTADO_CHOICES = [
        ('P', 'Pendiente'),
        ('A', 'Aprobada'),
        ('PAG', 'Pagada'),
        ('C', 'Cancelada'),
    ]
```

#### Campos del Modelo DetalleNomina:
```python
class DetalleNomina(models.Model):
    id = models.AutoField(primary_key=True)
    nomina = models.ForeignKey(Nomina, on_delete=models.CASCADE, related_name='detalles')
    tipo = models.CharField(max_length=3, choices=TIPO_CHOICES)
    descripcion = models.CharField(max_length=200)
    sueldo_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    beneficios = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuentos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    
    TIPO_CHOICES = [
        ('S', 'Salario'),
        ('B', 'Beneficio'),
        ('D', 'Descuento'),
        ('H', 'Horas Extras'),
        ('BON', 'Bonificación'),
        ('COM', 'Comisión'),
    ]
```

#### Serializers Eliminados:
- **NominaSerializer**: Gestión completa de nóminas
- **NominaCreateSerializer**: Creación de nóminas con detalles
- **DetalleNominaSerializer**: Gestión de detalles de nómina

#### Vistas Eliminadas:
- **NominaViewSet**: CRUD completo para nóminas
- **DetalleNominaViewSet**: CRUD completo para detalles de nómina

#### URLs Eliminadas:
- `/api/administracion/nominas/`
- `/api/administracion/detalles-nomina/`

#### Funcionalidades Especiales Eliminadas:
- Aprobar nóminas (`POST /nominas/{id}/aprobar/`)
- Marcar como pagadas (`POST /nominas/{id}/pagar/`)
- Cancelar nóminas (`POST /nominas/{id}/cancelar/`)
- Cálculo automático de totales
- Validaciones de períodos únicos

### 2. Sistema de Contratos (residencial)

#### Modelo Eliminado:
- **Contrato**: Contratos de propiedad/arrendamiento

#### Campos del Modelo Contrato:
```python
class Contrato(models.Model):
    id = models.AutoField(primary_key=True)
    numero_contrato = models.CharField(max_length=50, unique=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    cuota_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='A')
    tipo_contrato = models.CharField(max_length=1, choices=TIPO_CONTRATO_CHOICES, default='P')
    documento = models.FileField(upload_to='contratos/', blank=True, null=True)
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    ESTADO_CHOICES = [
        ('A', 'Activo'),
        ('I', 'Inactivo'),
        ('V', 'Vencido'),
        ('S', 'Suspendido'),
        ('C', 'Cancelado'),
    ]
    
    TIPO_CONTRATO_CHOICES = [
        ('P', 'Propiedad'),
        ('A', 'Arrendamiento'),
        ('C', 'Comodato'),
    ]
```

#### Serializer Eliminado:
- **ContratoSerializer**: Gestión completa de contratos

#### Vista Eliminada:
- **ContratoViewSet**: CRUD completo para contratos

#### URL Eliminada:
- `/api/residencial/contratos/`

#### Funcionalidades Especiales Eliminadas:
- Activar contratos (`POST /contratos/{id}/activar/`)
- Cancelar contratos (`POST /contratos/{id}/cancelar/`)
- Suspender contratos (`POST /contratos/{id}/suspender/`)
- Validación de fechas de contrato
- Carga de documentos

## Guía de Re-implementación

### Para Nóminas:

1. **Crear modelos**:
   ```python
   # En administracion/models.py
   class Nomina(models.Model):
       # ... campos del modelo arriba
   
   class DetalleNomina(models.Model):
       # ... campos del modelo arriba
   ```

2. **Crear serializers**:
   ```python
   # En administracion/serializers/serializersEmpleado.py
   class NominaSerializer(serializers.ModelSerializer):
       # ... implementación completa
   
   class DetalleNominaSerializer(serializers.ModelSerializer):
       # ... implementación completa
   ```

3. **Crear vistas**:
   ```python
   # En administracion/views.py
   class NominaViewSet(viewsets.ModelViewSet):
       # ... implementación completa
   
   class DetalleNominaViewSet(viewsets.ModelViewSet):
       # ... implementación completa
   ```

4. **Configurar URLs**:
   ```python
   # En administracion/urls.py
   router.register(r'nominas', NominaViewSet, basename='nominas')
   router.register(r'detalles-nomina', DetalleNominaViewSet, basename='detalles-nomina')
   ```

### Para Contratos:

1. **Crear modelo**:
   ```python
   # En residencial/models.py
   class Contrato(models.Model):
       # ... campos del modelo arriba
   ```

2. **Crear serializer**:
   ```python
   # En residencial/serializers/serializersPropietario.py
   class ContratoSerializer:
       # ... implementación completa
   ```

3. **Crear vista**:
   ```python
   # En residencial/views.py
   class ContratoViewSet(viewsets.ModelViewSet):
       # ... implementación completa
   ```

4. **Configurar URL**:
   ```python
   # En residencial/urls.py
   router.register(r'contratos', ContratoViewSet, basename='contratos')
   ```

## Consideraciones Técnicas

### Migraciones:
- Las migraciones de eliminación ya fueron aplicadas
- Para re-implementar, crear nuevas migraciones con los modelos

### Relaciones:
- **Nomina** → **Empleado** (ForeignKey)
- **DetalleNomina** → **Nomina** (ForeignKey)
- **Contrato** → **Propietario** (ForeignKey)
- **Contrato** → **Unidad** (ForeignKey)

### Validaciones Importantes:
- Números de contrato únicos
- Períodos de nómina únicos por empleado
- Fechas de contrato válidas
- Montos positivos

### Funcionalidades Avanzadas:
- Cálculo automático de totales de nómina
- Estados de flujo de trabajo
- Carga de documentos
- Reportes y estadísticas

## Notas de Implementación

1. **Prioridad**: Implementar primero los modelos básicos
2. **Validaciones**: Agregar validaciones robustas desde el inicio
3. **Estados**: Implementar flujos de estado completos
4. **Documentos**: Considerar almacenamiento de archivos
5. **Reportes**: Planificar funcionalidades de reportes

---
**Fecha de eliminación**: $(date)
**Motivo**: Simplificación del alcance del proyecto
**Estado**: Documentado para implementación futura
