import logging
from django.urls import reverse_lazy
from django.contrib import messages
from ..forms.alga import AlgaForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from ..models import Especie, Familia
from .muestra import MuestraCreateView, MuestraListView, MuestraDetailView, MuestraUpdateView, MuestraDeleteView

logger = logging.getLogger(__name__)


class AlgaCreateView(MuestraCreateView):
    """
    Vista especializada para crear muestras de tipo PLANTA
    """
    form_class = AlgaForm
    tipo_fijo = 'ALGA'
    template_name = 'catalogo/alga_form.html'
    
    def get_form_kwargs(self):
        """Asegura que el tipo PLANTA se pase al formulario"""
        kwargs = super().get_form_kwargs()
        kwargs['tipo_muestra'] = self.tipo_fijo
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo_pagina': "Nueva Alga",
            'es_alga': True,
            'subtitulo': "Complete los datos de la alga recolectada"
        })
        return context
    
    def get_success_url(self):
        return reverse_lazy('catalogo:alga_list')

    def form_valid(self, form):
         # Verificar que se haya subido una imagen
        # if 'imagen' not in self.request.FILES:
        #     form.add_error('imagen', 'Debe subir una imagen de la muestra')
        #     return self.form_invalid(form)
            
        
        # Asigna automáticamente la familia desde la especie si es necesario
        if form.cleaned_data.get('especie') and not form.cleaned_data.get('familia'):
            form.instance.familia = form.cleaned_data['especie'].familia
            
        # Guardar el objeto
        self.object = form.save()
        
        # Debug: Verificar que la imagen se guardó
        print(f"Imagen guardada en: {self.object.imagen.path}")
        print(f"URL de la imagen: {self.object.imagen.url}")
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('catalogo:alga-list')


class AlgaListView(MuestraListView):
    """Listado específico para algas"""
    template_name = 'catalogo/alga_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(tipo_muestra='ALGA').select_related(
            'especie', 'especie__familia', 'municipio'
        )
        
        # Filtro por familia
        familia_id = self.request.GET.get('familia')
        if familia_id and familia_id != '':
            queryset = queryset.filter(especie__familia_id=familia_id)
        
        # Debug: Imprimir información sobre los datos
        print(f"DEBUG AlgaListView - Total algas encontradas: {queryset.count()}")
        for alga in queryset[:3]:  # Mostrar los primeros 3
            print(f"DEBUG - ID: {alga.id}, Nombre científico: '{alga.nombre_cientifico}', Especie: {alga.especie}")
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todas las familias que tienen algas
        familias = Familia.objects.filter(
            especie__muestrabiologica__tipo_muestra='ALGA'
        ).distinct().order_by('nombre')
        
        context.update({
            'titulo_pagina': "Listado de Algas",
            'subtitulo': "Algas registradas en el sistema",
            'familias': familias,
            'familia_seleccionada': self.request.GET.get('familia', '')
        })
        return context


class AlgaDetailView(MuestraDetailView):
    """Detalle específico para plantas"""
    template_name = 'catalogo/alga_detail.html'
    context_object_name = 'alga'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        alga = self.get_object()
        context.update({
            'titulo_pagina': f"Detalle de {alga.nombre_cientifico}",
            'es_alga': True,
            'subtitulo': "Información detallada de la planta"
        })
        return context


class AlgaUpdateView(MuestraUpdateView):
    """Vista para editar plantas"""
    template_name = 'catalogo/alga_form.html'
    form_class = AlgaForm
    # tipo_fijo = 'ALGA'
    success_url = reverse_lazy('catalogo:alga-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tipo_muestra'] = 'ALGA'
        return kwargs

        # Asegúrate de pasar la instancia existente al formulario
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo_pagina': f"Editar {self.object.nombre_cientifico}",
            'es_alga': True,
        })
        return context
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo_pagina': f"Editar {self.object.nombre_cientifico}",
            'es_alga': True,
            'subtitulo': "Editar los datos de la alga"
        })
        return context


class AlgaDeleteView(MuestraDeleteView):
    """Vista para eliminar plantas"""
    success_url = reverse_lazy('catalogo:alga-list')
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Alga eliminada correctamente")

        alga = self.get_object()
        
        if alga.imagen:  # Si hay una imagen, bórrala del sistema de archivos
            alga.imagen.delete(save=False)
        
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Alga eliminada correctamente")  # Mensaje de confirmación
        return response


def load_especies(request):
    familia_id = request.GET.get('familia') or request.GET.get('familia_id')
    
    if not familia_id or familia_id == 'undefined':
        return HttpResponse('<option value="">---------</option>')
            
    try:
        especies = Especie.objects.filter(familia_id=int(familia_id)).order_by('nombre')
        options = ''.join(f'<option value="{e.id}">{e.nombre}</option>' for e in especies)
        return HttpResponse(options)
    except (ValueError, TypeError, Especie.DoesNotExist) as e:
        logger.error(f"Error cargando especies: {str(e)}")
        return HttpResponse('<option value="">Error cargando especies</option>')
    

