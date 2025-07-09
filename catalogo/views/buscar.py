from django.db.models import Q
from catalogo.models import MuestraBiologica
from django.shortcuts import render
from django.http import JsonResponse
from catalogo.models import Especie

def buscar_muestras(request):
    query = request.GET.get('q', '')
    familia_id = request.GET.get('familia')
    especie_id = request.GET.get('especie')
    tipo = request.GET.get('tipo')  # Filtro por tipo (alga, hongo, etc.)
    
    # Base query
    resultados = MuestraBiologica.objects.all()
    
    # Búsqueda full-text
    if query:
        resultados = resultados.filter(
            Q(nombre_cientifico__icontains=query) |
            Q(nombre_comun__icontains=query) |
            Q(especie__familia__nombre__icontains=query) |
            Q(especie__nombre__icontains=query)
        )
    
    # Filtro por tipo (opcional)
    if familia_id:
        resultados = resultados.filter(especie__familia_id=familia_id)
    if especie_id:
        resultados = resultados.filter(especie_id=especie_id)
    if tipo:
        resultados = resultados.filter(tipo_muestra=tipo)

    context = {
        'resultados': resultados,
        'query': query,
        'tipos_muestra': MuestraBiologica.TIPO_MUESTRA_CHOICES
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'catalogo/buscar/partials/lista_resultados.html', context)
    
    return render(request, 'catalogo/buscar/resultados.html', context)



def get_especies(request):
    familia_id = request.GET.get('familia_id')
    if not familia_id:
        return JsonResponse([], safe=False)
        
    especies = Especie.objects.filter(familia_id=familia_id).values('id', 'nombre')
    return JsonResponse(list(especies), safe=False)