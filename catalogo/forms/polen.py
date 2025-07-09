from django import forms
from ..models import MuestraBiologica, Especie, Familia, Municipio
from .muestra import MuestraBiologicaForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

class PolenForm(MuestraBiologicaForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        tipo_muestra = kwargs.pop('tipo_muestra', None)
        super().__init__(*args, **kwargs)
    # Campo imagen personalizado

        
        self.fields['imagen'].widget = forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'id_imagen'
        })
        self.fields['imagen'].required = True

        # Manejo de la familia y especie para casos de edición
        if self.instance.pk:  # Si es una edición
            # Si tiene especie, establece la familia y el queryset de especies
            if self.instance.especie:
                self.fields['familia'].initial = self.instance.especie.familia_id
                self.fields['especie'].queryset = Especie.objects.filter(
                    familia_id=self.instance.especie.familia_id
                ).order_by('nombre')
            # Si no tiene especie pero sí tiene familia directa
            elif self.instance.familia:
                self.fields['familia'].initial = self.instance.familia_id
                self.fields['especie'].queryset = Especie.objects.filter(
                    familia_id=self.instance.familia_id
                ).order_by('nombre')
        
        # Manejo de POST (cuando se envía el formulario)
        if 'familia' in self.data:
            try:
                familia_id = int(self.data.get('familia'))
                self.fields['especie'].queryset = Especie.objects.filter(
                    familia_id=familia_id
                ).order_by('nombre')
            except (ValueError, TypeError):
                pass
        
        # Configuración de HTMX para la funcionalidad dinámica
        self.fields['familia'].widget.attrs.update({
            'hx-get': '/catalogo/ajax/load-especies/',
            'hx-target': '#id_especie',
            'hx-trigger': 'change',
            'hx-swap': 'innerHTML',
            'hx-vals': '{"familia_id": this.value}'
        })

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Asigna automáticamente la familia desde la especie si existe
        if self.cleaned_data.get('especie'):
            instance.familia = self.cleaned_data['especie'].familia
        # Si no hay especie pero sí se seleccionó familia directamente
        elif self.cleaned_data.get('familia'):
            instance.familia = self.cleaned_data['familia']
        
        if commit:
            instance.save()
        
        return instance
   
    

    # Campo familia (solo una definición)
    familia = forms.ModelChoiceField(
        queryset=Familia.objects.all().order_by('nombre'),
        label="Familia",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'hx-get': '/catalogo/ajax/load-especies/',
            'hx-target': '#id_especie',
            'hx-trigger': 'change',
        })
    )

    especie = forms.ModelChoiceField(
        queryset=Especie.objects.none(),
        label="Especie",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_especie',
        }),
        empty_label="Seleccione una especie"
    )

    municipio = forms.ModelChoiceField(
        queryset=Municipio.objects.all().order_by('nombre'),
        label="Municipio",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Seleccione un municipio'
        }),
        empty_label="---------"
    )
    
    class Meta(MuestraBiologicaForm.Meta):
        fields = [
            'tipo_muestra', 'nombre_cientifico', 'nombre_comun', 'familia', 'especie',
            'genero', 'fecha', 'numero_recolecta', 'municipio',  'imagen', 'colonia', 
            'localidad', 'descripcion', 'nombre_colector','latitud', 'longitud'
        ]
        widgets = {
            'tipo_muestra': forms.HiddenInput(),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'latitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 17.98996809279243',
                'step': 'any',
                'id': 'latitud'
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: -92.97312461534396',
                'step': 'any',
                'id': 'longitud'
            }),

            'nombre_cientifico': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Rosa rubiginosa'}),
            'nombre_comun': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Rosa mosqueta'}),
            'numero_recolecta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: INV-123'}),
            'colonia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: san jose'}),
            'localidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: villahermosa'}),
            'municipio': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Ej: centro'}),
            'nombre_colector': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: El PEPE'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'tipo_muestra': forms.HiddenInput(),
            

            # No definimos 'imagen' aquí porque ya está definido arriba
        }

    

    def clean(self):
        cleaned_data = super().clean()
        familia = cleaned_data.get('familia')
        especie = cleaned_data.get('especie')

        # if not self.instance.pk or 'imagen' in self.changed_data:
        #     if not cleaned_data.get('imagen'):
        #         raise forms.ValidationError({'imagen': 'Debe subir una imagen de la planta'})
        
        if familia and especie and especie.familia != familia:
            raise forms.ValidationError(
                "La especie seleccionada no pertenece a la familia elegida."
            )
        
        return cleaned_data