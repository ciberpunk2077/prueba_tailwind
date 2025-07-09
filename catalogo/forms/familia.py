from django import forms
from ..models import Familia, Especie

class FamiliaForm(forms.ModelForm):
    class Meta:
        model = Familia
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class EspecieForm(forms.ModelForm):
    class Meta:
        model = Especie
        fields = ['nombre', 'familia', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'familia': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }