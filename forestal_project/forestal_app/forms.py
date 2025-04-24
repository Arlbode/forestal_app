from django import forms
from .models import Postura
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Especie


class EspecieForm(forms.ModelForm):
    class Meta:
        model = Especie
        fields = ['nombre_cientifico', 'nombre_comun']
        widgets = {
            'nombre_cientifico': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_comun': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PosturaForm(forms.ModelForm):
    class Meta:
        model = Postura
        fields = ['especie', 'fecha_adquisicion', 'fecha_siembra', 'latitud', 'longitud', 'estado']
        widgets = {
            'especie': forms.Select(attrs={'class': 'form-select'}),
            'fecha_adquisicion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_siembra': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'latitud': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['especie'].queryset = Especie.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        fecha_siembra = cleaned_data.get('fecha_siembra')
        fecha_adquisicion = cleaned_data.get('fecha_adquisicion')

        # Validar que no se pueda poner estado 'Sembrada' sin fecha de siembra
        if estado == 'Sembrada' and not fecha_siembra:
            self.add_error('fecha_siembra', 'Debe especificar la fecha de siembra para marcar como "Sembrada".')

        # Validar que no se pueda poner fecha de siembra si el estado no es 'Sembrada'
        if fecha_siembra and estado != 'Sembrada':
            self.add_error('estado', 'El estado debe ser "Sembrada" si se especifica la fecha de siembra.')

        # Validar que fecha_siembra no sea menor que fecha_adquisicion
        if fecha_siembra and fecha_adquisicion and fecha_siembra < fecha_adquisicion:
            self.add_error('fecha_siembra', 'La fecha de siembra no puede ser anterior a la fecha de adquisición.')


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']