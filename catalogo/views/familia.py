from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from ..models import Familia, Especie
from catalogo.forms.familia import FamiliaForm, EspecieForm

class FamiliaCreateView(CreateView):
    model = Familia
    form_class = FamiliaForm
    template_name = 'catalogo/familia_form.html'
    success_url = reverse_lazy('catalogo:familia_list')

class FamiliaUpdateView(UpdateView):
    model = Familia
    form_class = FamiliaForm
    template_name = 'catalogo/familia_form.html'
    success_url = reverse_lazy('catalogo:familia_list')

class FamiliaListView(ListView):
    model = Familia
    template_name = 'catalogo/familia_list.html'
    context_object_name = 'familias'

class EspecieCreateView(CreateView):
    model = Especie
    form_class = EspecieForm
    template_name = 'catalogo/especie_form.html'
    success_url = reverse_lazy('catalogo:especie_list')

class EspecieUpdateView(UpdateView):
    model = Especie
    form_class = EspecieForm
    template_name = 'catalogo/especie_form.html'
    success_url = reverse_lazy('catalogo:especie_list')

class EspecieListView(ListView):
    model = Especie
    template_name = 'catalogo/especie_list.html'
    context_object_name = 'especies'


@login_required
@require_POST
def ajax_add_familia(request):
    nombre = request.POST.get('nombre')
    descripcion = request.POST.get('descripcion', '')
    
    if not nombre:
        return JsonResponse({'error': 'Nombre requerido'}, status=400)
    
    familia = Familia.objects.create(nombre=nombre, descripcion=descripcion)
    return JsonResponse({
        'id': familia.id,
        'nombre': familia.nombre,
        'descripcion': familia.descripcion,
        'success': True
    })

@login_required
@require_POST
def ajax_add_especie(request):
    nombre = request.POST.get('nombre')
    familia_id = request.POST.get('familia_id')
    descripcion = request.POST.get('descripcion', '')
    
    if not nombre or not familia_id:
        return JsonResponse({'error': 'Nombre y familia requeridos'}, status=400)
    
    try:
        especie = Especie.objects.create(
            nombre=nombre,
            familia_id=familia_id,
            descripcion=descripcion
        )
        return JsonResponse({
            'id': especie.id,
            'nombre': especie.nombre,
            'familia_id': especie.familia_id,
            'descripcion': especie.descripcion,
            'success': True
        })
    except Familia.DoesNotExist:
        return JsonResponse({'error': 'Familia no encontrada'}, status=400)
    

