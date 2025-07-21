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
        def clean_telefono(self):
            telefono = self.cleaned_data.get('telefono')
            if not telefono.isdigit():
                raise forms.ValidationError("El teléfono debe contener solamente números.")
            return telefono

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'clave', 'nombre',
            'calle', 'numero_exterior', 'numero_interior',
            'colonia', 'ciudad',
            'telefono', 'extension', 'telefono2', 'movil',
            'atencion_a', 'correo'
        ]  

        #'obra', 'localizacion', 
        labels = {
            'clave': 'Clave del Cliente',
            'nombre': 'Nombre o Razón Social',
            'calle': 'Calle',
            'numero_exterior': 'Número exterior',
            'numero_interior': 'Número interior',
            'colonia': 'Colonia',
            'ciudad': 'Ciudad',
            'telefono': 'Teléfono 1',
            'extension': 'Extensión',
            'telefono2': 'Teléfono 2',
            'movil': 'Móvil',
            'atencion_a': 'Atención a',
            'correo': 'Correo Electrónico',
        }
        widgets = {
            'clave': forms.TextInput(attrs={'class': 'form-control text-center', 'readonly': 'readonly'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'calle': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_exterior': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_interior': forms.TextInput(attrs={'class': 'form-control'}),
            'colonia': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'extension': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono2': forms.TextInput(attrs={'class': 'form-control'}),
            'movil': forms.TextInput(attrs={'class': 'form-control'}),
            'atencion_a': forms.TextInput(attrs={'class': 'form-control'}),
            #'obra': forms.TextInput(attrs={'class': 'form-control'}),
            #'localizacion': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
        }

        
    
    '''def clean_telefono(self):
            telefono = self.cleaned_data.get('telefono')
            if not telefono.isdigit():
                raise forms.ValidationError("El teléfono debe contener solamente números.")
            return telefono'''