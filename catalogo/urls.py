from django.urls import path

from .views.planta import (
    PlantaCreateView, 
    PlantaListView, 
    PlantaDetailView,
    PlantaUpdateView,
    PlantaDeleteView, load_especies,)
from .views.alga import *
from .views.fruto import *
from .views.polen import *
from .views.helecho import *
from .views.hongo import *
from .views.familia import (  # Cambia este import
    FamiliaCreateView, FamiliaUpdateView, FamiliaListView,
    EspecieCreateView, EspecieUpdateView, EspecieListView, ajax_add_familia, ajax_add_especie
)
from .views.muestra import MuestraListView
from catalogo.views.buscar import buscar_muestras, get_especies


app_name = 'catalogo'

urlpatterns = [

    path('buscar/', buscar_muestras, name='buscar_muestras'),
    path('get_especies/', get_especies, name='get_especies'),

    # URLs para Familia
    path('familia/', FamiliaListView.as_view(), name='familia_list'),
    path('familia/nueva/', FamiliaCreateView.as_view(), name='familia_create'),
    path('familia/editar/<int:pk>/', FamiliaUpdateView.as_view(), name='familia_update'),
    
    # URLs para Especie
    path('especie/', EspecieListView.as_view(), name='especie_list'),
    path('especie/nueva/', EspecieCreateView.as_view(), name='especie_create'),
    path('especie/editar/<int:pk>/', EspecieUpdateView.as_view(), name='especie_update'),

    # URLs para algas
    path('algas/', AlgaListView.as_view(), name='alga-list'),#muestran todas la algas
    path('algas/nueva/', AlgaCreateView.as_view(), name='alga-create'),#formulario de algas
    path('algas/<int:pk>/', AlgaDetailView.as_view(), name='alga-detail'),#muestra la alga a detalle
    path('algas/<int:pk>/editar/', AlgaUpdateView.as_view(), name='alga-update'),#actualiza la informacion
    path('algas/<int:pk>/eliminar/', AlgaDeleteView.as_view(), name='alga-delete'),#elimina el alga

    # URLs para plantas
    path('plantas/', PlantaListView.as_view(), name='planta-list'),
    path('plantas/nueva/', PlantaCreateView.as_view(), name='planta-create'),
    path('plantas/<int:pk>/', PlantaDetailView.as_view(), name='planta-detail'),
    path('plantas/<int:pk>/editar/', PlantaUpdateView.as_view(), name='planta-update'),
    path('plantas/<int:pk>/eliminar/', PlantaDeleteView.as_view(), name='planta-delete'),

    # URLs frutos y semillas
    path('frutosemilla/', FrutoListView.as_view(), name='fruto-list'),
    path('frutosemilla/nueva/', FrutoCreateView.as_view(), name='fruto-create'),
    path('frutosemilla/<int:pk>/', FrutoDetailView.as_view(), name='fruto-detail'),
    path('frutosemilla/<int:pk>/editar/', FrutoUpdateView.as_view(), name='fruto-update'),
    path('frutosemilla/<int:pk>/eliminar/', FrutoDeleteView.as_view(), name='fruto-delete'),

# URLs polen
    path('polen/', PolenListView.as_view(), name='polen-list'),
    path('polen/nueva/', PolenCreateView.as_view(), name='polen-create'),
    path('polen/<int:pk>/', PolenDetailView.as_view(), name='polen-detail'),
    path('polen/<int:pk>/editar/', PolenUpdateView.as_view(), name='polen-update'),
    path('polen/<int:pk>/eliminar/', PolenDeleteView.as_view(), name='polen-delete'),

# URLs helecho
    path('helecho/', HelechoListView.as_view(), name='helecho-list'),
    path('helecho/nueva/', HelechoCreateView.as_view(), name='helecho-create'),
    path('helecho/<int:pk>/', HelechoDetailView.as_view(), name='helecho-detail'),
    path('helecho/<int:pk>/editar/', HelechoUpdateView.as_view(), name='helecho-update'),
    path('helecho/<int:pk>/eliminar/', HelechoDeleteView.as_view(), name='helecho-delete'),

# URLs hongo
    path('hongo/', HongoListView.as_view(), name='hongo-list'),
    path('hongo/nueva/', HongoCreateView.as_view(), name='hongo-create'),
    path('hongo/<int:pk>/', HongoDetailView.as_view(), name='hongo-detail'),
    path('hongo/<int:pk>/editar/', HongoUpdateView.as_view(), name='hongo-update'),
    path('hongo/<int:pk>/eliminar/', HongoDeleteView.as_view(), name='hongo-delete'),

    #URLs especie
    path('ajax/add-familia/', ajax_add_familia, name='ajax-add-familia'),
    path('ajax/add-especie/', ajax_add_especie, name='ajax-add-especie'),
    path('ajax/load-especies/', load_especies, name='ajax_load_especies'),
    
    # URLs generales para muestras (opcional mantenerlas)
    path('muestras/', MuestraListView.as_view(), name='muestra-list'),
    path('muestras/nueva/', MuestraCreateView.as_view(), name='muestra-create'),
    path('muestras/<int:pk>/', MuestraDetailView.as_view(), name='muestra-detail'),
    path('muestras/<int:pk>/editar/', MuestraUpdateView.as_view(), name='muestra-update'),
    path('muestras/<int:pk>/eliminar/', MuestraDeleteView.as_view(), name='muestra-delete'),
    # ... otras URLs ...
]