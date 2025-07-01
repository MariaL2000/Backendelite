from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe

class CloudinaryImageWidget(forms.ClearableFileInput):
    template_name = 'admin/widgets/cloudinary_image.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        # Get active config images
        from .models import SiteConfiguration
        active_images = SiteConfiguration.get_active_images(name)
        
        # Get current image if exists
        if value and hasattr(value, 'url'):
            context['widget'].update({
                'is_image': True,
                'current_image': value.url,
                'name': name,
            })

        # Add most recent active image if available
        if active_images:
            most_recent = active_images[0]  # Get only most recent
            context['widget'].update({
                'has_active': True,
                'active_preview': format_html(
                    '<div class="active-image">'
                    '<p>Current active image:</p>'
                    '<img src="{}" title="Config {}" '
                    'style="max-width:200px; margin:5px; border:2px solid #eee;">'
                    '</div>',
                    most_recent['url'],
                    most_recent['config_id']
                )
            })
            
        return context