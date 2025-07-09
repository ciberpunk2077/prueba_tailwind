from django.contrib import admin
from .models import MuestraBiologica, Especie, Familia, Municipio

# Register your models here.
admin.site.register(MuestraBiologica)
admin.site.register(Especie)
admin.site.register(Familia)
admin.site.register(Municipio)