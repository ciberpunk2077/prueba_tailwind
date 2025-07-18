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
    help = 'Genera 1000 muestras de frutos nativos de Tabasco, México con imágenes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Eliminar todas las muestras de frutos existentes antes de crear nuevas',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Eliminando muestras de frutos existentes...')
            MuestraBiologica.objects.filter(tipo_muestra='FRUTOSEMILLA').delete()
            self.stdout.write(self.style.SUCCESS('Muestras de frutos eliminadas'))

        # Obtener o crear familias de frutos
        familias_frutos = self.get_or_create_familias_frutos()
        
        # Obtener o crear especies de frutos
        especies_frutos = self.get_or_create_especies_frutos(familias_frutos)
        
        # Obtener municipios de Tabasco
        municipios_tabasco = self.get_municipios_tabasco()
        
        # Generar 1000 muestras
        self.stdout.write('Generando 1000 muestras de frutos de Tabasco...')
        
        # Nombres científicos de frutos nativos de Tabasco
        frutos_tabasco = [
            "Annona muricata", "Annona reticulata", "Annona squamosa", "Annona cherimola",
            "Artocarpus altilis", "Artocarpus heterophyllus", "Averrhoa carambola",
            "Bactris gasipaes", "Bixa orellana", "Brosimum alicastrum",
            "Byrsonima crassifolia", "Calocarpum mammosum", "Carica papaya",
            "Chrysophyllum cainito", "Citrus aurantium", "Citrus aurantifolia",
            "Citrus grandis", "Citrus limon", "Citrus reticulata", "Citrus sinensis",
            "Cocos nucifera", "Crescentia cujete", "Cucurbita moschata",
            "Cucurbita pepo", "Diospyros digyna", "Eugenia uniflora",
            "Ficus carica", "Genipa americana", "Gustavia superba",
            "Hylocereus undatus", "Inga edulis", "Inga jinicuil",
            "Lonchocarpus violaceus", "Mammea americana", "Mangifera indica",
            "Manilkara zapota", "Melicoccus bijugatus", "Morus alba",
            "Musa acuminata", "Musa balbisiana", "Myrciaria dubia",
            "Opuntia ficus-indica", "Passiflora edulis", "Passiflora ligularis",
            "Persea americana", "Phoenix dactylifera", "Physalis peruviana",
            "Pimenta dioica", "Pithecellobium dulce", "Pouteria sapota",
            "Prunus persica", "Psidium guajava", "Punica granatum",
            "Quararibea funebris", "Rheedia edulis", "Rollinia mucosa",
            "Saccharum officinarum", "Salacca zalacca", "Spondias mombin",
            "Spondias purpurea", "Syzygium malaccense", "Tamarindus indica",
            "Theobroma cacao", "Vaccinium corymbosum", "Vitis vinifera",
            "Ziziphus jujuba", "Ziziphus mauritiana", "Achras zapota",
            "Anacardium occidentale", "Ananas comosus", "Arachis hypogaea",
            "Bertholletia excelsa", "Carya illinoinensis", "Castanea sativa",
            "Coffea arabica", "Cola acuminata", "Corylus avellana",
            "Cucumis melo", "Cucumis sativus", "Cydonia oblonga",
            "Dovyalis caffra", "Durio zibethinus", "Eriobotrya japonica",
            "Fragaria x ananassa", "Garcinia mangostana", "Juglans regia",
            "Litchi chinensis", "Malus domestica", "Nephelium lappaceum",
            "Olea europaea", "Persea schiedeana", "Phoenix canariensis",
            "Prunus armeniaca", "Prunus avium", "Prunus domestica",
            "Prunus salicina", "Pyrus communis", "Ribes nigrum",
            "Rubus idaeus", "Rubus occidentalis", "Solanum lycopersicum",
            "Solanum melongena", "Solanum tuberosum", "Vaccinium macrocarpon",
            "Vaccinium myrtillus", "Vitis labrusca", "Ziziphus spina-christi"
        ]
        
        # Nombres comunes de frutos
        nombres_comunes = [
            "Guanábana", "Anona", "Chirimoya", "Cherimoya", "Fruta del pan",
            "Jackfruit", "Carambola", "Pejibaye", "Achiote", "Ramon",
            "Nance", "Mamey", "Papaya", "Caimito", "Naranja agria",
            "Lima", "Toronja", "Limón", "Mandarina", "Naranja dulce",
            "Coco", "Jícaro", "Calabaza", "Calabacita", "Zapote negro",
            "Pitanga", "Higo", "Genipa", "Membrillo", "Pitahaya",
            "Guaba", "Jinicuil", "Mata ratón", "Mamey americano", "Mango",
            "Chicozapote", "Mamoncillo", "Mora", "Plátano", "Plátano macho",
            "Camu camu", "Nopal", "Maracuyá", "Granadilla", "Aguacate",
            "Dátil", "Uchuva", "Pimienta", "Guamúchil", "Mamey colorado",
            "Durazno", "Guayaba", "Granada", "Molleja", "Bacuri",
            "Anona", "Caña de azúcar", "Salak", "Jobo", "Ciruela",
            "Manzana malaya", "Tamarindo", "Cacao", "Arándano", "Uva",
            "Jujube", "Jujube indio", "Zapote", "Marañón", "Piña",
            "Cacahuate", "Nuez de Brasil", "Nuez pecanera", "Castaña",
            "Café", "Cola", "Avellana", "Melón", "Pepino", "Membrillo",
            "Kei apple", "Durian", "Níspero", "Fresa", "Mangostán",
            "Nuez", "Lichi", "Manzana", "Rambután", "Aceituna",
            "Aguacate criollo", "Palma canaria", "Albaricoque", "Cereza",
            "Ciruela europea", "Ciruela japonesa", "Pera", "Grosella negra",
            "Frambuesa", "Frambuesa negra", "Tomate", "Berenjena", "Papa",
            "Arándano rojo", "Arándano azul", "Uva Concord", "Cristo"
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
        
        for i in range(1000):
            try:
                # Generar número de recolecta único
                numero_recolecta = f"FRU-{str(uuid.uuid4())[:8].upper()}"
                
                # Seleccionar datos aleatorios
                especie = random.choice(especies_frutos)
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
                    tipo_muestra='FRUTOSEMILLA',
                    nombre_cientifico=especie.nombre,
                    nombre_comun=random.choice(nombres_comunes),
                    numero_recolecta=numero_recolecta,
                    colonia=colonia,
                    localidad=localidad,
                    descripcion=f"Fruto recolectado en {localidad}, Tabasco. Especie nativa de la región con características típicas de los frutos tropicales.",
                    nombre_colector=nombre_colector,
                    fecha=fecha_aleatoria,
                    latitud=latitud,
                    longitud=longitud,
                    especie=especie,
                    municipio=municipio,
                    genero=random.choice(['M', 'F', 'H', 'ND'])
                )
                
                # Crear imagen placeholder
                self.create_placeholder_image(muestra)
                muestra.save()
                muestras_creadas += 1
                    
                if muestras_creadas % 100 == 0:
                    self.stdout.write(f'Progreso: {muestras_creadas} muestras creadas...')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creando muestra {i+1}: {str(e)}'))
                errores += 1
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'¡Completado! Se crearon {muestras_creadas} muestras de frutos de Tabasco. '
                f'Errores: {errores}'
            )
        )

    def create_placeholder_image(self, muestra):
        """Crea una imagen placeholder para la muestra"""
        try:
            # Crear directorio si no existe
            media_dir = 'media/muestras/imagenes'
            os.makedirs(media_dir, exist_ok=True)
            
            # Crear archivo de imagen placeholder
            filename = f"fruto_{muestra.numero_recolecta}.txt"
            filepath = os.path.join(media_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Imagen placeholder para {muestra.nombre_cientifico}\n")
                f.write(f"Recolecta: {muestra.numero_recolecta}\n")
                f.write(f"Localidad: {muestra.localidad}, Tabasco\n")
                f.write(f"Fecha: {muestra.fecha}\n")
                f.write(f"Colector: {muestra.nombre_colector}\n")
                f.write("Esta es una imagen simulada para representar el fruto recolectado.")
            
            # Asignar la imagen a la muestra
            with open(filepath, 'rb') as img_file:
                muestra.imagen.save(filename, File(img_file), save=False)
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error creando imagen placeholder: {str(e)}'))

    def get_or_create_familias_frutos(self):
        """Obtiene o crea las familias de frutos"""
        familias_data = [
            ("Annonaceae", "Familia de las anonas y guanábanas"),
            ("Moraceae", "Familia de las moras y higos"),
            ("Rutaceae", "Familia de los cítricos"),
            ("Arecaceae", "Familia de las palmas"),
            ("Musaceae", "Familia de los plátanos"),
            ("Sapotaceae", "Familia de los zapotes"),
            ("Myrtaceae", "Familia de las guayabas"),
            ("Passifloraceae", "Familia de las pasifloras"),
            ("Lauraceae", "Familia de los aguacates"),
            ("Solanaceae", "Familia de las solanáceas"),
            ("Cucurbitaceae", "Familia de las calabazas"),
            ("Rosaceae", "Familia de las rosáceas"),
            ("Fabaceae", "Familia de las leguminosas"),
            ("Malvaceae", "Familia de las malváceas"),
            ("Anacardiaceae", "Familia de los marañones"),
            ("Bromeliaceae", "Familia de las bromelias"),
            ("Rubiaceae", "Familia del café"),
            ("Ebenaceae", "Familia de los ébanos"),
            ("Oxalidaceae", "Familia de las oxalidáceas"),
            ("Bixaceae", "Familia del achiote"),
            ("Caricaceae", "Familia de las papayas"),
            ("Cactaceae", "Familia de los cactus"),
            ("Punicaceae", "Familia de las granadas"),
            ("Tamaricaceae", "Familia de los tamarindos"),
            ("Sterculiaceae", "Familia del cacao"),
            ("Ericaceae", "Familia de los arándanos"),
            ("Vitaceae", "Familia de las uvas"),
            ("Rhamnaceae", "Familia de los jujubes"),
            ("Juglandaceae", "Familia de las nueces"),
            ("Fagaceae", "Familia de las castañas"),
            ("Betulaceae", "Familia de las avellanas"),
            ("Oleaceae", "Familia de las aceitunas"),
            ("Grossulariaceae", "Familia de las grosellas"),
            ("Actinidiaceae", "Familia de los kiwis"),
            ("Bombacaceae", "Familia de las ceibas"),
            ("Lecythidaceae", "Familia de las lecitidáceas"),
            ("Clusiaceae", "Familia de las clusiáceas"),
            ("Meliaceae", "Familia de las meliáceas"),
            ("Sapindaceae", "Familia de las sapindáceas"),
            ("Burseraceae", "Familia de las burseráceas"),
            ("Combretaceae", "Familia de las combretáceas"),
            ("Myristicaceae", "Familia de las miristicáceas"),
            ("Zingiberaceae", "Familia de los jengibres"),
            ("Heliconiaceae", "Familia de las heliconiáceas"),
            ("Cannaceae", "Familia de las cannáceas"),
            ("Marantaceae", "Familia de las marantáceas"),
            ("Costaceae", "Familia de las costáceas"),
            ("Strelitziaceae", "Familia de las strelitziáceas"),
            ("Musaceae", "Familia de los plátanos"),
            ("Zingiberaceae", "Familia de los jengibres"),
            ("Cannaceae", "Familia de las cannáceas"),
            ("Marantaceae", "Familia de las marantáceas"),
            ("Costaceae", "Familia de las costáceas"),
            ("Strelitziaceae", "Familia de las strelitziáceas")
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

    def get_or_create_especies_frutos(self, familias):
        """Obtiene o crea las especies de frutos"""
        especies_data = [
            ("Annona muricata", "Guanábana", familias[0]),
            ("Annona reticulata", "Anona", familias[0]),
            ("Annona squamosa", "Chirimoya", familias[0]),
            ("Annona cherimola", "Cherimoya", familias[0]),
            ("Artocarpus altilis", "Fruta del pan", familias[1]),
            ("Artocarpus heterophyllus", "Jackfruit", familias[1]),
            ("Averrhoa carambola", "Carambola", familias[19]),
            ("Bactris gasipaes", "Pejibaye", familias[3]),
            ("Bixa orellana", "Achiote", familias[20]),
            ("Brosimum alicastrum", "Ramon", familias[1]),
            ("Byrsonima crassifolia", "Nance", familias[13]),
            ("Calocarpum mammosum", "Mamey", familias[5]),
            ("Carica papaya", "Papaya", familias[21]),
            ("Chrysophyllum cainito", "Caimito", familias[5]),
            ("Citrus aurantium", "Naranja agria", familias[2]),
            ("Citrus aurantifolia", "Lima", familias[2]),
            ("Citrus grandis", "Toronja", familias[2]),
            ("Citrus limon", "Limón", familias[2]),
            ("Citrus reticulata", "Mandarina", familias[2]),
            ("Citrus sinensis", "Naranja dulce", familias[2]),
            ("Cocos nucifera", "Coco", familias[3]),
            ("Crescentia cujete", "Jícaro", familias[1]),
            ("Cucurbita moschata", "Calabaza", familias[10]),
            ("Cucurbita pepo", "Calabacita", familias[10]),
            ("Diospyros digyna", "Zapote negro", familias[17]),
            ("Eugenia uniflora", "Pitanga", familias[6]),
            ("Ficus carica", "Higo", familias[1]),
            ("Genipa americana", "Genipa", familias[1]),
            ("Gustavia superba", "Membrillo", familias[28]),
            ("Hylocereus undatus", "Pitahaya", familias[22]),
            ("Inga edulis", "Guaba", familias[12]),
            ("Inga jinicuil", "Jinicuil", familias[12]),
            ("Lonchocarpus violaceus", "Mata ratón", familias[12]),
            ("Mammea americana", "Mamey americano", familias[5]),
            ("Mangifera indica", "Mango", familias[14]),
            ("Manilkara zapota", "Chicozapote", familias[5]),
            ("Melicoccus bijugatus", "Mamoncillo", familias[30]),
            ("Morus alba", "Mora", familias[1]),
            ("Musa acuminata", "Plátano", familias[4]),
            ("Musa balbisiana", "Plátano macho", familias[4]),
            ("Myrciaria dubia", "Camu camu", familias[6]),
            ("Opuntia ficus-indica", "Nopal", familias[22]),
            ("Passiflora edulis", "Maracuyá", familias[7]),
            ("Passiflora ligularis", "Granadilla", familias[7]),
            ("Persea americana", "Aguacate", familias[8]),
            ("Phoenix dactylifera", "Dátil", familias[3]),
            ("Physalis peruviana", "Uchuva", familias[9]),
            ("Pimenta dioica", "Pimienta", familias[6]),
            ("Pithecellobium dulce", "Guamúchil", familias[12]),
            ("Pouteria sapota", "Mamey colorado", familias[5]),
            ("Prunus persica", "Durazno", familias[11]),
            ("Psidium guajava", "Guayaba", familias[6]),
            ("Punica granatum", "Granada", familias[23]),
            ("Quararibea funebris", "Molleja", familias[1]),
            ("Rheedia edulis", "Bacuri", familias[29]),
            ("Rollinia mucosa", "Anona", familias[0]),
            ("Saccharum officinarum", "Caña de azúcar", familias[31]),
            ("Salacca zalacca", "Salak", familias[3]),
            ("Spondias mombin", "Jobo", familias[14]),
            ("Spondias purpurea", "Ciruela", familias[14]),
            ("Syzygium malaccense", "Manzana malaya", familias[6]),
            ("Tamarindus indica", "Tamarindo", familias[24]),
            ("Theobroma cacao", "Cacao", familias[26]),
            ("Vaccinium corymbosum", "Arándano", familias[27]),
            ("Vitis vinifera", "Uva", familias[28]),
            ("Ziziphus jujuba", "Jujube", familias[30]),
            ("Ziziphus mauritiana", "Jujube indio", familias[30]),
            ("Achras zapota", "Zapote", familias[5]),
            ("Anacardium occidentale", "Marañón", familias[14]),
            ("Ananas comosus", "Piña", familias[15]),
            ("Arachis hypogaea", "Cacahuate", familias[12]),
            ("Bertholletia excelsa", "Nuez de Brasil", familias[28]),
            ("Carya illinoinensis", "Nuez pecanera", familias[30]),
            ("Castanea sativa", "Castaña", familias[31]),
            ("Coffea arabica", "Café", familias[16]),
            ("Cola acuminata", "Cola", familias[26]),
            ("Corylus avellana", "Avellana", familias[32]),
            ("Cucumis melo", "Melón", familias[10]),
            ("Cucumis sativus", "Pepino", familias[10]),
            ("Cydonia oblonga", "Membrillo", familias[11]),
            ("Dovyalis caffra", "Kei apple", familias[11]),
            ("Durio zibethinus", "Durian", familias[1]),
            ("Eriobotrya japonica", "Níspero", familias[11]),
            ("Fragaria x ananassa", "Fresa", familias[11]),
            ("Garcinia mangostana", "Mangostán", familias[29]),
            ("Juglans regia", "Nuez", familias[30]),
            ("Litchi chinensis", "Lichi", familias[30]),
            ("Malus domestica", "Manzana", familias[11]),
            ("Nephelium lappaceum", "Rambután", familias[30]),
            ("Olea europaea", "Aceituna", familias[33]),
            ("Persea schiedeana", "Aguacate criollo", familias[8]),
            ("Phoenix canariensis", "Palma canaria", familias[3]),
            ("Prunus armeniaca", "Albaricoque", familias[11]),
            ("Prunus avium", "Cereza", familias[11]),
            ("Prunus domestica", "Ciruela europea", familias[11]),
            ("Prunus salicina", "Ciruela japonesa", familias[11]),
            ("Pyrus communis", "Pera", familias[11]),
            ("Ribes nigrum", "Grosella negra", familias[34]),
            ("Rubus idaeus", "Frambuesa", familias[11]),
            ("Rubus occidentalis", "Frambuesa negra", familias[11]),
            ("Solanum lycopersicum", "Tomate", familias[9]),
            ("Solanum melongena", "Berenjena", familias[9]),
            ("Solanum tuberosum", "Papa", familias[9]),
            ("Vaccinium macrocarpon", "Arándano rojo", familias[27]),
            ("Vaccinium myrtillus", "Arándano azul", familias[27]),
            ("Vitis labrusca", "Uva Concord", familias[28]),
            ("Ziziphus spina-christi", "Cristo", familias[30])
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