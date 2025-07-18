#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alga.settings')
django.setup()

from catalogo.models import MuestraBiologica, Familia, Especie, Municipio
from django.db.models import Count, Min, Max
from collections import Counter

def check_hongos_stats():
    """Verifica las estadísticas de las muestras de hongos creadas"""
    
    # Obtener todas las muestras de hongos
    muestras_hongos = MuestraBiologica.objects.filter(tipo_muestra='HONGO')
    total_muestras = muestras_hongos.count()
    
    print("=" * 60)
    print("ESTADÍSTICAS DE MUESTRAS DE HONGOS - TABASCO, MÉXICO")
    print("=" * 60)
    print(f"Total de muestras de hongos: {total_muestras}")
    print()
    
    # Verificar muestras con imágenes
    muestras_con_imagen = muestras_hongos.filter(imagen__isnull=False).count()
    muestras_sin_imagen = total_muestras - muestras_con_imagen
    
    print("ESTADO DE IMÁGENES:")
    print(f"  - Muestras con imagen: {muestras_con_imagen}")
    print(f"  - Muestras sin imagen: {muestras_sin_imagen}")
    print(f"  - Porcentaje con imagen: {(muestras_con_imagen/total_muestras)*100:.1f}%")
    print()
    
    # Distribución por municipio
    print("DISTRIBUCIÓN POR MUNICIPIO:")
    municipios_count = muestras_hongos.values('municipio__nombre').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for item in municipios_count[:10]:  # Top 10 municipios
        municipio = item['municipio__nombre'] or 'Sin municipio'
        count = item['count']
        porcentaje = (count/total_muestras)*100
        print(f"  - {municipio}: {count} muestras ({porcentaje:.1f}%)")
    print()
    
    # Distribución por familia
    print("DISTRIBUCIÓN POR FAMILIA:")
    familias_count = muestras_hongos.values('especie__familia__nombre').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for item in familias_count:
        familia = item['especie__familia__nombre'] or 'Sin familia'
        count = item['count']
        porcentaje = (count/total_muestras)*100
        print(f"  - {familia}: {count} muestras ({porcentaje:.1f}%)")
    print()
    
    # Distribución por especie
    print("DISTRIBUCIÓN POR ESPECIE (Top 15):")
    especies_count = muestras_hongos.values('especie__nombre').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for item in especies_count[:15]:
        especie = item['especie__nombre'] or 'Sin especie'
        count = item['count']
        porcentaje = (count/total_muestras)*100
        print(f"  - {especie}: {count} muestras ({porcentaje:.1f}%)")
    print()
    
    # Distribución por año
    print("DISTRIBUCIÓN POR AÑO:")
    años_count = muestras_hongos.values('fecha__year').annotate(
        count=Count('id')
    ).order_by('fecha__year')
    
    for item in años_count:
        año = item['fecha__year'] or 'Sin fecha'
        count = item['count']
        porcentaje = (count/total_muestras)*100
        print(f"  - {año}: {count} muestras ({porcentaje:.1f}%)")
    print()
    
    # Distribución por colector
    print("DISTRIBUCIÓN POR COLECTOR (Top 10):")
    colectores_count = muestras_hongos.values('nombre_colector').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for item in colectores_count[:10]:
        colector = item['nombre_colector'] or 'Sin colector'
        count = item['count']
        porcentaje = (count/total_muestras)*100
        print(f"  - {colector}: {count} muestras ({porcentaje:.1f}%)")
    print()
    
    # Verificar rangos de coordenadas
    print("RANGOS DE COORDENADAS:")
    lat_min = muestras_hongos.aggregate(min_lat=Min('latitud'))['min_lat']
    lat_max = muestras_hongos.aggregate(max_lat=Max('latitud'))['max_lat']
    lon_min = muestras_hongos.aggregate(min_lon=Min('longitud'))['min_lon']
    lon_max = muestras_hongos.aggregate(max_lon=Max('longitud'))['max_lon']
    
    print(f"  - Latitud: {lat_min:.6f} a {lat_max:.6f}")
    print(f"  - Longitud: {lon_min:.6f} a {lon_max:.6f}")
    print()
    
    # Verificar localidades únicas
    localidades_unicas = muestras_hongos.values_list('localidad', flat=True).distinct().count()
    print(f"Localidades únicas: {localidades_unicas}")
    print()
    
    # Verificar colonias únicas
    colonias_unicas = muestras_hongos.values_list('colonia', flat=True).distinct().count()
    print(f"Colonias únicas: {colonias_unicas}")
    print()
    
    # Verificar números de recolecta únicos
    numeros_unicos = muestras_hongos.values_list('numero_recolecta', flat=True).distinct().count()
    print(f"Números de recolecta únicos: {numeros_unicos}")
    print(f"Verificación de unicidad: {'✓ OK' if numeros_unicos == total_muestras else '✗ ERROR'}")
    print()
    
    print("=" * 60)
    print("VERIFICACIÓN COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    check_hongos_stats() 