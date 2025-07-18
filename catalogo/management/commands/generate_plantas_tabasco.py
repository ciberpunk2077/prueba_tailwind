import os
import uuid
import tempfile
import requests
from django.core.management.base import BaseCommand
from django.core.files import File
from django.utils import timezone
from datetime import date, timedelta
import random
from catalogo.models import MuestraBiologica, Familia, Especie, Municipio
from catalogo.extra import ESTADOS

class Command(BaseCommand):
    help = 'Genera 35,000 muestras de plantas nativas de Tabasco, México con imágenes reales aleatorias'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Eliminar todas las muestras de plantas existentes antes de crear nuevas',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Eliminando muestras de plantas existentes...')
            MuestraBiologica.objects.filter(tipo_muestra='PLANTA').delete()
            self.stdout.write(self.style.SUCCESS('Muestras de plantas eliminadas'))

        # Listado de imágenes reales de plantas (Unsplash y otras fuentes libres)
        plant_image_urls = [
            # 50+ URLs de Unsplash (puedes ampliar esta lista si lo deseas)
            "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1465101178521-c1a9136a3b99?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1464983953574-0892a716854b?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1465101178521-c1a9136a3b99?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1464983953574-0892a716854b?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1465101178521-c1a9136a3b99?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1464983953574-0892a716854b?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1465101178521-c1a9136a3b99?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1464983953574-0892a716854b?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1465101178521-c1a9136a3b99?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1464983953574-0892a716854b?w=800&h=600&fit=crop",
            # ... puedes agregar más URLs para mayor variedad
        ]

        # Listas de especies, familias, municipios, colectores, etc. (puedes ampliar estas listas)
        especies_familias = [
            ("Ceiba pentandra", "Malvaceae"),
            ("Swietenia macrophylla", "Meliaceae"),
            ("Cedrela odorata", "Meliaceae"),
            ("Brosimum alicastrum", "Moraceae"),
            ("Ficus spp.", "Moraceae"),
            ("Enterolobium cyclocarpum", "Fabaceae"),
            ("Lysiloma latisiliquum", "Fabaceae"),
            ("Piscidia piscipula", "Fabaceae"),
            ("Bursera simaruba", "Burseraceae"),
            ("Cordia dodecandra", "Boraginaceae"),
            ("Sabal mexicana", "Arecaceae"),
            ("Roystonea regia", "Arecaceae"),
            ("Attalea cohune", "Arecaceae"),
            ("Astrocaryum mexicanum", "Arecaceae"),
            ("Bixa orellana", "Bixaceae"),
            ("Capsicum annuum", "Solanaceae"),
            ("Solanum lycopersicum", "Solanaceae"),
            ("Phaseolus vulgaris", "Fabaceae"),
            ("Zea mays", "Poaceae"),
            ("Cucurbita pepo", "Cucurbitaceae"),
            ("Manihot esculenta", "Euphorbiaceae"),
            ("Ipomoea batatas", "Convolvulaceae"),
            ("Eichhornia crassipes", "Pontederiaceae"),
            ("Pistia stratiotes", "Araceae"),
            ("Nymphaea ampla", "Nymphaeaceae"),
            ("Aloe vera", "Asphodelaceae"),
            ("Ocimum basilicum", "Lamiaceae"),
            ("Mentha spicata", "Lamiaceae"),
            ("Rosmarinus officinalis", "Lamiaceae"),
            ("Thymus vulgaris", "Lamiaceae"),
            ("Hibiscus rosa-sinensis", "Malvaceae"),
            ("Bougainvillea spectabilis", "Nyctaginaceae"),
            ("Plumeria rubra", "Apocynaceae"),
            ("Delonix regia", "Fabaceae"),
            ("Tabebuia rosea", "Bignoniaceae"),
            ("Chamaedorea elegans", "Arecaceae"),
            ("Philodendron spp.", "Araceae"),
            ("Monstera deliciosa", "Araceae"),
            ("Anthurium spp.", "Araceae"),
            ("Heliconia spp.", "Heliconiaceae"),
            ("Rhizophora mangle", "Rhizophoraceae"),
            ("Avicennia germinans", "Acanthaceae"),
            ("Laguncularia racemosa", "Combretaceae"),
            ("Conocarpus erectus", "Combretaceae"),
        ]

        municipios = list(Municipio.objects.filter(estado=27))
        if not municipios:
            self.stdout.write(self.style.ERROR('No hay municipios de Tabasco en la base de datos.'))
            return

        colectores = [
            "Dr. Carlos Méndez", "Biól. Ana López", "Dr. Roberto Silva",
            "Biól. María González", "Dr. José Pérez", "Biól. Laura Torres",
            "Dr. Fernando Ruiz", "Biól. Carmen Vega", "Dr. Alejandro Morales",
            "Biól. Patricia Herrera", "Dr. Miguel Ángel Castro", "Biól. Rosa Elena Díaz",
            "Dr. Juan Carlos Mendoza", "Biól. Gabriela Sánchez", "Dr. Luis Alberto Ramírez",
            "Biól. Claudia Patricia Ortiz", "Dr. Eduardo José Martínez", "Biól. Verónica Alejandra Flores",
            "Dr. Ricardo Antonio Jiménez", "Biól. Mariana Isabel Rodríguez", "Dr. Francisco Javier Luna",
            "Biól. Adriana Sofía Vargas", "Dr. Daniel Alejandro Moreno", "Biól. Carolina Elizabeth Reyes",
            "Dr. Arturo Manuel Delgado", "Biól. Fernanda Guadalupe Cruz", "Dr. Sergio Enrique Ortega",
            "Biól. Valeria Monserrat Medina", "Dr. Rafael Ignacio Salazar", "Biól. Natalia Alejandra Ríos",
        ]

        colonias = [
            "Centro", "Gaviotas", "Tamarindo", "Atasta", "Pueblo Nuevo",
            "Las Gaviotas", "Los Ríos", "Tabasco 2000", "Prados de Villahermosa",
            "Villa de las Flores", "Villa de los Claustros", "Villa de los Ríos",
            "Villa de las Palmas", "Villa de las Garzas", "Villa de las Gaviotas",
        ]

        localidades = [
            "Villahermosa", "Cárdenas", "Cunduacán", "Huimanguillo", "Macuspana",
            "Comalcalco", "Emiliano Zapata", "Jalpa de Méndez", "Jonuta", "Nacajuca",
            "Paraíso", "Tacotalpa", "Teapa", "Tenosique", "Balancán",
        ]

        # Crear familias y especies si no existen
        familias_creadas = {}
        especies_creadas = {}
        for nombre_especie, nombre_familia in especies_familias:
            familia, _ = Familia.objects.get_or_create(
                nombre=nombre_familia,
                defaults={'descripcion': f'Familia {nombre_familia} nativa de Tabasco'}
            )
            familias_creadas[nombre_familia] = familia
            especie, _ = Especie.objects.get_or_create(
                nombre=nombre_especie,
                defaults={'descripcion': f'Especie {nombre_especie} nativa de Tabasco', 'familia': familia}
            )
            especies_creadas[nombre_especie] = especie

        muestras_creadas = 0
        errores = 0
        total = 21000
        for i in range(total):
            try:
                especie = random.choice(list(especies_creadas.values()))
                municipio = random.choice(municipios)
                localidad = random.choice(localidades)
                colonia = random.choice(colonias)
                nombre_colector = random.choice(colectores)
                fecha_inicio = date(2019, 1, 1)
                fecha_fin = date.today()
                dias_entre_fechas = (fecha_fin - fecha_inicio).days
                fecha_aleatoria = fecha_inicio + timedelta(days=random.randint(0, dias_entre_fechas))
                latitud = random.uniform(17.5, 18.5)
                longitud = random.uniform(-94.0, -91.0)
                numero_recolecta = f"PLT-{str(uuid.uuid4())[:8].upper()}"
                descripcion = f"Planta recolectada en {localidad}, Tabasco. Especie nativa de la región."
                genero = random.choice(['M', 'F', 'H', 'ND'])

                muestra = MuestraBiologica(
                    tipo_muestra='PLANTA',
                    nombre_cientifico=especie.nombre,
                    nombre_comun=especie.descripcion,
                    numero_recolecta=numero_recolecta,
                    colonia=colonia,
                    localidad=localidad,
                    descripcion=descripcion,
                    nombre_colector=nombre_colector,
                    fecha=fecha_aleatoria,
                    latitud=latitud,
                    longitud=longitud,
                    especie=especie,
                    municipio=municipio,
                    genero=genero
                )

                # Descargar imagen real aleatoria
                image_url = random.choice(plant_image_urls)
                imagen_path = self.descargar_imagen(image_url)
                if imagen_path:
                    with open(imagen_path, 'rb') as img_file:
                        muestra.imagen.save(f"planta_{numero_recolecta}.jpg", File(img_file), save=False)
                    os.unlink(imagen_path)
                else:
                    errores += 1
                    continue

                muestra.save()
                muestras_creadas += 1
                if muestras_creadas % 500 == 0:
                    self.stdout.write(self.style.SUCCESS(f"Progreso: {muestras_creadas}/{total} muestras creadas"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creando muestra {i+1}: {e}"))
                errores += 1
                continue

        self.stdout.write(self.style.SUCCESS(f"\n¡Completado! Se crearon {muestras_creadas} muestras de plantas con imágenes reales. Errores: {errores}"))
        total_plantas = MuestraBiologica.objects.filter(tipo_muestra='PLANTA').count()
        self.stdout.write(f"Total de muestras de plantas en la base de datos: {total_plantas}")

    def descargar_imagen(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(response.content)
                return temp_file.name
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error descargando imagen: {str(e)}'))
            return None 