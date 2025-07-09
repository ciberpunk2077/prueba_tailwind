from django.urls import path
from . import views
 
urlpatterns = [
    path('', views.home, name='home'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('datos/', views.datos, name='datos'),
    path('presentacion/', views.presentacion, name='presentacion'),
    path('test-busqueda/', views.test_busqueda, name='test_busqueda'),
] 