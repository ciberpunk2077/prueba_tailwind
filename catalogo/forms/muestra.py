
from django import forms
from ..models import MuestraBiologica

class MuestraBiologicaForm(forms.ModelForm):
    class Meta:
        model = MuestraBiologica
        fields = '__all__'
        

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Acepta pero no usa (o implementa lógica si es necesario)
        tipo_muestra = kwargs.pop('tipo_muestra', None)
        super().__init__(*args, **kwargs)  # Pasa los kwargs restantes al ModelForm
        # ... lógica específica ...