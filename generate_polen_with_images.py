#!/usr/bin/env python
"""
Script para generar 300 muestras de polen nativas de Villahermosa, Tabasco con imágenes reales
Ejecutar con: python manage.py shell < generate_polen_with_images.py
"""

import os
import sys
import django
from datetime import date, timedelta
import random
from decimal import Decimal
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alga.settings')
django.setup()

from catalogo.models import MuestraBiologica, Familia, Especie, Municipio

def download_image(url, filename):
    """Descargar imagen desde URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Crear archivo temporal
        temp_file = NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_file.write(response.content)
        temp_file.close()
        
        return temp_file.name
    except Exception as e:
        print(f"Error descargando imagen: {e}")
        return None

def get_pollen_image_url(plant_name):
    """Obtener URL de imagen de polen usando Unsplash API"""
    # URLs de imágenes de polen reales (microscopio)
    pollen_images = [
        "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop",
    ]
    return random.choice(pollen_images)

def create_fake_image(nombre_especie):
    """Crear una imagen fake para la muestra de polen"""
    # Intentar descargar una imagen real de polen
    image_url = get_pollen_image_url(nombre_especie)
    image_path = download_image(image_url, f"polen_{nombre_especie}.jpg")
    
    if image_path:
        return image_path
    
    # Si falla, crear una imagen simple
    temp_file = NamedTemporaryFile(delete=False, suffix='.txt')
    temp_file.write(f"Imagen simulada de polen de {nombre_especie}".encode())
    temp_file.close()
    return temp_file.name

def get_or_create_familia(nombre):
    """Obtener o crear una familia"""
    familia, created = Familia.objects.get_or_create(
        nombre=nombre,
        defaults={'descripcion': f'Familia {nombre} nativa de Tabasco'}
    )
    return familia

def get_or_create_especie(nombre, familia):
    """Obtener o crear una especie"""
    especie, created = Especie.objects.get_or_create(
        nombre=nombre,
        defaults={
            'descripcion': f'Especie {nombre} nativa de Villahermosa, Tabasco',
            'familia': familia
        }
    )
    return especie

def get_villahermosa_municipio():
    """Obtener el municipio de Villahermosa"""
    try:
        return Municipio.objects.get(nombre__icontains='Villahermosa')
    except Municipio.DoesNotExist:
        # Crear si no existe
        municipio = Municipio.objects.create(
            clave='VH001',
            nombre='Centro (Villahermosa)',
            estado=27  # Tabasco
        )
        return municipio

# Plantas nativas de Villahermosa, Tabasco que producen polen
PLANTAS_NATIVAS_TABASCO = [
    # Árboles
    ('Ceiba pentandra', 'Ceiba', 'Malvaceae'),
    ('Swietenia macrophylla', 'Caoba', 'Meliaceae'),
    ('Cedrela odorata', 'Cedro', 'Meliaceae'),
    ('Brosimum alicastrum', 'Ramon', 'Moraceae'),
    ('Ficus spp.', 'Higo', 'Moraceae'),
    ('Enterolobium cyclocarpum', 'Guanacaste', 'Fabaceae'),
    ('Lysiloma latisiliquum', 'Tzalam', 'Fabaceae'),
    ('Piscidia piscipula', 'Jabín', 'Fabaceae'),
    ('Bursera simaruba', 'Chaká', 'Burseraceae'),
    ('Cordia dodecandra', 'Siricote', 'Boraginaceae'),
    
    # Palmas
    ('Sabal mexicana', 'Palma real', 'Arecaceae'),
    ('Roystonea regia', 'Palma real cubana', 'Arecaceae'),
    ('Attalea cohune', 'Cohune', 'Arecaceae'),
    ('Astrocaryum mexicanum', 'Chocho', 'Arecaceae'),
    
    # Arbustos y hierbas
    ('Bixa orellana', 'Achiote', 'Bixaceae'),
    ('Capsicum annuum', 'Chile', 'Solanaceae'),
    ('Solanum lycopersicum', 'Tomate', 'Solanaceae'),
    ('Phaseolus vulgaris', 'Frijol', 'Fabaceae'),
    ('Zea mays', 'Maíz', 'Poaceae'),
    ('Cucurbita pepo', 'Calabaza', 'Cucurbitaceae'),
    ('Manihot esculenta', 'Yuca', 'Euphorbiaceae'),
    ('Ipomoea batatas', 'Camote', 'Convolvulaceae'),
    
    # Plantas acuáticas
    ('Eichhornia crassipes', 'Lirio acuático', 'Pontederiaceae'),
    ('Pistia stratiotes', 'Lechuga de agua', 'Araceae'),
    ('Nymphaea ampla', 'Nenúfar', 'Nymphaeaceae'),
    
    # Plantas medicinales
    ('Aloe vera', 'Sábila', 'Asphodelaceae'),
    ('Ocimum basilicum', 'Albahaca', 'Lamiaceae'),
    ('Mentha spicata', 'Menta', 'Lamiaceae'),
    ('Rosmarinus officinalis', 'Romero', 'Lamiaceae'),
    ('Thymus vulgaris', 'Tomillo', 'Lamiaceae'),
    
    # Plantas ornamentales
    ('Hibiscus rosa-sinensis', 'Hibisco', 'Malvaceae'),
    ('Bougainvillea spectabilis', 'Bugambilia', 'Nyctaginaceae'),
    ('Plumeria rubra', 'Flor de mayo', 'Apocynaceae'),
    ('Delonix regia', 'Flaming', 'Fabaceae'),
    ('Tabebuia rosea', 'Maculís', 'Bignoniaceae'),
    
    # Plantas de la selva
    ('Chamaedorea elegans', 'Palma camedor', 'Arecaceae'),
    ('Philodendron spp.', 'Filodendro', 'Araceae'),
    ('Monstera deliciosa', 'Costilla de Adán', 'Araceae'),
    ('Anthurium spp.', 'Anturio', 'Araceae'),
    ('Heliconia spp.', 'Heliconia', 'Heliconiaceae'),
    
    # Plantas de manglar
    ('Rhizophora mangle', 'Mangle rojo', 'Rhizophoraceae'),
    ('Avicennia germinans', 'Mangle negro', 'Acanthaceae'),
    ('Laguncularia racemosa', 'Mangle blanco', 'Combretaceae'),
    ('Conocarpus erectus', 'Mangle botoncillo', 'Combretaceae'),
]

# Colonias de Villahermosa
COLONIAS_VILLAHERMOSA = [
    'Centro', 'Primera Sección', 'Segunda Sección', 'Tercera Sección',
    'Cuarta Sección', 'Quinta Sección', 'Sexta Sección', 'Séptima Sección',
    'Octava Sección', 'Nueva Sección', 'Primera Sección de Atasta',
    'Segunda Sección de Atasta', 'Tercera Sección de Atasta',
    'Primera Sección de Tamulté', 'Segunda Sección de Tamulté',
    'Tercera Sección de Tamulté', 'Cuarta Sección de Tamulté',
    'Quinta Sección de Tamulté', 'Sexta Sección de Tamulté',
    'Séptima Sección de Tamulté', 'Octava Sección de Tamulté',
    'Nueva Sección de Tamulté', 'Primera Sección de Gaviotas',
    'Segunda Sección de Gaviotas', 'Tercera Sección de Gaviotas',
    'Cuarta Sección de Gaviotas', 'Quinta Sección de Gaviotas',
    'Sexta Sección de Gaviotas', 'Séptima Sección de Gaviotas',
    'Octava Sección de Gaviotas', 'Nueva Sección de Gaviotas',
    'Primera Sección de Dos Montes', 'Segunda Sección de Dos Montes',
    'Tercera Sección de Dos Montes', 'Cuarta Sección de Dos Montes',
    'Quinta Sección de Dos Montes', 'Sexta Sección de Dos Montes',
    'Séptima Sección de Dos Montes', 'Octava Sección de Dos Montes',
    'Nueva Sección de Dos Montes', 'Primera Sección de La Manga',
    'Segunda Sección de La Manga', 'Tercera Sección de La Manga',
    'Cuarta Sección de La Manga', 'Quinta Sección de La Manga',
    'Sexta Sección de La Manga', 'Séptima Sección de La Manga',
    'Octava Sección de La Manga', 'Nueva Sección de La Manga',
]

# Nombres de colectores
COLECTORES = [
    'Dr. Carlos Méndez', 'Dra. Ana López', 'Dr. Roberto García',
    'Dra. María Fernández', 'Dr. José Martínez', 'Dra. Carmen Rodríguez',
    'Dr. Luis González', 'Dra. Patricia Silva', 'Dr. Miguel Torres',
    'Dra. Elena Vargas', 'Dr. Francisco Ruiz', 'Dra. Isabel Morales',
    'Dr. Antonio Jiménez', 'Dra. Rosa Herrera', 'Dr. Manuel Castro',
    'Dra. Teresa Mendoza', 'Dr. Javier Ortega', 'Dra. Lucía Ríos',
    'Dr. Enrique Vega', 'Dra. Gabriela Flores', 'Dr. Ricardo Moreno',
    'Dra. Susana Delgado', 'Dr. Fernando Cruz', 'Dra. Adriana Luna',
    'Dr. Víctor Medina', 'Dra. Claudia Paredes', 'Dr. Arturo Reyes',
    'Dra. Norma Acosta', 'Dr. Sergio Miranda', 'Dra. Beatriz Soto',
]

def generate_polen_samples():
    """Generar 300 muestras de polen"""
    
    print("Iniciando generación de 300 muestras de polen...")
    
    # Obtener municipio de Villahermosa
    municipio = get_villahermosa_municipio()
    print(f"Municipio: {municipio.nombre}")
    
    # Crear familias y especies
    familias_creadas = {}
    especies_creadas = {}
    
    for nombre_cientifico, nombre_comun, familia_nombre in PLANTAS_NATIVAS_TABASCO:
        if familia_nombre not in familias_creadas:
            familia = get_or_create_familia(familia_nombre)
            familias_creadas[familia_nombre] = familia
            print(f"Familia creada: {familia.nombre}")
        
        familia = familias_creadas[familia_nombre]
        especie = get_or_create_especie(nombre_cientifico, familia)
        especies_creadas[nombre_cientifico] = especie
        print(f"Especie creada: {especie.nombre}")
    
    # Generar 300 muestras
    muestras_creadas = 0
    
    for i in range(300):
        # Seleccionar planta aleatoria
        planta = random.choice(PLANTAS_NATIVAS_TABASCO)
        nombre_cientifico, nombre_comun, familia_nombre = planta
        
        # Obtener especie
        especie = especies_creadas[nombre_cientifico]
        
        # Generar datos aleatorios
        fecha = date.today() - timedelta(days=random.randint(0, 365*3))  # Últimos 3 años
        numero_recolecta = f"POL-{str(i+1).zfill(4)}-{fecha.year}"
        colonia = random.choice(COLONIAS_VILLAHERMOSA)
        localidad = "Villahermosa"
        nombre_colector = random.choice(COLECTORES)
        
        # Coordenadas de Villahermosa (aproximadas)
        latitud = Decimal(str(random.uniform(17.95, 18.05)))
        longitud = Decimal(str(random.uniform(-92.98, -92.92)))
        
        # Crear imagen
        imagen_path = create_fake_image(nombre_cientifico)
        
        try:
            # Crear la muestra
            muestra = MuestraBiologica.objects.create(
                tipo_muestra='POLEN',
                nombre_cientifico=nombre_cientifico,
                nombre_comun=nombre_comun,
                numero_recolecta=numero_recolecta,
                colonia=colonia,
                localidad=localidad,
                descripcion=f"Muestra de polen de {nombre_comun} recolectada en {colonia}, Villahermosa, Tabasco. Especie nativa de la región con importancia ecológica y cultural.",
                nombre_colector=nombre_colector,
                fecha=fecha,
                latitud=latitud,
                longitud=longitud,
                especie=especie,
                municipio=municipio,
                genero=random.choice(['M', 'F', 'H', 'ND'])
            )
            
            # Asignar imagen
            with open(imagen_path, 'rb') as img_file:
                muestra.imagen.save(f"polen_{i+1}.jpg", File(img_file), save=True)
            
            # Limpiar archivo temporal
            os.unlink(imagen_path)
            
            muestras_creadas += 1
            
            if muestras_creadas % 50 == 0:
                print(f"Progreso: {muestras_creadas}/300 muestras creadas")
                
        except Exception as e:
            print(f"Error creando muestra {i+1}: {e}")
            if os.path.exists(imagen_path):
                os.unlink(imagen_path)
            continue
    
    print(f"\n¡Completado! Se crearon {muestras_creadas} muestras de polen.")
    print(f"Familias creadas: {len(familias_creadas)}")
    print(f"Especies creadas: {len(especies_creadas)}")
    
    # Mostrar estadísticas
    total_polen = MuestraBiologica.objects.filter(tipo_muestra='POLEN').count()
    print(f"Total de muestras de polen en la base de datos: {total_polen}")

if __name__ == "__main__":
    generate_polen_samples() 