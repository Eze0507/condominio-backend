from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Create your models here.

class Persona(models.Model):
    """
    Modelo base para todas las personas en el sistema.
    Esta tabla servirá como base para empleados, usuarios, etc.
    """
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('A', 'Activo'),
        ('I', 'Inactivo'),
        ('S', 'Suspendido'),
    ]
    
    TIPO_CHOICES = [
        ('E', 'Empleado'),
        ('P', 'Propietario'),
        ('C', 'Copropietario'),
        ('F', 'Familiar'),
        ('V', 'Visitante'),
        ('A', 'Administrador'),
    ]
    
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, verbose_name="Apellido")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono", blank=True, null=True)
    foto = models.ImageField(upload_to='personas/fotos/', verbose_name="Foto", blank=True, null=True)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='A', verbose_name="Estado")
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name="Sexo")
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, verbose_name="Tipo de Persona")
    fecha_registro = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Registro")
    CI = models.CharField(max_length=20, unique=True, verbose_name="Cédula de Identidad")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    
    class Meta:
        db_table = 'persona'
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        ordering = ['apellido', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.CI}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class Cargo(models.Model):
    """
    Modelo para los cargos/posiciones de los empleados
    """
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Cargo")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    salario_base = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Salario Base")
    estado = models.BooleanField(default=True, verbose_name="Estado Activo")
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")
    
    class Meta:
        db_table = 'cargo'
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    """
    Modelo para empleados que hereda de Persona
    """
    ESTADO_CHOICES = [
        ('A', 'Activo'),
        ('I', 'Inactivo'),
        ('V', 'Vacaciones'),
        ('S', 'Suspendido'),
    ]
    
    # Relación con Persona (herencia)
    persona = models.OneToOneField(
        Persona, 
        on_delete=models.CASCADE, 
        primary_key=True,
        verbose_name="Persona"
    )
    
    # Campos específicos del empleado
    direccion = models.TextField(verbose_name="Dirección")
    sueldo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name="Sueldo"
    )
    fecha_ingreso = models.DateField(verbose_name="Fecha de Ingreso")
    fecha_salida = models.DateField(blank=True, null=True, verbose_name="Fecha de Salida")
    estado_empleado = models.CharField(
        max_length=1, 
        choices=ESTADO_CHOICES, 
        default='A', 
        verbose_name="Estado del Empleado"
    )
    
    # Relación con Cargo
    cargo = models.ForeignKey(
        Cargo, 
        on_delete=models.PROTECT, 
        verbose_name="Cargo"
    )
    
    # Campos adicionales
    numero_empleado = models.CharField(max_length=20, unique=True, verbose_name="Número de Empleado")
    
    class Meta:
        db_table = 'empleado'
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ['persona__apellido', 'persona__nombre']
    
    def __str__(self):
        return f"{self.persona.nombre_completo} - {self.cargo.nombre}"
    
    @property
    def nombre_completo(self):
        return self.persona.nombre_completo
    
    @property
    def telefono(self):
        return self.persona.telefono
    
    @property
    def CI(self):
        return self.persona.CI


