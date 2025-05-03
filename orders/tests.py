from django.http import HttpResponse
from django.conf import settings
import os



from django.http import FileResponse, HttpResponse
import os
from django.conf import settings

def serve_default_image(request, field_name):
    """Directly serve a default image file"""
    image_path = os.path.join(settings.BASE_DIR, 'static', 'default_images', f'default_{field_name}.jpg')
    
    if os.path.exists(image_path):
        try:
            return FileResponse(open(image_path, 'rb'), content_type='image/jpeg')
        except Exception as e:
            return HttpResponse(f"Error serving file: {str(e)}", status=500)
    
    return HttpResponse(f"Image not found: {image_path}", status=404)





def test_static_serving(request):
    """Test if static files are being served correctly"""
    # Path to the image we know exists
    image_path = os.path.join(settings.BASE_DIR, 'static', 'default_images', 'default_image_carrousel_1.jpg')
    image_exists = os.path.exists(image_path)
    
    # Build the static URL
    image_url = f"{settings.STATIC_URL}default_images/default_image_carrousel_1.jpg"
    
    # Direct serving URL
    direct_url = f"/default-image/image_carrousel_1/"
    
    # Build response
    response = f"""
    <h1>Static File Serving Test</h1>
    <p>Image path: {image_path}</p>
    <p>Image exists: {image_exists}</p>
    
    <h2>Try accessing via static URL:</h2>
    <p>Static URL: {image_url}</p>
    <img src="{image_url}" alt="Test image via static URL" style="max-width: 500px;">
    
    <h2>Try accessing via direct URL:</h2>
    <p>Direct URL: {direct_url}</p>
    <img src="{direct_url}" alt="Test image via direct URL" style="max-width: 500px;">
    
    <h2>Debug info:</h2>
    <p>STATIC_URL: {settings.STATIC_URL}</p>
    <p>STATICFILES_DIRS: {settings.STATICFILES_DIRS}</p>
    <p>BASE_DIR: {settings.BASE_DIR}</p>
    """
    
    return HttpResponse(response)











from django.http import HttpResponse
import os
from django.conf import settings

def debug_images(request):
    """Vista para depurar problemas con imágenes"""
    # Verificar configuración de WhiteNoise
    whitenoise_enabled = 'whitenoise.middleware.WhiteNoiseMiddleware' in settings.MIDDLEWARE
    
    # Verificar si collectstatic se ha ejecutado
    static_root_exists = os.path.exists(settings.STATIC_ROOT)
    
    # Verificar si las imágenes predeterminadas existen en STATIC_ROOT
    default_images_in_static_root = []
    if static_root_exists:
        default_images_dir = os.path.join(settings.STATIC_ROOT, 'default_images')
        if os.path.exists(default_images_dir):
            default_images_in_static_root = os.listdir(default_images_dir)
    
    # Verificar si las imágenes predeterminadas existen en STATICFILES_DIRS
    default_images_in_dirs = []
    for static_dir in settings.STATICFILES_DIRS:
        default_images_dir = os.path.join(static_dir, 'default_images')
        if os.path.exists(default_images_dir):
            default_images_in_dirs.extend(os.listdir(default_images_dir))
    
    # Construir respuesta HTML
    response = f"""
    <h1>Depuración de Imágenes</h1>
    
    <h2>Configuración</h2>
    <p>WhiteNoise habilitado: {whitenoise_enabled}</p>
    <p>STATIC_URL: {settings.STATIC_URL}</p>
    <p>STATIC_ROOT: {settings.STATIC_ROOT} (existe: {static_root_exists})</p>
    <p>STATICFILES_DIRS: {settings.STATICFILES_DIRS}</p>
    
    <h2>Imágenes en STATIC_ROOT</h2>
    <p>Directorio: {os.path.join(settings.STATIC_ROOT, 'default_images')}</p>
    <ul>
    """
    
    for img in default_images_in_static_root:
        img_url = f"{settings.STATIC_URL}default_images/{img}"
        response += f"""
        <li>
            {img} - <a href="{img_url}" target="_blank">{img_url}</a>
            <br>
            <img src="{img_url}" alt="{img}" style="max-width: 200px;">
        </li>
        """
    
    response += """
    </ul>
    
    <h2>Imágenes en STATICFILES_DIRS</h2>
    <ul>
    """
    
    for img in default_images_in_dirs:
        img_url = f"{settings.STATIC_URL}default_images/{img}"
        response += f"""
        <li>
            {img} - <a href="{img_url}" target="_blank">{img_url}</a>
            <br>
            <img src="{img_url}" alt="{img}" style="max-width: 200px;">
        </li>
        """
    
    response += """
    </ul>
    
    <h2>Prueba con vista personalizada</h2>
    <p>Estas imágenes se sirven usando la vista personalizada:</p>
    <ul>
    """
    
    # Probar algunas imágenes con la vista personalizada
    test_fields = ['image_carrousel_1', 'image_carrousel_2', 'image_carrousel_3']
    for field in test_fields:
        direct_url = f"/default-image/{field}/"
        response += f"""
        <li>
            {field} - <a href="{direct_url}" target="_blank">{direct_url}</a>
            <br>
            <img src="{direct_url}" alt="{field}" style="max-width: 200px;">
        </li>
        """
    
    response += """
    </ul>
    """
    
    return HttpResponse(response)
