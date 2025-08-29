from django import forms
from .models import Empleado, Cliente, Servicio, Obra
from django.contrib.auth.models import User

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
            'colonia', 'codigo_postal', 'ciudad',
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
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
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

        
    def clean_numero_exterior(self):
        dato = self.cleaned_data['numero_exterior']
        if dato and not dato.isdigit():
            raise forms.ValidationError("Solo se permiten números.")
        return dato

    def clean_numero_interior(self):
        dato = self.cleaned_data['numero_interior']
        if dato and not dato.isdigit():
            raise forms.ValidationError("Solo se permiten números.")
        return dato
    
    def clean_telefono(self):
            telefono = self.cleaned_data.get('telefono')
            if not telefono.isdigit():
                raise forms.ValidationError("El teléfono debe contener solamente números.")
            return telefono
    
    def clean_telefono2(self):
            telefono2 = self.cleaned_data.get('telefono2')
            if telefono2 and not telefono2.isdigit():
                raise forms.ValidationError("El teléfono debe contener solamente números.")
            return telefono2
    
    def clean_movil(self):
            movil = self.cleaned_data.get('movil')
            if movil and not movil.isdigit():
                raise forms.ValidationError("El teléfono debe contener solamente números.")
            return movil

class ObraForm(forms.ModelForm):
    class Meta:
        model = Obra
        fields = ['clave_obra', 'nombre', 'atencion_a', 'localizacion']
        labels = {
            'clave_obra': 'ID de Obra',
            'nombre': 'Obra',
            'atencion_a': 'Atención a',
            'localizacion': 'Localización',
        }
        widgets = {
            'clave_obra': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'atencion_a': forms.TextInput(attrs={'class': 'form-control'}),
            'localizacion': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

class ServicioForm(forms.ModelForm):
    empleado_asignado = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Empleado'),
        required=False,
        label="Empleado Asignado",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
        model = Servicio
        fields = [
            'fecha', 'otvm', 'llegada', 'termino',
            'solicitante', 'preguntar_por', 'trabajo_realizado', 'cantidad', 'observaciones',
            'vobo_cliente_nombre', 'lab_nombre',
            'superviso_nombre', 'superviso_fecha',
            'capturo_nombre', 'capturo_fecha',
            'facturo_nombre', 'factura_numero', 'facturo_fecha',
            'autorizo_nombre', 'autorizo_fecha',
            'empleado_asignado',
        ]
        widgets = {
            'fecha': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'llegada': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'termino': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'otvm': forms.TextInput(attrs={'class': 'form-control'}),
            'solicitante': forms.TextInput(attrs={'class': 'form-control'}),
            'preguntar_por': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vobo_cliente_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'lab_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'superviso_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'superviso_fecha': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'capturo_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'capturo_fecha': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'facturo_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'factura_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'facturo_fecha': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'autorizo_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'autorizo_fecha': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'empleado_asignado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limitar la selección solo a usuarios con grupo "Empleado"
        if 'empleado_asignado' in self.fields:
            self.fields['empleado_asignado'].queryset = User.objects.filter(groups__name="Empleado")
            self.fields['empleado_asignado'].widget.attrs.update({'class': 'form-select'})

    '''def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Esto permite que Django parsee correctamente las fechas del input
        date_fields = [
            'fecha', 'superviso_fecha', 'capturo_fecha', 'facturo_fecha', 'autorizo_fecha'
        ]

        self.fields['empleado_asignado'].queryset = User.objects.filter(groups__name="Empleado")

        for field in date_fields:
            self.fields[field].input_formats = ['%Y-%m-%d']'''
        
        
