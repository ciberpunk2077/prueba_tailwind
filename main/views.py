from django.shortcuts import render
from catalogo.models import MuestraBiologica, Especie, Familia
from django.db.models import Count

# Create your views here.

def home(request):
    # Obtener estadísticas de las especies
    total_muestras = MuestraBiologica.objects.count()
    total_especies = Especie.objects.count()
    total_familias = Familia.objects.count()
    
    # Contar por tipo de muestra
    estadisticas_tipo = MuestraBiologica.objects.values('tipo_muestra').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Contar por familia (top 10)
    estadisticas_familia = MuestraBiologica.objects.values(
        'especie__familia__nombre'
    ).annotate(
        total=Count('id')
    ).filter(
        especie__familia__nombre__isnull=False
    ).order_by('-total')[:10]
    
    # Datos para la gráfica
    tipos_muestra = {
        'ALGA': 'Algas',
        'PLANTA': 'Plantas', 
        'FRUTOSEMILLA': 'Frutos y Semillas',
        'POLEN': 'Polen',
        'HELECHO': 'Helechos',
        'HONGO': 'Hongos'
    }
    
    datos_grafica = []
    for stat in estadisticas_tipo:
        tipo_nombre = tipos_muestra.get(stat['tipo_muestra'], stat['tipo_muestra'])
        datos_grafica.append({
            'tipo': tipo_nombre,
            'total': stat['total'],
            'porcentaje': round((stat['total'] / total_muestras * 100), 1) if total_muestras > 0 else 0
        })
    
    context = {
        'total_muestras': total_muestras,
        'total_especies': total_especies,
        'total_familias': total_familias,
        'estadisticas_tipo': estadisticas_tipo,
        'estadisticas_familia': estadisticas_familia,
        'datos_grafica': datos_grafica,
        'tipos_muestra': tipos_muestra
    }
    
    return render(request, 'main/home.html', context)

def about(request):
    return render(request, 'main/about.html')

def contact(request):
    return render(request, 'main/contact.html')

def datos(request):
    return render(request, 'main/datos.html')

def nosotros(request):
    return render(request, 'main/nosotros.html')

def presentacion(request):
    return render(request, 'main/presentacion.html')

def test_busqueda(request):
    """Vista de prueba para verificar el buscador"""
    # Obtener algunas muestras de prueba
    muestras = MuestraBiologica.objects.select_related('especie', 'especie__familia').all()[:5]
    especies = Especie.objects.select_related('familia').all()[:5]
    familias = Familia.objects.all()[:5]
    
    context = {
        'muestras': muestras,
        'especies': especies,
        'familias': familias,
        'total_muestras': MuestraBiologica.objects.count(),
        'total_especies': Especie.objects.count(),
        'total_familias': Familia.objects.count(),
    }
    
    return render(request, 'main/test_busqueda.html', context)