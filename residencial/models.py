from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from administracion.models import Persona

# Create your models here.

class Propietario(models.Model):
    """
    Modelo para propietarios que hereda de Persona
    """
    ESTADO_CHOICES = [
        ('A', 'Activo'),
        ('I', 'Inactivo'),
        ('S', 'Suspendido'),
        ('P', 'Pendiente'),
    ]
    
    # Relación con Persona (herencia)
    persona = models.OneToOneField(
        Persona, 
        on_delete=models.CASCADE, 
        primary_key=True,
        verbose_name="Persona"
    )
    fecha_registro_propietario = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Fecha de Registro como Propietario"
    )
    estado_propietario = models.CharField(
        max_length=1, 
        choices=ESTADO_CHOICES, 
        default='A', 
        verbose_name="Estado del Propietario"
    )
    
    # Información adicional
    observaciones = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Observaciones"
    )
    
    class Meta:
        db_table = 'propietario'
        verbose_name = "Propietario"
        verbose_name_plural = "Propietarios"
        ordering = ['persona__apellido', 'persona__nombre']
    
    def __str__(self):
        return f"{self.persona.nombre_completo} - Propietario"
    
    @property
    def nombre_completo(self):
        return self.persona.nombre_completo
    
    @property
    def telefono(self):
        return self.persona.telefono
    
    @property
    def CI(self):
        return self.persona.CI
    


class Bloque(models.Model):
    """
    Modelo para bloques del condominio
    """
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del Bloque")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    numero_pisos = models.PositiveIntegerField(default=1, verbose_name="Número de Pisos")
    estado = models.BooleanField(default=True, verbose_name="Estado Activo")
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")
    
    class Meta:
        db_table = 'bloque'
        verbose_name = "Bloque"
        verbose_name_plural = "Bloques"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Unidad(models.Model):
    """
    Modelo para unidades del condominio
    """
    ESTADO_CHOICES = [
        ('D', 'Disponible'),
        ('O', 'Ocupada'),
        ('M', 'En Mantenimiento'),
        ('R', 'Reservada'),
    ]
    
    TIPO_UNIDAD_CHOICES = [
        ('A', 'Apartamento'),
        ('C', 'Casa'),
        ('L', 'Local Comercial'),
        ('E', 'Estacionamiento'),
    ]
    
    id = models.AutoField(primary_key=True)
    numero = models.CharField(max_length=10, verbose_name="Número de Unidad")
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código de Unidad")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    dimensiones = models.CharField(max_length=100, blank=True, null=True, verbose_name="Dimensiones")
    tipo_unidad = models.CharField(
        max_length=1, 
        choices=TIPO_UNIDAD_CHOICES, 
        default='A', 
        verbose_name="Tipo de Unidad"
    )
    estado = models.CharField(
        max_length=1, 
        choices=ESTADO_CHOICES, 
        default='D', 
        verbose_name="Estado"
    )
    
    # Relación con Bloque
    bloque = models.ForeignKey(
        Bloque, 
        on_delete=models.PROTECT, 
        verbose_name="Bloque"
    )
    
    # Información adicional
    numero_piso = models.PositiveIntegerField(default=1, verbose_name="Número de Piso")
    area_m2 = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name="Área en m²"
    )
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")
    
    class Meta:
        db_table = 'unidad'
        verbose_name = "Unidad"
        verbose_name_plural = "Unidades"
        ordering = ['bloque__nombre', 'numero_piso', 'numero']
        unique_together = ['bloque', 'numero']
    
    def __str__(self):
        return f"{self.bloque.nombre} - {self.numero}"


