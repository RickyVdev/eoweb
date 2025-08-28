import os
import base64
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile


# Create your models here.
class Cliente(models.Model):
    clave = models.CharField(max_length=100, unique=True, null=True, blank=True)
    nombre = models.CharField("Nombre", max_length=255)
    calle = models.CharField("Calle", max_length=100, blank=True, null=True)
    numero_exterior = models.CharField("Número exterior", max_length=5, blank=True, null=True)
    numero_interior = models.CharField("Número interior", max_length=5, blank=True, null=True)
    colonia = models.CharField("Colonia", max_length=100)
    codigo_postal = models.CharField("Código Postal", max_length=10, blank=True)
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
    telefono = models.CharField(max_length=10, blank=True)
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
    
class Obra(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='obras')
    clave_obra = models.CharField("Clave Obra", max_length=20)
    nombre = models.CharField("Nombre de la Obra", max_length=150)
    atencion_a = models.CharField("Atención a", max_length=255, blank=True)
    localizacion = models.CharField("Localización", max_length=150, blank=True)

    def __str__(self):
        return f"{self.clave_obra} - {self.nombre} ({self.cliente.nombre})"

class TrabajoRealizado(models.Model):
    nombre = models.CharField("Trabajo realizado", max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    obra = models.ForeignKey(Obra, on_delete=models.CASCADE, related_name='servicios')
    fecha = models.DateField()
    otvm = models.CharField("O.T.V.M.", max_length=20)

    llegada = models.TimeField("Llegada a las")
    termino = models.TimeField("Término de los trabajos a las")

    solicitante = models.CharField("Solicitó el servicio", max_length=100)
    preguntar_por = models.CharField("Preguntar por", max_length=100)
    
    trabajo_realizado = models.ForeignKey(TrabajoRealizado, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    observaciones = models.TextField(blank=True)

    # Datos relacionados a cliente/obra
    clave_cliente = models.CharField("Clave Cliente", max_length=100)  # se puede llenar desde obra.cliente.clave
    localizacion = models.CharField("Localización", max_length=150) # se puede llenar desde obra.localizacion

    # VoBo Cliente
    vobo_cliente_nombre = models.CharField(max_length=100)
    vobo_cliente_firma = models.ImageField(upload_to="firmas/", blank=True, null=True)

    # Por el Lab
    lab_nombre = models.CharField(max_length=100)
    lab_firma = models.ImageField(upload_to="firmas/", blank=True, null=True)

    # Supervisó, Capturó, Facturó, Autorizó
    superviso_nombre = models.CharField(max_length=100)
    superviso_firma = models.ImageField(upload_to='firmas/', null=True, blank=True)
    superviso_fecha = models.DateField()

    capturo_nombre = models.CharField(max_length=100)
    capturo_firma = models.ImageField(upload_to='firmas/', null=True, blank=True)
    capturo_fecha = models.DateField()
    
    facturo_nombre = models.CharField(max_length=100)
    facturo_firma = models.ImageField(upload_to='firmas/', null=True, blank=True)
    factura_numero = models.CharField(max_length=20, blank=True)
    facturo_fecha = models.DateField()

    autorizo_nombre = models.CharField(max_length=100)
    autorizo_firma = models.ImageField(upload_to='firmas/', null=True, blank=True)
    autorizo_fecha = models.DateField()

    empleado_asignado = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='servicios_asignados'
    )

    def __str__(self):
        return f"Servicio {self.otvm} - {self.obra.nombre} - {self.fecha}"

