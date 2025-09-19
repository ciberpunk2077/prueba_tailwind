from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.contrib import messages

from catalogo.models import Collection, CollectionItem, MuestraBiologica
from catalogo.forms.collection import CollectionForm, MoveItemForm


@method_decorator(login_required, name='dispatch')
class CollectionListView(ListView):
    model = Collection
    template_name = 'catalogo/collections/list.html'
    context_object_name = 'collections'

    def get_queryset(self):
        return Collection.objects.filter(owner=self.request.user).order_by('-is_default', 'name')


@method_decorator(login_required, name='dispatch')
class CollectionDetailView(DetailView):
    model = Collection
    template_name = 'catalogo/collections/detail.html'
    context_object_name = 'collection'

    def get_queryset(self):
        return Collection.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir todas las colecciones del usuario para el modal de mover elementos
        context['collections'] = Collection.objects.filter(owner=self.request.user)
        return context


def _get_or_create_default_collection(user: "User") -> Collection:
    default_collection = Collection.objects.filter(owner=user, is_default=True).first()
    if default_collection:
        return default_collection
    # Si no existe, crear una por defecto
    return Collection.objects.create(owner=user, name='Mi herbario', is_default=True)


@login_required
@require_POST
def toggle_favorite(request):
    muestra_id = request.POST.get('muestra_id')
    collection_id = request.POST.get('collection_id')

    if not muestra_id:
        return JsonResponse({'ok': False, 'error': 'muestra_id requerido'}, status=400)

    muestra = get_object_or_404(MuestraBiologica, pk=muestra_id)

    if collection_id:
        collection = get_object_or_404(Collection, pk=collection_id)
        if collection.owner_id != request.user.id:
            return HttpResponseForbidden('No autorizado')
    else:
        collection = _get_or_create_default_collection(request.user)

    item = CollectionItem.objects.filter(collection=collection, muestra=muestra).first()
    if item:
        item.delete()
        return JsonResponse({'ok': True, 'favorited': False})
    else:
        CollectionItem.objects.create(collection=collection, muestra=muestra)
        return JsonResponse({'ok': True, 'favorited': True})


@method_decorator(login_required, name='dispatch')
class CollectionCreateView(CreateView):
    model = Collection
    form_class = CollectionForm
    template_name = 'catalogo/collections/create.html'
    success_url = reverse_lazy('catalogo:collection-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f'Colección "{form.instance.name}" creada exitosamente.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class CollectionUpdateView(UpdateView):
    model = Collection
    form_class = CollectionForm
    template_name = 'catalogo/collections/edit.html'
    success_url = reverse_lazy('catalogo:collection-list')

    def get_queryset(self):
        return Collection.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Colección "{form.instance.name}" actualizada exitosamente.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class CollectionDeleteView(DeleteView):
    model = Collection
    template_name = 'catalogo/collections/delete.html'
    success_url = reverse_lazy('catalogo:collection-list')

    def get_queryset(self):
        return Collection.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        collection = self.get_object()
        if collection.is_default:
            messages.error(request, 'No puedes eliminar tu colección por defecto.')
            return redirect('catalogo:collection-list')
        messages.success(request, f'Colección "{collection.name}" eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


@login_required
@require_POST
def move_item_to_collection(request):
    item_id = request.POST.get('item_id')
    target_collection_id = request.POST.get('target_collection_id')
    copy_only = request.POST.get('copy_only') == '1'
    
    if not item_id or not target_collection_id:
        return JsonResponse({'ok': False, 'error': 'Parámetros requeridos'}, status=400)

    # Verificar que el item pertenece al usuario
    item = get_object_or_404(CollectionItem, pk=item_id, collection__owner=request.user)
    target_collection = get_object_or_404(Collection, pk=target_collection_id, owner=request.user)

    # Verificar que no esté ya en la colección destino
    if CollectionItem.objects.filter(collection=target_collection, muestra=item.muestra).exists():
        return JsonResponse({'ok': False, 'error': 'El elemento ya está en esta colección'})

    if copy_only:
        # Copiar (crear nuevo vínculo) y mantener el actual
        CollectionItem.objects.create(collection=target_collection, muestra=item.muestra)
        return JsonResponse({'ok': True, 'copied': True, 'message': f'Elemento copiado a "{target_collection.name}"'})
    else:
        # Mover el item
        item.collection = target_collection
        item.save()
        return JsonResponse({'ok': True, 'moved': True, 'message': f'Elemento movido a "{target_collection.name}"'})


@login_required
@require_POST
def create_collection_quick(request):
    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    if not name:
        return JsonResponse({'ok': False, 'error': 'Nombre requerido'}, status=400)
    # Validar unicidad por usuario
    if Collection.objects.filter(owner=request.user, name=name).exists():
        return JsonResponse({'ok': False, 'error': 'Ya existe una colección con ese nombre'}, status=400)
    col = Collection.objects.create(owner=request.user, name=name, description=description)
    return JsonResponse({'ok': True, 'id': col.id, 'name': col.name})


@login_required
@require_POST
def remove_item_from_collection(request):
    item_id = request.POST.get('item_id')
    
    if not item_id:
        return JsonResponse({'ok': False, 'error': 'item_id requerido'}, status=400)

    item = get_object_or_404(CollectionItem, pk=item_id, collection__owner=request.user)
    collection_name = item.collection.name
    item.delete()

    return JsonResponse({'ok': True, 'message': f'Elemento eliminado de "{collection_name}"'})


@login_required
def my_default_collection_redirect(request):
    collection = _get_or_create_default_collection(request.user)
    return redirect('catalogo:collection-detail', pk=collection.pk)


