from django import forms
from .models import Empleado

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = [
            'nombre', 'email', 'telefono', 'cargo',
            'domicilio', 'codigo_postal', 'rfc', 'anio_nacimiento', 'tipo_sangre'
        ]
