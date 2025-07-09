from django.shortcuts import render
from django.http import JsonResponse
from .models import MuestraBiologica, Especie

def catalogo(request):
    muestras = MuestraBiologica.objects.all()
    return render(request, 'catalogo/catalogo.html', {'muestras': muestras})

def lista_plantas(request):
    plantas = MuestraBiologica.objects.filter(tipo_muestra='PLANTA')
    return render(request, 'catalogo/lista_plantas.html', {'plantas': plantas})

def home(request):
    return render(request, 'mi_app/home.html')

def load_especies(request):
    """
    Vista AJAX para cargar especies según la familia seleccionada.
    Se usa en el formulario de plantas para filtrado dinámico.
    """
    familia_id = request.GET.get('familia_id')
    
    # Validación básica
    if not familia_id:
        return JsonResponse({'error': 'Parámetro familia_id requerido'}, status=400)
    
    try:
        especies = Especie.objects.filter(familia_id=familia_id).order_by('nombre')
        # Creamos las opciones HTML para el select
        options_html = '<option value="">Seleccione una especie...</option>'
        for especie in especies:
            options_html += f'<option value="{especie.id}">{especie.nombre}</option>'
        
        return JsonResponse({'options_html': options_html})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
@require_POST
def ajax_add_familia(request):
    nombre = request.POST.get('nombre')
    if not nombre:
        return JsonResponse({'error': 'Nombre requerido'}, status=400)
    
    familia = Familia.objects.create(nombre=nombre)
    return JsonResponse({
        'id': familia.id,
        'nombre': familia.nombre,
        'success': True
    })

@login_required
@require_POST
def ajax_add_especie(request):
    nombre = request.POST.get('nombre')
    familia_id = request.POST.get('familia_id')
    
    if not nombre or not familia_id:
        return JsonResponse({'error': 'Nombre y familia requeridos'}, status=400)
    
    try:
        especie = Especie.objects.create(
            nombre=nombre,
            familia_id=familia_id
        )
        return JsonResponse({
            'id': especie.id,
            'nombre': especie.nombre,
            'familia_id': especie.familia_id,
            'success': True
        })
    except Familia.DoesNotExist:
        return JsonResponse({'error': 'Familia no encontrada'}, status=400)
    
