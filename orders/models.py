from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.safestring import mark_safe
from colorfield.fields import ColorField
from django.core.files.storage import FileSystemStorage
import os
from django.utils import timezone
from cloudinary.models import CloudinaryField
import cloudinary.uploader

class StaticStorage(FileSystemStorage):
    def __init__(self):
        super().__init__(
            location=os.path.join(settings.BASE_DIR, 'static', 'default_images'),
            base_url='/static/default_images/'
        )
        
    def url(self, name):
        """Return URL for both uploaded and default images"""
        if not name:
            name = f'default_{self.field_name}.jpg'
        return f'{self.base_url}{name}'

THEME_COLORS = [
    ('#007BFFFF', 'Blue'),
    ('#1D097FFF', 'Blue2'),
    ('#28A745FF', 'Green'), 
    ('#DC3545FF', 'Red'),
    ('#895188FF', 'Cyan'),
    ('#6C757DFF', 'Gray'),
    ('#CBC3FFFF', 'Gray2'),
    ('#651A89FF', 'Dark'),
    ('#FFFFFFFF', 'White'),
    ('#000000FF', 'Black'),
    ('#CF1DBDFF', 'Violet'),
    ('#9027E9FF', 'Violet2'),
]

class Client(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=255) 
    
    def __str__(self):
        return f'{self.name} ({self.email})'
    
    class Meta:
        verbose_name = ('Client')
        verbose_name_plural = ('Clients')
        ordering = ['name']

class Comment(models.Model):
    name = models.CharField(max_length=100)
    opinion = models.TextField()
    rating = models.IntegerField()
    sug = models.TextField()

    def __str__(self):
        return self.name

    def clean(self):
        """Método de validación para rating."""
        if not (0 <= self.rating <= 5):
            raise ValidationError("Rating must be between 0 and 5.")

    def save(self, *args, **kwargs):
        self.clean()  # Aseguramos que la validación se ejecute al guardar
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = ('Website Reviews')
        verbose_name_plural = ('Website Reviews')
    



class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    client_name = models.CharField(max_length=255)
    description = models.TextField(help_text='Describe your needs')
    phone = models.CharField(max_length=100)
    email = models.EmailField()
    date = models.DateTimeField(auto_now_add=True)
    address = models.TextField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    schedule = models.ForeignKey('Schedule', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Order #{self.id} - {self.client_name}'

    def safe_description(self):
        return mark_safe(self.description)

    class Meta:
        verbose_name = ('List of orders')
        verbose_name_plural = ('List of orders')
        ordering = ['date']


    def save(self, *args, **kwargs):
        # Si la orden tiene un schedule asignado, marcamos el schedule como no disponible
        if self.schedule and self.schedule.is_available:
            self.schedule.is_available = False
            self.schedule.save()
        super().save(*args, **kwargs)



class Schedule(models.Model):
    time_slot = models.CharField(max_length=50)
    date = models.DateField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.date} - {self.time_slot}"

    def clean(self):
        if Schedule.objects.filter(date=self.date, time_slot=self.time_slot).exists():
            raise ValidationError("This time slot is already booked.")

    class Meta:
        verbose_name = ('Calendar')
        verbose_name_plural = ('Calendar')
        ordering = ['date', 'time_slot']
        unique_together = ['date', 'time_slot']



THEME_COLORS = [
    ('#FF5733', 'Red'),
    ('#33FF57', 'Green'),
    # Agrega otros colores aquí
]

