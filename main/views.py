from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'herbario_home.html')

def about(request):
    return render(request, 'main/about.html')

def contact(request):
    return render(request, 'main/contact.html')

def contact222(request):
    return render(request, 'base.html')
