# catalogo/views/__init__.py
from .planta import PlantaCreateView, PlantaListView, PlantaDetailView
from .muestra import MuestraCreateView, MuestraListView  # etc
# from .familia import ajax_add_familia, ajax_add_especie

__all__ = [
    'PlantaCreateView',
    'PlantaListView',
    'PlantaDetailView',
    'MuestraCreateView',
    # ...
]