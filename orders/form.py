from django import forms
from .models import SiteConfiguration


   # Lista de campos de imágenes
image_fields = [
        "image_carrousel_1", "image_carrousel_2", "image_carrousel_3",
        "granite_countertop_1", "granite_countertop_2",
        "quartz_countertop_1", "quartz_countertop_2",
        "quartzite_countertop_1", "quartzite_countertop_2",
        "image_before", "image_after",
        *[f"bathroom_{i}" for i in range(1, 11)],
        *[f"kitchen_{i}" for i in range(1, 11)],
        *[f"fireplace_{i}" for i in range(1, 11)],
        "company_picture_1", "company_picture_2", "company_picture_3",
        "admin_perfil", "admin_2_perfil", "architect",
    ]

class SiteConfigurationForm(forms.ModelForm):
 

    # Añadir campos FileField para cada imagen
    for field in image_fields:
        locals()[field] = forms.FileField(required=False)

    # Incluir campos de URL y public_id dinámicamente
    for field in image_fields:
        locals()[f"{field}_url"] = forms.URLField(required=False, widget=forms.HiddenInput())
        locals()[f"{field}_public_id"] = forms.CharField(max_length=255, required=False, widget=forms.HiddenInput())

    class Meta:
        model = SiteConfiguration
        exclude = [  # Excluimos los campos calculados o de solo lectura
            f"{field}_url" for field in image_fields
        ] + [
            f"{field}_public_id" for field in image_fields
        ]

    def __init__(self, *args, **kwargs):
        # Inicializa el formulario
        super().__init__(*args, **kwargs)

        # Agregar atributos para cada campo de imagen (para la previsualización)
        for field in self.fields:
            if "image" in field:  # Solo campos que contengan "image"
                self.fields[field].widget.attrs.update({
                    'onchange': f"preview_image(this, '{field}_preview')"
                })

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
