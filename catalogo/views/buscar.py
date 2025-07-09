from django.db.models import Q
from catalogo.models import MuestraBiologica, Especie, Familia
from django.shortcuts import render
from django.http import JsonResponse

def buscar_muestras(request):
    query = request.GET.get('q', '').strip()
    familia_id = request.GET.get('familia')
    especie_id = request.GET.get('especie')
    tipo = request.GET.get('tipo')
    
    # Base query - obtener todas las muestras
    resultados = MuestraBiologica.objects.select_related('especie', 'especie__familia').all()
    
    # Búsqueda full-text mejorada
    if query:
        # Buscar en múltiples campos de las muestras
        resultados = resultados.filter(
            Q(nombre_cientifico__icontains=query) |
            Q(nombre_comun__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(numero_recolecta__icontains=query) |
            Q(nombre_colector__icontains=query) |
            Q(colonia__icontains=query) |
            Q(localidad__icontains=query) |
            # Buscar en especie
            Q(especie__nombre__icontains=query) |
            Q(especie__descripcion__icontains=query) |
            # Buscar en familia
            Q(especie__familia__nombre__icontains=query) |
            Q(especie__familia__descripcion__icontains=query)
        ).distinct()
    
    # Filtros adicionales
    if familia_id:
        resultados = resultados.filter(especie__familia_id=familia_id)
    if especie_id:
        resultados = resultados.filter(especie_id=especie_id)
    if tipo:
        resultados = resultados.filter(tipo_muestra=tipo)

    # Ordenar por nombre científico
    resultados = resultados.order_by('nombre_cientifico')

    # Obtener estadísticas de búsqueda
    total_resultados = resultados.count()
    estadisticas = {
        'plantas': resultados.filter(tipo_muestra='PLANTA').count(),
        'algas': resultados.filter(tipo_muestra='ALGA').count(),
        'hongos': resultados.filter(tipo_muestra='HONGO').count(),
        'helechos': resultados.filter(tipo_muestra='HELECHO').count(),
        'frutos': resultados.filter(tipo_muestra='FRUTOSEMILLA').count(),
        'polen': resultados.filter(tipo_muestra='POLEN').count(),
    }

    context = {
        'resultados': resultados,
        'query': query,
        'total_resultados': total_resultados,
        'estadisticas': estadisticas,
        'tipos_muestra': MuestraBiologica.TIPO_MUESTRA_CHOICES
    }

    # Si es una petición AJAX, devolver solo el partial
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'catalogo/buscar/partials/lista_resultados.html', context)
    
    # Si no hay resultados y hay query, mostrar sugerencias
    if query and total_resultados == 0:
        # Buscar especies similares
        especies_similares = Especie.objects.filter(
            Q(nombre__icontains=query) |
            Q(familia__nombre__icontains=query)
        )[:5]
        
        # Buscar familias similares
        familias_similares = Familia.objects.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query)
        )[:5]
        
        context.update({
            'especies_similares': especies_similares,
            'familias_similares': familias_similares,
            'sin_resultados': True
        })
    
    return render(request, 'catalogo/buscar/resultados.html', context)

def get_especies(request):
    familia_id = request.GET.get('familia_id')
    if not familia_id:
        return JsonResponse([], safe=False)
        
    especies = Especie.objects.filter(familia_id=familia_id).values('id', 'nombre')
    return JsonResponse(list(especies), safe=False)

def buscar_sugerencias(request):
    """API para obtener sugerencias de búsqueda"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    sugerencias = []
    
    # Buscar en especies
    especies = Especie.objects.filter(
        Q(nombre__icontains=query) |
        Q(familia__nombre__icontains=query)
    ).select_related('familia')[:10]
    
    for especie in especies:
        sugerencias.append({
            'tipo': 'especie',
            'nombre': especie.nombre,
            'familia': especie.familia.nombre if especie.familia else 'Sin familia',
            'url': f'/catalogo/buscar/?q={especie.nombre}'
        })
    
    # Buscar en familias
    familias = Familia.objects.filter(
        Q(nombre__icontains=query) |
        Q(descripcion__icontains=query)
    )[:5]
    
    for familia in familias:
        sugerencias.append({
            'tipo': 'familia',
            'nombre': familia.nombre,
            'descripcion': familia.descripcion[:100] + '...' if len(familia.descripcion) > 100 else familia.descripcion,
            'url': f'/catalogo/buscar/?q={familia.nombre}'
        })
    
    # Buscar en muestras
    muestras = MuestraBiologica.objects.filter(
        Q(nombre_cientifico__icontains=query) |
        Q(nombre_comun__icontains=query)
    ).select_related('especie', 'especie__familia')[:5]
    
    for muestra in muestras:
        sugerencias.append({
            'tipo': 'muestra',
            'nombre': muestra.nombre_cientifico,
            'nombre_comun': muestra.nombre_comun,
            'tipo_muestra': muestra.get_tipo_muestra_display(),
            'url': f'/catalogo/{muestra.tipo_muestra.lower()}-detail/{muestra.pk}/'
        })
    
    return JsonResponse(sugerencias, safe=False)