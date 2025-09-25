import qrcode
import qrcode.image.pil
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.urls import reverse
from catalogo.models import MuestraBiologica


def generate_qr_code(request, pk):
    """
    Genera un código QR que apunta a la página de detalle de la muestra.
    """
    muestra = get_object_or_404(MuestraBiologica, pk=pk)
    
    # Construir la URL completa de la muestra
    if muestra.tipo_muestra == 'PLANTA':
        url = request.build_absolute_uri(reverse('catalogo:planta-detail', kwargs={'pk': pk}))
    elif muestra.tipo_muestra == 'ALGA':
        url = request.build_absolute_uri(reverse('catalogo:alga-detail', kwargs={'pk': pk}))
    elif muestra.tipo_muestra == 'FRUTOSEMILLA':
        url = request.build_absolute_uri(reverse('catalogo:fruto-detail', kwargs={'pk': pk}))
    elif muestra.tipo_muestra == 'HELECHO':
        url = request.build_absolute_uri(reverse('catalogo:helecho-detail', kwargs={'pk': pk}))
    elif muestra.tipo_muestra == 'HONGO':
        url = request.build_absolute_uri(reverse('catalogo:hongo-detail', kwargs={'pk': pk}))
    elif muestra.tipo_muestra == 'POLEN':
        url = request.build_absolute_uri(reverse('catalogo:polen-detail', kwargs={'pk': pk}))
    else:
        # Fallback a la vista general de muestra
        url = request.build_absolute_uri(reverse('catalogo:muestra-detail', kwargs={'pk': pk}))
    
    # Crear el código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Crear la imagen
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir a respuesta HTTP
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    
    return response


def show_qr_modal(request, pk):
    """
    Vista que muestra un modal con el QR de la muestra.
    """
    muestra = get_object_or_404(MuestraBiologica, pk=pk)
    
    # Construir la URL de la muestra
    if muestra.tipo_muestra == 'PLANTA':
        detail_url = reverse('catalogo:planta-detail', kwargs={'pk': pk})
    elif muestra.tipo_muestra == 'ALGA':
        detail_url = reverse('catalogo:alga-detail', kwargs={'pk': pk})
    elif muestra.tipo_muestra == 'FRUTOSEMILLA':
        detail_url = reverse('catalogo:fruto-detail', kwargs={'pk': pk})
    elif muestra.tipo_muestra == 'HELECHO':
        detail_url = reverse('catalogo:helecho-detail', kwargs={'pk': pk})
    elif muestra.tipo_muestra == 'HONGO':
        detail_url = reverse('catalogo:hongo-detail', kwargs={'pk': pk})
    elif muestra.tipo_muestra == 'POLEN':
        detail_url = reverse('catalogo:polen-detail', kwargs={'pk': pk})
    else:
        detail_url = reverse('catalogo:muestra-detail', kwargs={'pk': pk})
    
    full_url = request.build_absolute_uri(detail_url)
    
    context = {
        'muestra': muestra,
        'qr_url': reverse('catalogo:muestra-qr', kwargs={'pk': pk}),
        'detail_url': full_url,
    }
    
    from django.shortcuts import render
    return render(request, 'catalogo/partials/qr_modal.html', context)

