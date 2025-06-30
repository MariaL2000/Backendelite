from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe

class CloudinaryImageWidget(forms.ClearableFileInput):
    template_name = 'admin/widgets/cloudinary_image.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        # Get all active config images
        from .models import SiteConfiguration
        active_images = SiteConfiguration.get_active_images(name)
        
        if active_images:
            previews = ''.join([
                f'<img src="{img["url"]}" title="Config {img["config_id"]}" '
                f'style="max-width:150px; margin:5px; border:2px solid #eee;">'
                for img in active_images
            ])
            context['widget']['active_previews'] = mark_safe(previews)
            
        if value and hasattr(value, 'url'):
            context['widget']['current_image'] = value.url
            
        return context