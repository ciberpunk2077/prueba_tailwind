// Funciones reutilizables para el catálogo
// ======================================

// Función para el dropdown de categorías
function toggleDropdown() {
    const dropdown = document.getElementById('dropdown');
    if (dropdown) {
        dropdown.classList.toggle('hidden');
    }
}

// Función para cerrar dropdown cuando se hace clic fuera
function setupDropdownClose() {
    document.addEventListener('click', function (event) {
        const dropdown = document.getElementById('dropdown');
        const button = event.target.closest('button');
        if (!button || !button.onclick) {
            if(dropdown) dropdown.classList.add('hidden');
        }
    });
}

// Función para el modal de imágenes
function setupImageModal() {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalTitle = document.getElementById('modalTitle');
    const modalSubtitle = document.getElementById('modalSubtitle');
    const closeModal = document.getElementById('closeModal');
    
    if (!modal || !modalImage || !closeModal) return;
    
    // Función para abrir el modal
    function openModal(imageSrc, imageAlt, title, subtitle) {
        modalImage.src = imageSrc;
        modalImage.alt = imageAlt;
        modalTitle.textContent = title || imageAlt;
        modalSubtitle.textContent = subtitle || '';
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Prevenir scroll
        
        // Asegurar que la imagen se cargue correctamente
        modalImage.onload = function() {
            // Ajustar el tamaño de la imagen para que sea consistente
            const container = modalImage.parentElement;
            const containerWidth = container.clientWidth - 64; // Restar padding
            const containerHeight = container.clientHeight - 64; // Restar padding
            
            // Calcular el tamaño óptimo manteniendo proporciones
            const imgAspectRatio = this.naturalWidth / this.naturalHeight;
            const containerAspectRatio = containerWidth / containerHeight;
            
            let finalWidth, finalHeight;
            
            if (imgAspectRatio > containerAspectRatio) {
                // Imagen más ancha que el contenedor
                finalWidth = Math.min(containerWidth, 1200); // Máximo 1200px de ancho
                finalHeight = finalWidth / imgAspectRatio;
            } else {
                // Imagen más alta que el contenedor
                finalHeight = Math.min(containerHeight, 800); // Máximo 800px de alto
                finalWidth = finalHeight * imgAspectRatio;
            }
            
            // Aplicar tamaño mínimo
            finalWidth = Math.max(finalWidth, 400);
            finalHeight = Math.max(finalHeight, 400);
            
            this.style.width = finalWidth + 'px';
            this.style.height = finalHeight + 'px';
        };
    }
    
    // Función para cerrar el modal
    function closeModalFunc() {
        modal.classList.add('hidden');
        document.body.style.overflow = ''; // Restaurar scroll
    }
    
    // Event listeners para cerrar el modal
    closeModal.addEventListener('click', closeModalFunc);
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModalFunc();
        }
    });
    
    // Cerrar con la tecla Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
            closeModalFunc();
        }
    });
    
    // Hacer todas las imágenes clickeables
    const images = document.querySelectorAll('img[src*="/media/"]'); // Solo imágenes de media
    images.forEach(img => {
        img.style.cursor = 'pointer';
        img.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const imageSrc = this.src;
            const imageAlt = this.alt;
            
            // Obtener información del espécimen desde la fila/tarjeta
            const row = this.closest('tr, .bg-white');
            let title = imageAlt;
            let subtitle = '';
            
            if (row) {
                // Buscar el nombre científico
                const scientificName = row.querySelector('.text-sm.font-semibold, h3');
                if (scientificName) {
                    title = scientificName.textContent.trim();
                }
                
                // Buscar información adicional
                const commonName = row.querySelector('.text-sm.text-gray-900');
                if (commonName && commonName.textContent.trim() !== title) {
                    subtitle = commonName.textContent.trim();
                }
            }
            
            openModal(imageSrc, imageAlt, title, subtitle);
        });
    });
}

// Función para el filtro por familia
function setupFamiliaFilter() {
    const familiaFilter = document.getElementById('familia-filter');
    if (familiaFilter) {
        familiaFilter.addEventListener('change', function() {
            const selectedFamilia = this.value;
            const currentUrl = new URL(window.location);
            
            if (selectedFamilia) {
                currentUrl.searchParams.set('familia', selectedFamilia);
            } else {
                currentUrl.searchParams.delete('familia');
            }
            
            // Mantener la página actual si existe
            const currentPage = currentUrl.searchParams.get('page');
            if (currentPage) {
                currentUrl.searchParams.set('page', '1'); // Resetear a la primera página
            }
            
            window.location.href = currentUrl.toString();
        });
    }
}

// Función principal que inicializa todas las funcionalidades
function initCatalogoFunctions() {
    setupDropdownClose();
    setupImageModal();
    setupFamiliaFilter();
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initCatalogoFunctions); 