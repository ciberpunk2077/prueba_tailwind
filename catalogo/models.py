from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import folium
import os
from catalogo.extra import *

# Create your models here.


#Usuarios
class User(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('CAPT', 'Capturista'),
        ('USER', 'Usuario normal'),
    )
    rol = models.CharField(max_length=5, choices=ROLES, default='USER')
    
    # Agrega estos related_name para evitar conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='catalogo_user_set',  # Nombre único
        related_query_name='catalogo_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='catalogo_user_set',  # Nombre único
        related_query_name='catalogo_user'
    )

    class Meta:
        db_table = 'auth_user' 


#Familia
class Familia(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(max_length=500)

    class Meta:
        default_permissions =()

    def __str__(self):
        return f'{self.nombre}'

#Especie
class Especie(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(max_length=500)
    familia = models.ForeignKey("catalogo.Familia", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return f'{self.nombre}'

#Municipio
class Municipio(models.Model):
    clave = models.CharField(max_length=100)
    nombre = models.CharField(max_length=200)
    estado = models.PositiveSmallIntegerField(choices=ESTADOS, default=0)

    def __str__(self):
        return '{}-{} /{}'.format(self.clave, self.nombre, self.estado)

#Muestra base
class MuestraBase(models.Model):

    

    GENERO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('H', 'Hermafrodita'),
        ('ND', 'No determinado'),
    )
    
    
    # genero = models.IntegerField(choices=CHOICES_GENERO, null=True, blank=True)
    genero = models.CharField(max_length=2, choices=GENERO_CHOICES, null=True, blank=True)
    nombre_cientifico = models.CharField(max_length=200)
    nombre_comun = models.CharField(max_length=200, null=True, blank=True)
    
    numero_recolecta = models.CharField(max_length=100, unique=True)  # Único para evitar duplicados
    colonia = models.CharField(max_length=200, null=True, blank=True)
    localidad = models.CharField(max_length=200, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)  # TextField para descripciones largas
    nombre_colector = models.CharField(max_length=200, null=True, blank=True)
    fecha = models.DateField(
        null=True, 
        blank=True,
        help_text="Fecha de recolección de la muestra"
    )
    latitud = models.DecimalField(
        max_digits=50, 
        decimal_places=47, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]  # Validación de rango
    )
    longitud = models.DecimalField(
        max_digits=50, 
        decimal_places=47, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    especie = models.ForeignKey('Especie', on_delete=models.CASCADE, null=True, blank=False)
    municipio = models.ForeignKey('Municipio', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.nombre_cientifico} (Recolecta #{self.numero_recolecta})"

    def get_map(self):
        """Genera un mapa interactivo con la ubicación de la muestra."""
        if self.latitud and self.longitud:
            mapa = folium.Map(
                location=[float(self.latitud), float(self.longitud)], 
                zoom_start=15,
                tiles="OpenStreetMap"
            )
            folium.Marker(
                location=[float(self.latitud), float(self.longitud)], 
                popup=f"<b>{self.nombre_cientifico}</b><br>Recolecta #{self.numero_recolecta}"
            ).add_to(mapa)
            return mapa._repr_html_()  # Retorna HTML para integrar en templates
        return None


# En lugar de repetir el mismo código para cada modelo, podrías:
def get_upload_path_imagen(instance, filename):
    """Genera la ruta de almacenamiento para las imágenes"""
    if instance.pk and instance.especie:
        familia = slugify(instance.especie.familia.nombre) if instance.especie.familia else 'sin-familia'
        especie = slugify(instance.especie.nombre)
        return f"muestras/{familia}/{especie}/{filename}"
    return f"muestras/temporales/{filename}"

class MuestraBiologica(MuestraBase):
    TIPO_MUESTRA_CHOICES = [
        ('ALGA', 'Alga'),
        ('PLANTA', 'Planta'),
        ('FRUTOSEMILLA', 'Frutosemilla'),
        ('POLEN', 'Polen'),
        ('HELECHO', 'Helecho'),
        ('HONGO', 'Hongo'),
        # ... otros tipos
    ]
    
    tipo_muestra = models.CharField(
        max_length=15,  # Aumenté por "FRUTOSEMILLA"
        choices=TIPO_MUESTRA_CHOICES,
        help_text="Tipo de muestra biológica"
    )


    imagen = models.ImageField(
        upload_to='muestras/imagenes/',
        null=True,
        blank=False,
        verbose_name="Imagen de la muestra"
    )

    # Agrega este campo
    # familia = models.ForeignKey(
    #     Familia,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     verbose_name="Familia"
    # )
    
    
    class Meta:
        verbose_name = "Muestra Biológica"
        verbose_name_plural = "Muestras Biológicas"
        permissions = [
            ("can_export", "Puede exportar datos de muestras"),
            ("can_import", "Puede importar datos de muestras"),
        ]
    
    # Mantén el clean() de validación de fecha
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.fecha and self.fecha > timezone.now().date():
            raise ValidationError("La fecha no puede ser futura.")