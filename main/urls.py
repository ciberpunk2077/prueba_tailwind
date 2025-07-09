from django.urls import path
from . import views
 
urlpatterns = [
    path('', views.home, name='home'),
    path('contact222/', views.contact222, name='contact222'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
] 