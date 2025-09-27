# Generated manually for updating existing records

from django.db import migrations


def update_persona_tipo(apps, schema_editor):
    """
    Actualizar los tipos de persona existentes:
    - Cambiar 'C' (Copropietario) por 'I' (Inquilino)
    - Eliminar registros con tipo 'A' (Administrador)
    """
    Persona = apps.get_model('administracion', 'Persona')
    
    # Cambiar copropietarios por inquilinos
    Persona.objects.filter(tipo='C').update(tipo='I')
    
    # Eliminar administradores
    Persona.objects.filter(tipo='A').delete()


def reverse_update_persona_tipo(apps, schema_editor):
    """
    Función de reversión (no se puede recuperar los administradores eliminados)
    """
    Persona = apps.get_model('administracion', 'Persona')
    
    # Revertir inquilinos a copropietarios
    Persona.objects.filter(tipo='I').update(tipo='C')


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0010_alter_persona_tipo'),
    ]

    operations = [
        migrations.RunPython(update_persona_tipo, reverse_update_persona_tipo),
    ]
