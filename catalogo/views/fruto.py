

import logging
from django.urls import reverse_lazy
from django.contrib import messages
from ..forms.fruto import FrutoForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from ..models import Especie, Familia
from .muestra import MuestraCreateView, MuestraListView, MuestraDetailView, MuestraUpdateView, MuestraDeleteView

logger = logging.getLogger(__name__)


class FrutoCreateView(MuestraCreateView):
    """
    Vista especializada para crear muestras de tipo PLANTA
    """
    form_class = FrutoForm
    tipo_fijo = 'FRUTOSEMILLA'
    template_name = 'catalogo/fruto_form.html'
    
    def get_form_kwargs(self):
        """Asegura que el tipo PLANTA se pase al formulario"""
        kwargs = super().get_form_kwargs()
        kwargs['tipo_muestra'] = self.tipo_fijo
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo_pagina': "Nueva Fruto o semilla",
            'es_fruto': True,
            'subtitulo': "Complete los datos de la fruto recolectada"
        })
        return context
    
    def get_success_url(self):
        return reverse_lazy('catalogo:fruto-list')

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
        return reverse_lazy('catalogo:fruto-list')


class FrutoListView(MuestraListView):
    """Listado específico para plantas"""
    template_name = 'catalogo/fruto_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(tipo_muestra='FRUTOSEMILLA').select_related(
            'familia', 'especie', 'especie__familia', 'municipio'
        )
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(tipo_muestra='FRUTOSEMILLA').select_related(
            'especie', 'especie__familia', 'municipio'
        )
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context.update({
    #         'titulo_pagina': "Listado de Plantas",
    #         'subtitulo': "Plantas registradas en el sistema"
    #     })
    #     return context


class FrutoDetailView(MuestraDetailView):
    """Detalle específico para plantas"""
    template_name = 'catalogo/fruto_detail.html'
    context_object_name = 'fruto'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fruto = self.get_object()
        context.update({
            'titulo_pagina': f"Detalle de {fruto.nombre_cientifico}",
            'es_fruto': True,
            'subtitulo': "Información detallada de la planta"
        })
        return context


class FrutoUpdateView(MuestraUpdateView):
    """Vista para editar plantas"""
    template_name = 'catalogo/fruto_form.html'
    form_class = FrutoForm
    # tipo_fijo = 'FRUTOSEMILLA'
    success_url = reverse_lazy('catalogo:fruto-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tipo_muestra'] = 'FRUTOSEMILLA'
        return kwargs

        # Asegúrate de pasar la instancia existente al formulario
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo_pagina': f"Editar {self.object.nombre_cientifico}",
            'es_fruto': True,
        })
        return context
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo_pagina': f"Editar {self.object.nombre_cientifico}",
            'es_fruto': True,
            'subtitulo': "Editar los datos de la fruta"
        })
        return context


class FrutoDeleteView(MuestraDeleteView):
    """Vista para eliminar plantas"""
    success_url = reverse_lazy('catalogo:fruto-list')
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Fruto eliminada correctamente")

        fruto = self.get_object()
        
        if fruto.imagen:  # Si hay una imagen, bórrala del sistema de archivos
            fruto.imagen.delete(save=False)
        
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Fruto eliminada correctamente")  # Mensaje de confirmación
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
    

