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
    help = 'Genera 1000 muestras de hongos nativos de Tabasco, México con imágenes reales'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Eliminar todas las muestras de hongos existentes antes de crear nuevas',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Eliminando muestras de hongos existentes...')
            MuestraBiologica.objects.filter(tipo_muestra='HONGO').delete()
            self.stdout.write(self.style.SUCCESS('Muestras de hongos eliminadas'))

        # Obtener o crear familias de hongos
        familias_hongos = self.get_or_create_familias_hongos()
        # Obtener o crear especies de hongos
        especies_hongos = self.get_or_create_especies_hongos(familias_hongos)
        # Obtener municipios de Tabasco
        municipios_tabasco = self.get_municipios_tabasco()

        # URLs de imágenes reales de hongos (Unsplash, libres de derechos)
        hongo_image_urls = [
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop&q=80"
        ]

        localidades_tabasco = [
            "Villahermosa", "Centro", "Cárdenas", "Cunduacán", "Huimanguillo",
            "Macuspana", "Comalcalco", "Emiliano Zapata", "Jalpa de Méndez", "Jonuta",
            "Nacajuca", "Paraíso", "Tacotalpa", "Teapa", "Tenosique", "Balancán",
            "El Triunfo", "Francisco I. Madero", "Ignacio Gutiérrez Gómez", "Pueblo Nuevo",
            "San Carlos", "San Fernando", "San Juan Bautista", "San Simón", "Santa Ana",
            "Santa Cruz", "Santa María", "Santo Domingo", "Villa Aldama", "Villa Chontalpa",
            "Ranchería El Limón", "Ranchería La Ceiba", "Ejido El Zapote", "Colonia La Esperanza",
            "Poblado El Carmen", "Ranchería San José", "Ejido La Victoria", "Colonia Nueva Era"
        ]
        colonias_tabasco = [
            "Centro", "Gaviotas", "Tamarindo", "Atasta", "Pueblo Nuevo",
            "Las Gaviotas", "Los Ríos", "Tabasco 2000", "Prados de Villahermosa",
            "Villa de las Flores", "Villa de los Claustros", "Villa de los Ríos",
            "Villa de las Palmas", "Villa de las Garzas", "Villa de las Gaviotas",
            "Colonia del Bosque", "Colonia La Manga", "Colonia La Paz", "Colonia La Victoria",
            "Colonia Los Pinos", "Colonia San José", "Colonia Santa Cruz", "Colonia Santa Fe"
        ]
        colectores = [
            "Dr. Carlos Méndez", "Biól. Ana López", "Dr. Roberto Silva",
            "Biól. María González", "Dr. José Pérez", "Biól. Laura Torres",
            "Dr. Fernando Ruiz", "Biól. Carmen Vega", "Dr. Alejandro Morales",
            "Biól. Patricia Herrera", "Dr. Miguel Ángel Castro", "Biól. Rosa Elena Díaz",
            "Dr. Juan Carlos Ramírez", "Biól. Gabriela Mendoza", "Dr. Luis Alberto Sánchez",
            "Biól. Claudia Patricia Jiménez", "Dr. Francisco Javier López", "Biól. Adriana Martínez"
        ]

        muestras_creadas = 0
        errores = 0
        for i in range(1000):
            try:
                numero_recolecta = f"HON-{str(uuid.uuid4())[:8].upper()}"
                especie = random.choice(especies_hongos)
                municipio = random.choice(municipios_tabasco)
                localidad = random.choice(localidades_tabasco)
                colonia = random.choice(colonias_tabasco)
                nombre_colector = random.choice(colectores)
                fecha_inicio = date(2019, 1, 1)
                fecha_fin = date.today()
                dias_entre_fechas = (fecha_fin - fecha_inicio).days
                fecha_aleatoria = fecha_inicio + timedelta(days=random.randint(0, dias_entre_fechas))
                latitud = random.uniform(17.5, 18.5)
                longitud = random.uniform(-94.0, -91.0)
                
                # Descripciones específicas para hongos
                descripciones_hongos = [
                    f"Hongo recolectado en {localidad}, Tabasco. Especie nativa de la región selvática.",
                    f"Ejemplar de hongo encontrado en suelo húmedo de {localidad}, Tabasco.",
                    f"Hongo saprófito recolectado en tronco caído en {localidad}, Tabasco.",
                    f"Especie de hongo micorrízico asociado a raíces de árboles en {localidad}, Tabasco.",
                    f"Hongo parásito encontrado en vegetación de {localidad}, Tabasco.",
                    f"Ejemplar de hongo comestible recolectado en {localidad}, Tabasco.",
                    f"Hongo tóxico identificado en {localidad}, Tabasco. No apto para consumo.",
                    f"Especie de hongo medicinal encontrada en {localidad}, Tabasco.",
                    f"Hongo descomponedor de materia orgánica en {localidad}, Tabasco.",
                    f"Ejemplar de hongo raro encontrado en {localidad}, Tabasco."
                ]
                
                muestra = MuestraBiologica(
                    tipo_muestra='HONGO',
                    nombre_cientifico=especie.nombre,
                    nombre_comun=especie.descripcion,
                    numero_recolecta=numero_recolecta,
                    colonia=colonia,
                    localidad=localidad,
                    descripcion=random.choice(descripciones_hongos),
                    nombre_colector=nombre_colector,
                    fecha=fecha_aleatoria,
                    latitud=latitud,
                    longitud=longitud,
                    especie=especie,
                    municipio=municipio,
                    genero=random.choice(['M', 'F', 'H', 'ND'])
                )
                imagen_url = random.choice(hongo_image_urls)
                if self.download_and_assign_image(muestra, imagen_url):
                    muestra.save()
                    muestras_creadas += 1
                    if muestras_creadas % 100 == 0:
                        self.stdout.write(f'Progreso: {muestras_creadas} muestras creadas...')
                else:
                    errores += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creando muestra {i+1}: {str(e)}'))
                errores += 1
                continue
        self.stdout.write(self.style.SUCCESS(f'¡Completado! Se crearon {muestras_creadas} muestras de hongos de Tabasco. Errores: {errores}'))

    def get_or_create_familias_hongos(self):
        familias_data = [
            ("Agaricaceae", "Familia de hongos con láminas"),
            ("Amanitaceae", "Familia de hongos venenosos"),
            ("Boletaceae", "Familia de hongos poroides"),
            ("Cantharellaceae", "Familia de hongos comestibles"),
            ("Cortinariaceae", "Familia de hongos con cortina"),
            ("Entolomataceae", "Familia de hongos rosados"),
            ("Ganodermataceae", "Familia de hongos medicinales"),
            ("Hydnaceae", "Familia de hongos con espinas"),
            ("Inocybaceae", "Familia de hongos fibrosos"),
            ("Lycoperdaceae", "Familia de hongos puffball"),
            ("Marasmiaceae", "Familia de hongos resistentes"),
            ("Mycenaceae", "Familia de hongos pequeños"),
            ("Omphalotaceae", "Familia de hongos ombligo"),
            ("Pleurotaceae", "Familia de hongos ostra"),
            ("Polyporaceae", "Familia de hongos políporos"),
            ("Psathyrellaceae", "Familia de hongos frágiles"),
            ("Russulaceae", "Familia de hongos lechosos"),
            ("Strophariaceae", "Familia de hongos escamosos"),
            ("Tricholomataceae", "Familia de hongos blancos"),
            ("Xerocomaceae", "Familia de hongos secos")
        ]
        familias = []
        for nombre, descripcion in familias_data:
            familia, created = Familia.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion}
            )
            familias.append(familia)
            if created:
                self.stdout.write(f'Familia creada: {nombre}')
        return familias

    def get_or_create_especies_hongos(self, familias):
        especies_data = [
            ("Agaricus campestris", "Champiñón silvestre", familias[0]),
            ("Amanita muscaria", "Amanita muscaria", familias[1]),
            ("Boletus edulis", "Boleto comestible", familias[2]),
            ("Cantharellus cibarius", "Reishi", familias[3]),
            ("Cortinarius violaceus", "Cortinario violeta", familias[4]),
            ("Entoloma lividum", "Entoloma livido", familias[5]),
            ("Ganoderma lucidum", "Ganoderma brillante", familias[6]),
            ("Hydnum repandum", "Hidno repando", familias[7]),
            ("Inocybe geophylla", "Inocibe geófilo", familias[8]),
            ("Lycoperdon perlatum", "Pedos de lobo", familias[9]),
            ("Marasmius oreades", "Marasmio de las hadas", familias[10]),
            ("Mycena galericulata", "Micena galericulada", familias[11]),
            ("Omphalotus olearius", "Omfaloto oleario", familias[12]),
            ("Pleurotus ostreatus", "Seta ostra", familias[13]),
            ("Polyporus squamosus", "Políporo escamoso", familias[14]),
            ("Psathyrella candolleana", "Psatirela de Candolle", familias[15]),
            ("Russula emetica", "Russula emética", familias[16]),
            ("Stropharia aeruginosa", "Estrofaria verdosa", familias[17]),
            ("Tricholoma terreum", "Tricholoma terroso", familias[18]),
            ("Xerocomus badius", "Xerocomus bayo", familias[19]),
            ("Agaricus bisporus", "Champiñón común", familias[0]),
            ("Amanita phalloides", "Amanita faloide", familias[1]),
            ("Boletus aereus", "Boleto negro", familias[2]),
            ("Cantharellus tubaeformis", "Reishi tubular", familias[3]),
            ("Cortinarius semisanguineus", "Cortinario semisanguíneo", familias[4]),
            ("Entoloma sinuatum", "Entoloma sinuado", familias[5]),
            ("Ganoderma applanatum", "Ganoderma plano", familias[6]),
            ("Hydnum umbilicatum", "Hidno umbilicado", familias[7]),
            ("Inocybe fastigiata", "Inocibe fastigiado", familias[8]),
            ("Lycoperdon pyriforme", "Pedos de lobo piriformes", familias[9]),
            ("Marasmius rotula", "Marasmio rotulado", familias[10]),
            ("Mycena pura", "Micena pura", familias[11]),
            ("Omphalotus illudens", "Omfaloto ilusorio", familias[12]),
            ("Pleurotus pulmonarius", "Seta ostra pulmonar", familias[13]),
            ("Polyporus umbellatus", "Políporo umbelado", familias[14]),
            ("Psathyrella hydrophila", "Psatirela hidrófila", familias[15]),
            ("Russula virescens", "Russula verdosa", familias[16]),
            ("Stropharia semiglobata", "Estrofaria semiglobosa", familias[17]),
            ("Tricholoma portentosum", "Tricholoma portentoso", familias[18]),
            ("Xerocomus chrysenteron", "Xerocomus dorado", familias[19])
        ]
        especies = []
        for nombre, descripcion, familia in especies_data:
            especie, created = Especie.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': descripcion,
                    'familia': familia
                }
            )
            especies.append(especie)
            if created:
                self.stdout.write(f'Especie creada: {nombre}')
        return especies

    def get_municipios_tabasco(self):
        municipios = Municipio.objects.filter(estado=27)
        if not municipios.exists():
            municipios_tabasco = [
                ("001", "Balancán"),
                ("002", "Cárdenas"),
                ("003", "Centla"),
                ("004", "Centro"),
                ("005", "Comalcalco"),
                ("006", "Cunduacán"),
                ("007", "Emiliano Zapata"),
                ("008", "Huimanguillo"),
                ("009", "Jalpa de Méndez"),
                ("010", "Jonuta"),
                ("011", "Macuspana"),
                ("012", "Nacajuca"),
                ("013", "Paraíso"),
                ("014", "Tacotalpa"),
                ("015", "Teapa"),
                ("016", "Tenosique"),
            ]
            for clave, nombre in municipios_tabasco:
                municipio = Municipio.objects.create(
                    clave=clave,
                    nombre=nombre,
                    estado=27
                )
                self.stdout.write(f'Municipio creado: {nombre}')
            municipios = Municipio.objects.filter(estado=27)
        return list(municipios)

    def download_and_assign_image(self, muestra, image_url):
        """Descarga una imagen desde URL y la asigna a la muestra"""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            # Asignar imagen a la muestra
            with open(temp_file_path, 'rb') as f:
                filename = f"hongo_{muestra.numero_recolecta}.jpg"
                muestra.imagen.save(filename, File(f), save=False)
            
            # Limpiar archivo temporal
            os.unlink(temp_file_path)
            return True
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error descargando imagen: {str(e)}'))
            return False 