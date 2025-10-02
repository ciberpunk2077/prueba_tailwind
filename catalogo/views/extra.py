from django.shortcuts import render, get_object_or_404
from catalogo.models import MuestraBiologica

def comparador_tipo(request, tipo):
    s1 = request.GET.get('s1')
    s2 = request.GET.get('s2')
    muestra1 = None
    muestra2 = None
    # Obtener todas las muestras del tipo, excluyendo la seleccionada
    muestras_qs = MuestraBiologica.objects.filter(tipo_muestra=tipo).order_by('nombre_cientifico')
    if s1:
        muestras_qs = muestras_qs.exclude(pk=s1)
    # Mostrar solo una muestra por nombre científico (evitar duplicados)
    nombres_vistos = set()
    muestras = []
    for m in muestras_qs:
        if m.nombre_cientifico not in nombres_vistos:
            muestras.append(m)
            nombres_vistos.add(m.nombre_cientifico)
    if s1:
        try:
            muestra1 = MuestraBiologica.objects.get(pk=s1, tipo_muestra=tipo)
        except MuestraBiologica.DoesNotExist:
            muestra1 = None
    if s2:
        try:
            muestra2 = MuestraBiologica.objects.get(pk=s2, tipo_muestra=tipo)
        except MuestraBiologica.DoesNotExist:
            muestra2 = None
    return render(request, 'catalogo/comparador_tipo.html', {
        'muestra1': muestra1,
        'muestra2': muestra2,
        'muestras': muestras,
        'tipo': tipo,
    })
