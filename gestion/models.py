import os
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Cliente(models.Model):
    clave = models.CharField(max_length=100, unique=True, null=True, blank=True)
    nombre = models.CharField("Nombre", max_length=255)
    calle = models.CharField("Calle", max_length=100, blank=True, null=True)
    numero_exterior = models.CharField("Número exterior", max_length=10, blank=True, null=True)
    numero_interior = models.CharField("Número interior", max_length=10, blank=True, null=True)
    colonia = models.CharField("Colonia", max_length=100)
    ciudad = models.CharField("Ciudad", max_length=100)
    telefono = models.CharField("Teléfono 1", max_length=10, blank=True)
    extension = models.CharField("Extensión", max_length=3, blank=True, null=True)
    telefono2 = models.CharField("Teléfono 2", max_length=10, blank=True, null=True)
    movil = models.CharField("Móvil", max_length=10, blank=True, null=True)
    atencion_a = models.CharField("Atención a", max_length=255, blank=True)
    obra = models.CharField("Obra", max_length=150)
    localizacion = models.CharField("Localización", max_length=150, blank=True)
    correo = models.EmailField("Correo", blank=True)

    def __str__(self):
        return f"{self.clave} - {self.nombre}"

class Puesto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Empleado(models.Model): 
    id_personal = models.CharField(max_length=20, unique=True, null=True, blank=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    puesto_antiguo = models.CharField(max_length=100, null=True, blank=True)  # renombrado
    puesto = models.ForeignKey(Puesto, on_delete=models.SET_NULL, null=True, blank=True)

    # Campos adicionales
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
    

