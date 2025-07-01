from django.db import models
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from colorfield.fields import ColorField

import cloudinary
import cloudinary.uploader
from cloudinary.models import CloudinaryField


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

    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Configuración actualmente activa")
    
    bathroom_1 = CloudinaryField('Bathroom 1', blank=True, null=True)
    bathroom_2 = CloudinaryField('Bathroom 2', blank=True, null=True)
    bathroom_3 = CloudinaryField('Bathroom 3', blank=True, null=True)
    bathroom_4 = CloudinaryField('Bathroom 4', blank=True, null=True)
    bathroom_5 = CloudinaryField('Bathroom 5', blank=True, null=True)
    bathroom_6 = CloudinaryField('Bathroom 6', blank=True, null=True)
    bathroom_7 = CloudinaryField('Bathroom 7', blank=True, null=True)
    bathroom_8 = CloudinaryField('Bathroom 8', blank=True, null=True)
    bathroom_9 = CloudinaryField('Bathroom 9', blank=True, null=True)
    bathroom_10 = CloudinaryField('Bathroom 10', blank=True, null=True)

    # Kitchen Gallery
    kitchen_1 = CloudinaryField('Kitchen 1', blank=True, null=True)
    kitchen_2 = CloudinaryField('Kitchen 2', blank=True, null=True)
    kitchen_3 = CloudinaryField('Kitchen 3', blank=True, null=True)
    kitchen_4 = CloudinaryField('Kitchen 4', blank=True, null=True)
    kitchen_5 = CloudinaryField('Kitchen 5', blank=True, null=True)
    kitchen_6 = CloudinaryField('Kitchen 6', blank=True, null=True)
    kitchen_7 = CloudinaryField('Kitchen 7', blank=True, null=True)
    kitchen_8 = CloudinaryField('Kitchen 8', blank=True, null=True)
    kitchen_9 = CloudinaryField('Kitchen 9', blank=True, null=True)
    kitchen_10 = CloudinaryField('Kitchen 10', blank=True, null=True)
    # Fireplace Gallery
    fireplace_1 = CloudinaryField('Fireplace 1', blank=True, null=True)
    fireplace_2 = CloudinaryField('Fireplace 2', blank=True, null=True)
    fireplace_3 = CloudinaryField('Fireplace 3', blank=True, null=True)
    fireplace_4 = CloudinaryField('Fireplace 4', blank=True, null=True)
    fireplace_5 = CloudinaryField('Fireplace 5', blank=True, null=True)
    fireplace_6 = CloudinaryField('Fireplace 6', blank=True, null=True)
    fireplace_7 = CloudinaryField('Fireplace 7', blank=True, null=True)
    fireplace_8 = CloudinaryField('Fireplace 8', blank=True, null=True)
    fireplace_9 = CloudinaryField('Fireplace 9', blank=True, null=True)
    fireplace_10 = CloudinaryField('Fireplace 10', blank=True, null=True)

    # Main Carousel
    image_carrousel_1 = CloudinaryField('Carousel 1', blank=True, null=True)
    image_carrousel_2 = CloudinaryField('Carousel 2', blank=True, null=True)
    image_carrousel_3 = CloudinaryField('Carousel 3', blank=True, null=True)

    # Material Showcase
    granite_countertop_1 = CloudinaryField('Granite 1', blank=True, null=True)
    granite_countertop_2 = CloudinaryField('Granite 2', blank=True, null=True)
    quartz_countertop_1 = CloudinaryField('Quartz 1', blank=True, null=True)
    quartz_countertop_2 = CloudinaryField('Quartz 2', blank=True, null=True)
    quartzite_countertop_1 = CloudinaryField('Quartzite 1', blank=True, null=True)
    quartzite_countertop_2 = CloudinaryField('Quartzite 2', blank=True, null=True)

    # Before/After
    image_before = CloudinaryField('Before', blank=True, null=True)
    image_after = CloudinaryField('After', blank=True, null=True)

    # Team
    admin_perfil = CloudinaryField('Admin Profile', blank=True, null=True)
    admin_2_perfil = CloudinaryField('Admin 2 Profile', blank=True, null=True)
    architect = CloudinaryField('Architect Profile', blank=True, null=True)
    company_picture_1 = CloudinaryField('Company 1', blank=True, null=True)
    company_picture_2 = CloudinaryField('Company 2', blank=True, null=True)
    company_picture_3 = CloudinaryField('Company 3', blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_images = {}
        for field in self._meta.fields:
            if isinstance(field, CloudinaryField):
                self._initial_images[field.name] = getattr(self, field.name)

    @classmethod
    def get_active_images(cls, field_name):
        """Get all images from active configurations"""
        active_configs = cls.objects.filter(is_active=True).order_by('-updated_at')
        images = []
        seen_urls = set()  # Track unique images
        
        for config in active_configs:
            image = getattr(config, field_name, None)
            if image and hasattr(image, 'url'):
                # Only add if URL not already seen
                if image.url not in seen_urls:
                    images.append({
                        'url': image.url,
                        'config_id': config.id,
                        'updated_at': config.updated_at
                    })
                    seen_urls.add(image.url)
        return images

    @classmethod
    def get_most_recent_active_image(cls, field_name):
        """Get most recent image for a field from active configs"""
        return cls.objects.filter(
            is_active=True,
            **{f"{field_name}__isnull": False}
        ).order_by('-updated_at').values_list(field_name, flat=True).first()

    

    @classmethod
    def copy_previous_config(cls):
        """Copy most recent configuration with images"""
        latest = cls.objects.order_by('-updated_at').first()
        if not latest:
            return cls()
        
        new_config = cls()
        # Copy all fields including images
        for field in cls._meta.fields:
            if not field.primary_key:
                setattr(new_config, field.name, getattr(latest, field.name))
        
        new_config._state.adding = True
        new_config.pk = None
        return new_config

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            return

        old_instance = self.__class__.objects.get(pk=self.pk)
        
        # Handle image changes
        for field in self._meta.fields:
            if isinstance(field, CloudinaryField):
                old_value = getattr(old_instance, field.name)
                new_value = getattr(self, field.name)
                
                if new_value and new_value != old_value:
                    # Delete old image
                    if old_value and hasattr(old_value, 'public_id'):
                        try:
                            cloudinary.uploader.destroy(old_value.public_id)
                        except Exception as e:
                            print(f"Error deleting old image {field.name}: {e}")
                            # Set new image
                    setattr(self, field.name, new_value)
                elif not new_value and old_value:
                    # Keep old image if no new one provided
                    setattr(self, field.name, old_value)

        super().save(*args, **kwargs)
        
        # Update initial states
        for field in self._meta.fields:
            if isinstance(field, CloudinaryField):
                self._initial_images[field.name] = getattr(self, field.name)

    def delete(self, *args, **kwargs):
        # Cleanup all Cloudinary images
        for field in self._meta.fields:
            if isinstance(field, CloudinaryField):
                image = getattr(self, field.name)
                if image and hasattr(image, 'public_id'):
                    try:
                        cloudinary.uploader.destroy(image.public_id)
                    except Exception as e:
                        print(f"Error deleting image {field.name}: {e}")
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configurations"
        ordering = ['-updated_at']



    
    
    