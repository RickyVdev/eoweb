from django import forms
from .models import Empleado, Cliente

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = [
            'id_personal',
            'nombre', 'email', 'telefono', 'puesto',
            'domicilio', 'codigo_postal', 'rfc', 'fecha_nacimiento', 'tipo_sangre'
        ]

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'clave', 'nombre', 'direccion', 'colonia', 'ciudad',
            'telefono', 'atencion_a','correo'
        ]    

        #'obra', 'localizacion', 
        labels = {
            'clave': 'Clave del Cliente',
            'nombre': 'Nombre o Razón Social',
            'direccion': 'Dirección',
            'colonia': 'Colonia',
            'ciudad': 'Ciudad',
            'telefono': 'Teléfono',
            'atencion_a': 'Atención a',
            #'obra': 'Nombre de la Obra o Proyecto',
            #'localizacion': 'Localización',
            'correo': 'Correo Electrónico',
        }
        widgets = {
            'clave': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'colonia': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'atencion_a': forms.TextInput(attrs={'class': 'form-control'}),
            #'obra': forms.TextInput(attrs={'class': 'form-control'}),
            #'localizacion': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean_telefono(self):
            telefono = self.cleaned_data.get('telefono')
            if not telefono.isdigit():
                raise forms.ValidationError("El teléfono debe contener solo números.")
            return telefono