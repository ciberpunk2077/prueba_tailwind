from django import forms
from catalogo.models import MuestraBiologica, Familia, Especie

class BusquedaForm(forms.Form):
    q = forms.CharField(
        label="Término general",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre, familia, especie...'})
    )
    familia = forms.ModelChoiceField(
        label="Filtrar por familia",
        queryset=Familia.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    especie = forms.ModelChoiceField(
        label="Filtrar por especie",
        queryset=Especie.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tipo = forms.ChoiceField(
        label="Tipo muestra",
        choices=MuestraBiologica.TIPO_MUESTRA_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )