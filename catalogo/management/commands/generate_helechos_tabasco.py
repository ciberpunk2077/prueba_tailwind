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
    help = 'Genera 500 muestras de helechos nativos de Tabasco, México con imágenes reales'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Eliminar todas las muestras de helechos existentes antes de crear nuevas',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Eliminando muestras de helechos existentes...')
            MuestraBiologica.objects.filter(tipo_muestra='HELECHO').delete()
            self.stdout.write(self.style.SUCCESS('Muestras de helechos eliminadas'))

        # Obtener o crear familias de helechos
        familias_helechos = self.get_or_create_familias_helechos()
        
        # Obtener o crear especies de helechos
        especies_helechos = self.get_or_create_especies_helechos(familias_helechos)
        
        # Obtener municipios de Tabasco
        municipios_tabasco = self.get_municipios_tabasco()
        
        # Generar 500 muestras
        self.stdout.write('Generando 500 muestras de helechos de Tabasco...')
        
        # URLs de imágenes de helechos de Unsplash (URLs válidas)
        fern_image_urls = [
            "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=800&h=600&fit=crop&q=80",
            "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=800&h=600&fit=crop&q=80",
        ]
        
        # Nombres científicos de helechos nativos de Tabasco
        helechos_tabasco = [
            "Adiantum capillus-veneris",
            "Asplenium auritum",
            "Blechnum occidentale",
            "Cyathea mexicana",
            "Dennstaedtia bipinnata",
            "Dryopteris patula",
            "Elaphoglossum latifolium",
            "Gleichenia bifida",
            "Hymenophyllum polyanthos",
            "Lygodium venustum",
            "Microgramma lycopodioides",
            "Nephrolepis exaltata",
            "Osmunda regalis",
            "Pellaea ternifolia",
            "Pityrogramma calomelanos",
            "Polypodium polypodioides",
            "Pteris cretica",
            "Salvinia auriculata",
            "Selaginella lepidophylla",
            "Thelypteris normalis",
            "Trichomanes radicans",
            "Vittaria lineata",
            "Woodsia mexicana",
            "Acrostichum aureum",
            "Anemia mexicana",
            "Blechnum serrulatum",
            "Campyloneurum phyllitidis",
            "Ctenitis submarginalis",
            "Diplazium striatum",
            "Elaphoglossum crinitum",
            "Gleichenia pectinata",
            "Hemionitis palmata",
            "Lomariopsis maxonii",
            "Marattia weinmanniifolia",
            "Nephrolepis biserrata",
            "Osmunda cinnamomea",
            "Pellaea atropurpurea",
            "Pleopeltis polypodioides",
            "Pteridium aquilinum",
            "Salvinia minima",
            "Selaginella pallescens",
            "Thelypteris kunthii",
            "Trichomanes hymenophylloides",
            "Vittaria graminifolia",
            "Woodsia obtusa",
            "Acrostichum danaeifolium",
            "Anemia adiantifolia",
            "Blechnum fragile",
            "Campyloneurum angustifolium",
            "Ctenitis sloanei",
            "Diplazium cristatum",
            "Elaphoglossum decoratum",
            "Gleichenia bifida",
            "Hemionitis tomentosa",
            "Lomariopsis vestita",
            "Marattia alata",
            "Nephrolepis cordifolia",
            "Osmunda claytoniana",
            "Pellaea sagittata",
            "Pleopeltis macrocarpa",
            "Pteris longifolia",
            "Salvinia natans",
            "Selaginella rupestris",
            "Thelypteris ovata",
            "Trichomanes radicans",
            "Vittaria costata",
            "Woodsia ilvensis"
        ]
        
        # Nombres comunes de helechos
        nombres_comunes = [
            "Culantrillo",
            "Helecho de hoja de cuero",
            "Helecho occidental",
            "Helecho arbóreo mexicano",
            "Helecho de Dennstaedtia",
            "Helecho de Dryopteris",
            "Helecho de lengua",
            "Helecho de Gleichenia",
            "Helecho filmy",
            "Helecho trepador",
            "Helecho de Microgramma",
            "Helecho de Boston",
            "Helecho real",
            "Helecho de Pellaea",
            "Helecho dorado",
            "Helecho de Polypodium",
            "Helecho de Cretan",
            "Helecho de agua",
            "Rosa de Jericó",
            "Helecho de Thelypteris",
            "Helecho de Trichomanes",
            "Helecho de Vittaria",
            "Helecho de Woodsia",
            "Helecho de manglar",
            "Helecho de Anemia",
            "Helecho serrulado",
            "Helecho de Campyloneurum",
            "Helecho de Ctenitis",
            "Helecho de Diplazium",
            "Helecho de Elaphoglossum",
            "Helecho de Gleichenia",
            "Helecho de Hemionitis",
            "Helecho de Lomariopsis",
            "Helecho de Marattia",
            "Helecho de Nephrolepis",
            "Helecho de Osmunda",
            "Helecho de Pellaea",
            "Helecho de Pleopeltis",
            "Helecho águila",
            "Helecho de Salvinia",
            "Helecho de Selaginella",
            "Helecho de Thelypteris",
            "Helecho de Trichomanes",
            "Helecho de Vittaria",
            "Helecho de Woodsia",
            "Helecho de Acrostichum",
            "Helecho de Anemia",
            "Helecho frágil",
            "Helecho de Campyloneurum",
            "Helecho de Ctenitis",
            "Helecho de Diplazium",
            "Helecho decorado",
            "Helecho de Gleichenia",
            "Helecho tomentoso",
            "Helecho de Lomariopsis",
            "Helecho alado",
            "Helecho de Nephrolepis",
            "Helecho de Osmunda",
            "Helecho de Pellaea",
            "Helecho de Pleopeltis",
            "Helecho de Pteris",
            "Helecho de Salvinia",
            "Helecho de Selaginella",
            "Helecho de Thelypteris",
            "Helecho de Trichomanes",
            "Helecho de Vittaria",
            "Helecho de Woodsia"
        ]
        
        # Localidades de Tabasco
        localidades_tabasco = [
            "Villahermosa", "Centro", "Cárdenas", "Cunduacán", "Huimanguillo",
            "Macuspana", "Cárdenas", "Comalcalco", "Cunduacán", "Emiliano Zapata",
            "Huimanguillo", "Jalpa de Méndez", "Jonuta", "Macuspana", "Nacajuca",
            "Paraíso", "Tacotalpa", "Teapa", "Tenosique", "Balancán",
            "El Triunfo", "Francisco I. Madero", "Ignacio Gutiérrez Gómez",
            "Jalpa de Méndez", "Jonuta", "Nacajuca", "Paraíso", "Pueblo Nuevo",
            "San Carlos", "San Fernando", "San Juan Bautista", "San Simón",
            "Santa Ana", "Santa Cruz", "Santa María", "Santo Domingo",
            "Tacotalpa", "Teapa", "Tenosique", "Villa Aldama", "Villa Chontalpa"
        ]
        
        # Colonias de Tabasco
        colonias_tabasco = [
            "Centro", "Gaviotas", "Tamarindo", "Atasta", "Pueblo Nuevo",
            "Las Gaviotas", "Los Ríos", "Tabasco 2000", "Prados de Villahermosa",
            "Villa de las Flores", "Villa de los Claustros", "Villa de los Ríos",
            "Villa de las Palmas", "Villa de las Garzas", "Villa de las Gaviotas",
            "Villa de las Flores", "Villa de los Claustros", "Villa de los Ríos",
            "Villa de las Palmas", "Villa de las Garzas", "Villa de las Gaviotas",
            "Villa de las Flores", "Villa de los Claustros", "Villa de los Ríos",
            "Villa de las Palmas", "Villa de las Garzas", "Villa de las Gaviotas",
            "Villa de las Flores", "Villa de los Claustros", "Villa de los Ríos",
            "Villa de las Palmas", "Villa de las Garzas", "Villa de las Gaviotas",
            "Villa de las Flores", "Villa de los Claustros", "Villa de los Ríos",
            "Villa de las Palmas", "Villa de las Garzas", "Villa de las Gaviotas",
            "Villa de las Flores", "Villa de los Claustros", "Villa de los Ríos",
            "Villa de las Palmas", "Villa de las Garzas", "Villa de las Gaviotas",
            "Villa de las Flores", "Villa de los Claustros", "Villa de los Ríos",
            "Villa de las Palmas", "Villa de las Garzas", "Villa de las Gaviotas"
        ]
        
        # Nombres de colectores
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
            "Dr. Gerardo Francisco Mendoza", "Biól. Daniela Fernanda Aguilar", "Dr. Oscar Eduardo Torres",
            "Biól. Andrea Gabriela Méndez", "Dr. Víctor Manuel Hernández", "Biól. Karla Patricia Silva",
            "Dr. Roberto Carlos Vega", "Biól. Ana Sofía Morales", "Dr. José Luis González",
            "Biól. María Fernanda Ruiz", "Dr. Carlos Alberto Pérez", "Biól. Laura Alejandra Castro",
            "Dr. Fernando José Díaz", "Biól. Carmen Elena Sánchez", "Dr. Miguel Ángel Ramírez",
            "Biól. Rosa Patricia Ortiz", "Dr. Juan Carlos Martínez", "Biól. Gabriela Alejandra Flores",
            "Dr. Luis Alberto Jiménez", "Biól. Claudia Sofía Rodríguez", "Dr. Eduardo José Luna",
            "Biól. Verónica Alejandra Vargas", "Dr. Ricardo Antonio Moreno", "Biól. Mariana Isabel Reyes"
        ]
        
        muestras_creadas = 0
        errores = 0
        
        for i in range(500):
            try:
                # Generar número de recolecta único
                numero_recolecta = f"HEL-{str(uuid.uuid4())[:8].upper()}"
                
                # Seleccionar datos aleatorios
                especie = random.choice(especies_helechos)
                municipio = random.choice(municipios_tabasco)
                localidad = random.choice(localidades_tabasco)
                colonia = random.choice(colonias_tabasco)
                nombre_colector = random.choice(colectores)
                
                # Generar fecha aleatoria en los últimos 5 años
                fecha_inicio = date(2019, 1, 1)
                fecha_fin = date.today()
                dias_entre_fechas = (fecha_fin - fecha_inicio).days
                fecha_aleatoria = fecha_inicio + timedelta(days=random.randint(0, dias_entre_fechas))
                
                # Generar coordenadas aleatorias en Tabasco
                latitud = random.uniform(17.5, 18.5)  # Rango de latitud de Tabasco
                longitud = random.uniform(-94.0, -91.0)  # Rango de longitud de Tabasco
                
                # Crear la muestra
                muestra = MuestraBiologica(
                    tipo_muestra='HELECHO',
                    nombre_cientifico=especie.nombre,
                    nombre_comun=random.choice(nombres_comunes),
                    numero_recolecta=numero_recolecta,
                    colonia=colonia,
                    localidad=localidad,
                    descripcion=f"Helecho recolectado en {localidad}, Tabasco. Especie nativa de la región con características típicas de los helechos tropicales.",
                    nombre_colector=nombre_colector,
                    fecha=fecha_aleatoria,
                    latitud=latitud,
                    longitud=longitud,
                    especie=especie,
                    municipio=municipio,
                    genero=random.choice(['M', 'F', 'H', 'ND'])
                )
                
                # Descargar y asignar imagen
                imagen_url = random.choice(fern_image_urls)
                if self.download_and_assign_image(muestra, imagen_url):
                    muestra.save()
                    muestras_creadas += 1
                    
                    if muestras_creadas % 50 == 0:
                        self.stdout.write(f'Progreso: {muestras_creadas} muestras creadas...')
                else:
                    errores += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creando muestra {i+1}: {str(e)}'))
                errores += 1
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'¡Completado! Se crearon {muestras_creadas} muestras de helechos de Tabasco. '
                f'Errores: {errores}'
            )
        )

    def get_or_create_familias_helechos(self):
        """Obtiene o crea las familias de helechos"""
        familias_data = [
            ("Adiantaceae", "Familia de helechos que incluye el culantrillo"),
            ("Aspleniaceae", "Familia de helechos con esporangios en líneas"),
            ("Blechnaceae", "Familia de helechos con frondas pinnadas"),
            ("Cyatheaceae", "Familia de helechos arbóreos"),
            ("Dennstaedtiaceae", "Familia de helechos terrestres"),
            ("Dryopteridaceae", "Familia de helechos con esporangios redondos"),
            ("Elaphoglossaceae", "Familia de helechos epífitos"),
            ("Gleicheniaceae", "Familia de helechos con frondas bifurcadas"),
            ("Hymenophyllaceae", "Familia de helechos filmy"),
            ("Lygodiaceae", "Familia de helechos trepadores"),
            ("Polypodiaceae", "Familia de helechos epífitos"),
            ("Pteridaceae", "Familia de helechos con esporangios marginales"),
            ("Salviniaceae", "Familia de helechos acuáticos"),
            ("Selaginellaceae", "Familia de licopodios"),
            ("Thelypteridaceae", "Familia de helechos terrestres"),
            ("Vittariaceae", "Familia de helechos epífitos"),
            ("Woodsiaceae", "Familia de helechos terrestres"),
            ("Acrostichaceae", "Familia de helechos de manglar"),
            ("Anemiaceae", "Familia de helechos con frondas fértiles"),
            ("Marattiaceae", "Familia de helechos primitivos"),
            ("Osmundaceae", "Familia de helechos reales"),
            ("Schizaeaceae", "Familia de helechos con esporangios especializados")
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

    def get_or_create_especies_helechos(self, familias):
        """Obtiene o crea las especies de helechos"""
        especies_data = [
            ("Adiantum capillus-veneris", "Culantrillo", familias[0]),
            ("Asplenium auritum", "Helecho de hoja de cuero", familias[1]),
            ("Blechnum occidentale", "Helecho occidental", familias[2]),
            ("Cyathea mexicana", "Helecho arbóreo mexicano", familias[3]),
            ("Dennstaedtia bipinnata", "Helecho de Dennstaedtia", familias[4]),
            ("Dryopteris patula", "Helecho de Dryopteris", familias[5]),
            ("Elaphoglossum latifolium", "Helecho de lengua", familias[6]),
            ("Gleichenia bifida", "Helecho de Gleichenia", familias[7]),
            ("Hymenophyllum polyanthos", "Helecho filmy", familias[8]),
            ("Lygodium venustum", "Helecho trepador", familias[9]),
            ("Microgramma lycopodioides", "Helecho de Microgramma", familias[10]),
            ("Nephrolepis exaltata", "Helecho de Boston", familias[10]),
            ("Osmunda regalis", "Helecho real", familias[21]),
            ("Pellaea ternifolia", "Helecho de Pellaea", familias[5]),
            ("Pityrogramma calomelanos", "Helecho dorado", familias[11]),
            ("Polypodium polypodioides", "Helecho de Polypodium", familias[10]),
            ("Pteris cretica", "Helecho de Cretan", familias[11]),
            ("Salvinia auriculata", "Helecho de agua", familias[12]),
            ("Selaginella lepidophylla", "Rosa de Jericó", familias[13]),
            ("Thelypteris normalis", "Helecho de Thelypteris", familias[14]),
            ("Trichomanes radicans", "Helecho de Trichomanes", familias[8]),
            ("Vittaria lineata", "Helecho de Vittaria", familias[15]),
            ("Woodsia mexicana", "Helecho de Woodsia", familias[16]),
            ("Acrostichum aureum", "Helecho de manglar", familias[17]),
            ("Anemia mexicana", "Helecho de Anemia", familias[18]),
            ("Blechnum serrulatum", "Helecho serrulado", familias[2]),
            ("Campyloneurum phyllitidis", "Helecho de Campyloneurum", familias[10]),
            ("Ctenitis submarginalis", "Helecho de Ctenitis", familias[5]),
            ("Diplazium striatum", "Helecho de Diplazium", familias[5]),
            ("Elaphoglossum crinitum", "Helecho de Elaphoglossum", familias[6]),
            ("Gleichenia pectinata", "Helecho de Gleichenia", familias[7]),
            ("Hemionitis palmata", "Helecho de Hemionitis", familias[11]),
            ("Lomariopsis maxonii", "Helecho de Lomariopsis", familias[5]),
            ("Marattia weinmanniifolia", "Helecho de Marattia", familias[20]),
            ("Nephrolepis biserrata", "Helecho de Nephrolepis", familias[10]),
            ("Osmunda cinnamomea", "Helecho de Osmunda", familias[21]),
            ("Pellaea atropurpurea", "Helecho de Pellaea", familias[5]),
            ("Pleopeltis polypodioides", "Helecho de Pleopeltis", familias[10]),
            ("Pteridium aquilinum", "Helecho águila", familias[4]),
            ("Salvinia minima", "Helecho de Salvinia", familias[12]),
            ("Selaginella pallescens", "Helecho de Selaginella", familias[13]),
            ("Thelypteris kunthii", "Helecho de Thelypteris", familias[14]),
            ("Trichomanes hymenophylloides", "Helecho de Trichomanes", familias[8]),
            ("Vittaria graminifolia", "Helecho de Vittaria", familias[15]),
            ("Woodsia obtusa", "Helecho de Woodsia", familias[16]),
            ("Acrostichum danaeifolium", "Helecho de Acrostichum", familias[17]),
            ("Anemia adiantifolia", "Helecho de Anemia", familias[18]),
            ("Blechnum fragile", "Helecho frágil", familias[2]),
            ("Campyloneurum angustifolium", "Helecho de Campyloneurum", familias[10]),
            ("Ctenitis sloanei", "Helecho de Ctenitis", familias[5]),
            ("Diplazium cristatum", "Helecho de Diplazium", familias[5]),
            ("Elaphoglossum decoratum", "Helecho decorado", familias[6]),
            ("Gleichenia bifida", "Helecho de Gleichenia", familias[7]),
            ("Hemionitis tomentosa", "Helecho tomentoso", familias[11]),
            ("Lomariopsis vestita", "Helecho de Lomariopsis", familias[5]),
            ("Marattia alata", "Helecho alado", familias[20]),
            ("Nephrolepis cordifolia", "Helecho de Nephrolepis", familias[10]),
            ("Osmunda claytoniana", "Helecho de Osmunda", familias[21]),
            ("Pellaea sagittata", "Helecho de Pellaea", familias[5]),
            ("Pleopeltis macrocarpa", "Helecho de Pleopeltis", familias[10]),
            ("Pteris longifolia", "Helecho de Pteris", familias[11]),
            ("Salvinia natans", "Helecho de Salvinia", familias[12]),
            ("Selaginella rupestris", "Helecho de Selaginella", familias[13]),
            ("Thelypteris ovata", "Helecho de Thelypteris", familias[14]),
            ("Trichomanes radicans", "Helecho de Trichomanes", familias[8]),
            ("Vittaria costata", "Helecho de Vittaria", familias[15]),
            ("Woodsia ilvensis", "Helecho de Woodsia", familias[16])
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
        """Obtiene los municipios de Tabasco"""
        # Buscar el estado de Tabasco (ID 27 según extra.py)
        municipios = Municipio.objects.filter(estado=27)
        
        if not municipios.exists():
            # Crear municipios de Tabasco si no existen
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
                    estado=27  # Tabasco
                )
                self.stdout.write(f'Municipio creado: {nombre}')
            
            municipios = Municipio.objects.filter(estado=27)
        
        return list(municipios)

    def download_and_assign_image(self, muestra, image_url):
        """Descarga una imagen y la asigna a la muestra"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(image_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            # Asignar imagen a la muestra
            with open(temp_file_path, 'rb') as img_file:
                filename = f"helecho_{muestra.numero_recolecta}.jpg"
                muestra.imagen.save(filename, File(img_file), save=False)
            
            # Limpiar archivo temporal
            os.unlink(temp_file_path)
            return True
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error descargando imagen: {str(e)}'))
            return False 