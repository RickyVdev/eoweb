import os
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
    direccion = models.CharField(max_length=200, blank=True)
    colonia = models.CharField(max_length=100, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    rfc = models.CharField(max_length=13, blank=True)
    razon_social = models.CharField(max_length=200, blank=True)
    telefono1 = models.CharField(max_length=20, default='0000000000')  # Valor temporal  # Obligatorio
    telefono2 = models.CharField(max_length=20, blank=True)  # Opcional
    obra = models.TextField(blank=True)
    atendio_reporte = models.ForeignKey('Empleado', null=True, blank=True, on_delete=models.SET_NULL)

    cfdi = models.FileField(upload_to='cfdis/', null=True, blank=True)
    def delete(self, *args, **kwargs):
        # Borrar archivo CFDI si existe
        if self.cfdi and os.path.isfile(self.cfdi.path):
            os.remove(self.cfdi.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    cargo = models.CharField(max_length=50)

    # Nuevos campos
    domicilio = models.CharField(max_length=255, blank=True, null=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    rfc = models.CharField(max_length=13, blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    tipo_sangre = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return self.nombre
    
class EmpleadoDocumento(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='documentos')
    archivo = models.FileField(upload_to='documentos_empleados/')
    descripcion = models.CharField(max_length=100, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        if self.archivo and os.path.isfile(self.archivo.path):
            os.remove(self.archivo.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.empleado.nombre} - {self.archivo.name}"
