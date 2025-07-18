from django.core.management.base import BaseCommand
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from catalogo.models import MuestraBiologica, Familia, Especie, Municipio
from datetime import date, timedelta
import random
from decimal import Decimal
import os
import requests

class Command(BaseCommand):
    help = 'Generar 300 muestras de polen nativas de Villahermosa, Tabasco con imágenes reales descargadas de internet.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando generación de 300 muestras de polen con imágenes reales...'))

        PLANTAS_NATIVAS_TABASCO = [
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
            ('Sabal mexicana', 'Palma real', 'Arecaceae'),
            ('Roystonea regia', 'Palma real cubana', 'Arecaceae'),
            ('Attalea cohune', 'Cohune', 'Arecaceae'),
            ('Astrocaryum mexicanum', 'Chocho', 'Arecaceae'),
            ('Bixa orellana', 'Achiote', 'Bixaceae'),
            ('Capsicum annuum', 'Chile', 'Solanaceae'),
            ('Solanum lycopersicum', 'Tomate', 'Solanaceae'),
            ('Phaseolus vulgaris', 'Frijol', 'Fabaceae'),
            ('Zea mays', 'Maíz', 'Poaceae'),
            ('Cucurbita pepo', 'Calabaza', 'Cucurbitaceae'),
            ('Manihot esculenta', 'Yuca', 'Euphorbiaceae'),
            ('Ipomoea batatas', 'Camote', 'Convolvulaceae'),
            ('Eichhornia crassipes', 'Lirio acuático', 'Pontederiaceae'),
            ('Pistia stratiotes', 'Lechuga de agua', 'Araceae'),
            ('Nymphaea ampla', 'Nenúfar', 'Nymphaeaceae'),
            ('Aloe vera', 'Sábila', 'Asphodelaceae'),
            ('Ocimum basilicum', 'Albahaca', 'Lamiaceae'),
            ('Mentha spicata', 'Menta', 'Lamiaceae'),
            ('Rosmarinus officinalis', 'Romero', 'Lamiaceae'),
            ('Thymus vulgaris', 'Tomillo', 'Lamiaceae'),
            ('Hibiscus rosa-sinensis', 'Hibisco', 'Malvaceae'),
            ('Bougainvillea spectabilis', 'Bugambilia', 'Nyctaginaceae'),
            ('Plumeria rubra', 'Flor de mayo', 'Apocynaceae'),
            ('Delonix regia', 'Flaming', 'Fabaceae'),
            ('Tabebuia rosea', 'Maculís', 'Bignoniaceae'),
            ('Chamaedorea elegans', 'Palma camedor', 'Arecaceae'),
            ('Philodendron spp.', 'Filodendro', 'Araceae'),
            ('Monstera deliciosa', 'Costilla de Adán', 'Araceae'),
            ('Anthurium spp.', 'Anturio', 'Araceae'),
            ('Heliconia spp.', 'Heliconia', 'Heliconiaceae'),
            ('Rhizophora mangle', 'Mangle rojo', 'Rhizophoraceae'),
            ('Avicennia germinans', 'Mangle negro', 'Acanthaceae'),
            ('Laguncularia racemosa', 'Mangle blanco', 'Combretaceae'),
            ('Conocarpus erectus', 'Mangle botoncillo', 'Combretaceae'),
        ]

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

        # Lista de imágenes de polen reales (puedes agregar más URLs si lo deseas)
        IMAGENES_POLEN = [
            'https://images.unsplash.com/photo-1576086213369-97a306d36557?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop',
            'https://upload.wikimedia.org/wikipedia/commons/7/7c/Pollen_Grains_%28cropped%29.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/2/2c/Pollen_Grains_Microscopy.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/3/3b/Pollen_Grains_2.jpg',
        ]

        def get_or_create_familia(nombre):
            familia, _ = Familia.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': f'Familia {nombre} nativa de Tabasco'}
            )
            return familia

        def get_or_create_especie(nombre, familia):
            especie, _ = Especie.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': f'Especie {nombre} nativa de Villahermosa, Tabasco',
                    'familia': familia
                }
            )
            return especie

        def get_villahermosa_municipio():
            try:
                return Municipio.objects.get(nombre__icontains='Villahermosa')
            except Municipio.DoesNotExist:
                municipio = Municipio.objects.create(
                    clave='VH001',
                    nombre='Centro (Villahermosa)',
                    estado=27
                )
                return municipio

        def descargar_imagen(url):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                temp_file = NamedTemporaryFile(delete=False, suffix='.jpg')
                temp_file.write(response.content)
                temp_file.close()
                return temp_file.name
            except Exception as e:
                print(f"Error descargando imagen: {e}")
                return None

        municipio = get_villahermosa_municipio()
        familias_creadas = {}
        especies_creadas = {}
        for nombre_cientifico, nombre_comun, familia_nombre in PLANTAS_NATIVAS_TABASCO:
            if familia_nombre not in familias_creadas:
                familia = get_or_create_familia(familia_nombre)
                familias_creadas[familia_nombre] = familia
            familia = familias_creadas[familia_nombre]
            especie = get_or_create_especie(nombre_cientifico, familia)
            especies_creadas[nombre_cientifico] = especie

        muestras_creadas = 0
        for i in range(300):
            planta = random.choice(PLANTAS_NATIVAS_TABASCO)
            nombre_cientifico, nombre_comun, familia_nombre = planta
            especie = especies_creadas[nombre_cientifico]
            fecha = date.today() - timedelta(days=random.randint(0, 365*3))
            numero_recolecta = f"POL-{str(i+1).zfill(4)}-{fecha.year}"
            colonia = random.choice(COLONIAS_VILLAHERMOSA)
            localidad = "Villahermosa"
            nombre_colector = random.choice(COLECTORES)
            latitud = Decimal(str(random.uniform(17.95, 18.05)))
            longitud = Decimal(str(random.uniform(-92.98, -92.92)))
            url_imagen = random.choice(IMAGENES_POLEN)
            imagen_path = descargar_imagen(url_imagen)
            if not imagen_path:
                imagen_path = os.path.join(os.path.dirname(__file__), 'backup_polen.jpg')
            try:
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
                with open(imagen_path, 'rb') as img_file:
                    muestra.imagen.save(f"polen_{i+1}.jpg", File(img_file), save=True)
                if os.path.exists(imagen_path) and 'backup_polen.jpg' not in imagen_path:
                    os.unlink(imagen_path)
                muestras_creadas += 1
                if muestras_creadas % 50 == 0:
                    self.stdout.write(self.style.SUCCESS(f"Progreso: {muestras_creadas}/300 muestras creadas"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creando muestra {i+1}: {e}"))
                if imagen_path and os.path.exists(imagen_path) and 'backup_polen.jpg' not in imagen_path:
                    os.unlink(imagen_path)
                continue
        self.stdout.write(self.style.SUCCESS(f"\n¡Completado! Se crearon {muestras_creadas} muestras de polen con imágenes reales."))
        total_polen = MuestraBiologica.objects.filter(tipo_muestra='POLEN').count()
        self.stdout.write(f"Total de muestras de polen en la base de datos: {total_polen}") 