class SiteConfiguration(models.Model):
    # Colores principales y secundarios
    primary_color = ColorField(
        choices=[('', '---------')] + THEME_COLORS, 
        format="hexa",
        null=True,
        blank=True,
        default=None,
        help_text=('Main brand color used throughout the site') 
    )
    secondary_color = ColorField(
        choices=[('', '---------')] + THEME_COLORS,  
        format="hexa",
        null=True,
        blank=True,
        default=None,
        help_text=('Secondary color for accents and highlights')
    )
    buttons_color = ColorField(
        choices=[('', '---------')] + THEME_COLORS,  
        format="hexa",
        null=True,
        blank=True,
        default=None,
        help_text=('Color for all action buttons')
    )

    # Otros campos de configuración
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Configuración actualmente activa")
    
    # Campos de imágenes para diferentes secciones (bathroom, kitchen, etc.)
    bathroom_1_url = models.URLField(blank=True, null=True)
    bathroom_1_public_id = models.CharField(max_length=255, blank=True, null=True)
    bathroom_2_url = models.URLField(blank=True, null=True)
    bathroom_2_public_id = models.CharField(max_length=255, blank=True, null=True)
    bathroom_3_url = models.URLField(blank=True, null=True)
    bathroom_3_public_id = models.CharField(max_length=255, blank=True, null=True)
    bathroom_4_url = models.URLField(blank=True, null=True)
    bathroom_4_public_id = models.CharField(max_length=255, blank=True, null=True)
    bathroom_5_url = models.URLField(blank=True, null=True)
    bathroom_5_public_id = models.CharField(max_length=255, blank=True, null=True)
    bathroom_6_url = models.URLField(blank=True, null=True)
    bathroom_6_public_id = models.CharField(max_length=255, blank=True, null=True)
    bathroom_7_url = models.URLField(blank=True, null=True)
    bathroom_7_public_id = models.CharField(max_length=255, blank=True, null=True)
    bathroom_8_url = models.URLField(blank=True, null=True)
    bathroom_8_public_id = models.CharField(max_length=255, blank=True, null=True)
    bathroom_9_url = models.URLField(blank=True, null=True)
    bathroom_9_public_id = models.CharField(max_length=255, blank=True, null=True)
    bathroom_10_url = models.URLField(blank=True, null=True)
    bathroom_10_public_id = models.CharField(max_length=255, blank=True, null=True)

    kitchen_1_url = models.URLField(blank=True, null=True)
    kitchen_1_public_id = models.CharField(max_length=255, blank=True, null=True)
    kitchen_2_url = models.URLField(blank=True, null=True)
    kitchen_2_public_id = models.CharField(max_length=255, blank=True, null=True)
    kitchen_3_url = models.URLField(blank=True, null=True)
    kitchen_3_public_id = models.CharField(max_length=255, blank=True, null=True)
    kitchen_4_url = models.URLField(blank=True, null=True)
    kitchen_4_public_id = models.CharField(max_length=255, blank=True, null=True)
    kitchen_5_url = models.URLField(blank=True, null=True)
    kitchen_5_public_id = models.CharField(max_length=255, blank=True, null=True)
    kitchen_6_url = models.URLField(blank=True, null=True)
    kitchen_6_public_id = models.CharField(max_length=255, blank=True, null=True)
    kitchen_7_url = models.URLField(blank=True, null=True)
    kitchen_7_public_id = models.CharField(max_length=255, blank=True, null=True)
    kitchen_8_url = models.URLField(blank=True, null=True)
    kitchen_8_public_id = models.CharField(max_length=255, blank=True, null=True)
    kitchen_9_url = models.URLField(blank=True, null=True)
    kitchen_9_public_id = models.CharField(max_length=255, blank=True, null=True)
    kitchen_10_url = models.URLField(blank=True, null=True)
    kitchen_10_public_id = models.CharField(max_length=255, blank=True, null=True)

    fireplace_1_url = models.URLField(blank=True, null=True)
    fireplace_1_public_id = models.CharField(max_length=255, blank=True, null=True)
    fireplace_2_url = models.URLField(blank=True, null=True)
    fireplace_2_public_id = models.CharField(max_length=255, blank=True, null=True)
    fireplace_3_url = models.URLField(blank=True, null=True)
    fireplace_3_public_id = models.CharField(max_length=255, blank=True, null=True)
    fireplace_4_url = models.URLField(blank=True, null=True)
    fireplace_4_public_id = models.CharField(max_length=255, blank=True, null=True)
    fireplace_5_url = models.URLField(blank=True, null=True)
    fireplace_5_public_id = models.CharField(max_length=255, blank=True, null=True)
    fireplace_6_url = models.URLField(blank=True, null=True)
    fireplace_6_public_id = models.CharField(max_length=255, blank=True, null=True)
    fireplace_7_url = models.URLField(blank=True, null=True)
    fireplace_7_public_id = models.CharField(max_length=255, blank=True, null=True)
    fireplace_8_url = models.URLField(blank=True, null=True)
    fireplace_8_public_id = models.CharField(max_length=255, blank=True, null=True)
    fireplace_9_url = models.URLField(blank=True, null=True)
    fireplace_9_public_id = models.CharField(max_length=255, blank=True, null=True)
    fireplace_10_url = models.URLField(blank=True, null=True)
    fireplace_10_public_id = models.CharField(max_length=255, blank=True, null=True)

    image_carrousel_1_url = models.URLField(blank=True, null=True)
    image_carrousel_1_public_id = models.CharField(max_length=255, blank=True, null=True)
    image_carrousel_2_url = models.URLField(blank=True, null=True)
    image_carrousel_2_public_id = models.CharField(max_length=255, blank=True, null=True)
    image_carrousel_3_url = models.URLField(blank=True, null=True)
    image_carrousel_3_public_id = models.CharField(max_length=255, blank=True, null=True)

    granite_countertop_1_url = models.URLField(blank=True, null=True)
    granite_countertop_1_public_id = models.CharField(max_length=255, blank=True, null=True)
    granite_countertop_2_url = models.URLField(blank=True, null=True)
    granite_countertop_2_public_id = models.CharField(max_length=255, blank=True, null=True)
    quartz_countertop_1_url = models.URLField(blank=True, null=True)
    quartz_countertop_1_public_id = models.CharField(max_length=255, blank=True, null=True)
    quartz_countertop_2_url = models.URLField(blank=True, null=True)
    quartz_countertop_2_public_id = models.CharField(max_length=255, blank=True, null=True)
    quartzite_countertop_1_url = models.URLField(blank=True, null=True)
    quartzite_countertop_1_public_id = models.CharField(max_length=255, blank=True, null=True)
    quartzite_countertop_2_url = models.URLField(blank=True, null=True)
    quartzite_countertop_2_public_id = models.CharField(max_length=255, blank=True, null=True)

    image_before_url = models.URLField(blank=True, null=True)
    image_before_public_id = models.CharField(max_length=255, blank=True, null=True)
    image_after_url = models.URLField(blank=True, null=True)
    image_after_public_id = models.CharField(max_length=255, blank=True, null=True)

    admin_perfil_url = models.URLField(blank=True, null=True)
    admin_perfil_public_id = models.CharField(max_length=255, blank=True, null=True)
    admin_2_perfil_url = models.URLField(blank=True, null=True)
    admin_2_perfil_public_id = models.CharField(max_length=255, blank=True, null=True)
    architect_url = models.URLField(blank=True, null=True)
    architect_public_id = models.CharField(max_length=255, blank=True, null=True)
    company_picture_1_url = models.URLField(blank=True, null=True)
    company_picture_1_public_id = models.CharField(max_length=255, blank=True, null=True)
    company_picture_2_url = models.URLField(blank=True, null=True)
    company_picture_2_public_id = models.CharField(max_length=255, blank=True, null=True)
    company_picture_3_url = models.URLField(blank=True, null=True)
    company_picture_3_public_id = models.CharField(max_length=255, blank=True, null=True)

    # Método para obtener las imágenes más recientes
    @classmethod
    def get_latest_images(cls):
        """Get most recent non-null images from active configurations"""
        latest_config = {}
        active_configs = cls.objects.filter(is_active=True).order_by('-updated_at')
        
        for field in cls._meta.fields:
            if isinstance(field, models.ImageField):
                field_name = field.name
                # Get first non-null value for each image field
                image = (
                    active_configs
                    .exclude(**{field_name: ''})
                    .exclude(**{field_name: None})
                    .values_list(field_name, flat=True)
                    .first()
                )
                if image:
                    latest_config[field_name] = image
        
        return latest_config

    # Método para guardar las imágenes en Cloudinary
    def save(self, *args, **kwargs):
        image_fields = [
        # Bathroom
        'bathroom_1_url', 'bathroom_2_url', 'bathroom_3_url', 'bathroom_4_url', 'bathroom_5_url',
        'bathroom_6_url', 'bathroom_7_url', 'bathroom_8_url', 'bathroom_9_url', 'bathroom_10_url',

        # Kitchen
        'kitchen_1_url', 'kitchen_2_url', 'kitchen_3_url', 'kitchen_4_url', 'kitchen_5_url',
        'kitchen_6_url', 'kitchen_7_url', 'kitchen_8_url', 'kitchen_9_url', 'kitchen_10_url',

        # Fireplace
        'fireplace_1_url', 'fireplace_2_url', 'fireplace_3_url', 'fireplace_4_url', 'fireplace_5_url',
        'fireplace_6_url', 'fireplace_7_url', 'fireplace_8_url', 'fireplace_9_url', 'fireplace_10_url',

        # Carrousel
        'image_carrousel_1_url', 'image_carrousel_2_url', 'image_carrousel_3_url',

        # Countertops
        'granite_countertop_1_url', 'granite_countertop_2_url',
        'quartz_countertop_1_url', 'quartz_countertop_2_url',
        'quartzite_countertop_1_url', 'quartzite_countertop_2_url',

        # Before & After
        'image_before_url', 'image_after_url',

        # Admin & staff
        'admin_perfil_url', 'admin_2_perfil_url', 'architect_url',

        # Company pictures
        'company_picture_1_url', 'company_picture_2_url', 'company_picture_3_url',
    ]

        
        for field in image_fields:
         url_field = f"{field}_url"
         public_id_field = f"{field}_public_id"
        
         current_public_id = getattr(self, public_id_field, None)
         new_image = getattr(self, field)  # Aquí new_image debería ser un archivo (FileField) o ruta local
        
         # Si tienes una imagen nueva para subir (puede ser un archivo o path)
         if new_image:
            try:
                # Si había una imagen subida antes, elimínala de Cloudinary
                if current_public_id:
                    cloudinary.uploader.destroy(current_public_id)
                
                # Sube la nueva imagen a Cloudinary
                result = cloudinary.uploader.upload(new_image)
                
                # Actualiza los campos URL y public_id con la nueva info
                setattr(self, url_field, result.get('secure_url'))
                setattr(self, public_id_field, result.get('public_id'))
                
                # Si es archivo local, opcionalmente lo borras
                if hasattr(new_image, 'delete'):
                    new_image.delete(save=False)
            
            except Exception as e:
                print(f"Error gestionando imagen {field}: {e}")

        # No olvides actualizar updated_at si lo usas
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Update images"
        verbose_name_plural = "Update images"
        ordering = ['-updated_at']




    
    
    