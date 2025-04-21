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
        fields = ['especie', 'fecha_siembra', 'latitud', 'longitud', 'estado']
        widgets = {
            'especie': forms.Select(attrs={'class': 'form-select'}),  # ✅ CORREGIDO
            'fecha_siembra': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'latitud': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Esto asegura que el queryset esté bien definido
        self.fields['especie'].queryset = Especie.objects.all()

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']