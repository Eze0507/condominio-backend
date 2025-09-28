from django.db import models
from administracion.models import Persona

class contrato(models.Model):
    ESTADO_CHOICES = [
        ('A', 'Activo'),
        ('I', 'Inactivo'),
        ('P', 'Pendiente'),
        ('F', 'Finalizado'),
    ]
    
    id = models.AutoField(primary_key=True)
    propietario = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='contratos_propietario')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    cuota_mensual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P')
    documento_url = models.URLField(max_length=200, blank=True, null=True)
    costo_compra = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    contrato_PDF = models.URLField(max_length=200, blank=True, null=True)
    
    class Meta:
        db_table = 'contrato'
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        
    def __str__(self):
        return f"Contrato {self.id} - Propietario: {self.propietario.nombre} {self.propietario.apellido}"
