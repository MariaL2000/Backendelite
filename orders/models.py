from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.safestring import mark_safe
from colorfield.fields import ColorField
import os
from django.core.files.storage import default_storage
from django.db import transaction


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
        ordering = ['-date']


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
    primary_color = ColorField(
        choices=[('', '---------')] + THEME_COLORS, 
        format="hexa",
        null=True,
        blank=True,
        default=None ,
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
    
  
    
    
    #las 3 primeras son para gallery
    bathroom_1 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    bathroom_2 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    bathroom_3 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    bathroom_4 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    bathroom_5 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    bathroom_6 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    bathroom_7 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    bathroom_8 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    bathroom_9 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    bathroom_10 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)

    kitchen_1 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    kitchen_2 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    kitchen_3 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    kitchen_4 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    kitchen_5 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    kitchen_6 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    kitchen_7 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    kitchen_8 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    kitchen_9 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    kitchen_10 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)

    fireplace_1 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    fireplace_2 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    fireplace_3 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    fireplace_4 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    fireplace_5 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    fireplace_6 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    fireplace_7 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    fireplace_8 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    fireplace_9 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    fireplace_10 = models.ImageField(upload_to='backgrounds/', blank=True, null=True)

    #para el index
    image_carrousel_1= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    image_carrousel_2= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    image_carrousel_3= models.ImageField(upload_to='backgrounds/', blank=True, null=True)

    #para el carrousel infinito
    granite_countertop_1= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    granite_countertop_2= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    quartz_countertop_1= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    quartz_countertop_2= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    quartzite_countertop_1= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    quartzite_countertop_2= models.ImageField(upload_to='backgrounds/', blank=True, null=True)

    #para la imagen before after y las scrolleables
    image_before= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    image_after= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    image_scrolleable_1= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    image_scrolleable_2= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    image_scrolleable_3= models.ImageField(upload_to='backgrounds/', blank=True, null=True)





#para el about
    admin_perfil= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    admin_2_perfil= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    architect= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    company_picture_1= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    company_picture_2= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    company_picture_3= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    company_picture_4= models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    company_picture_5= models.ImageField(upload_to='backgrounds/', blank=True, null=True)




    
    def save(self, *args, **kwargs):
        """Al guardar una nueva configuración, desactiva las anteriores"""
        if not self.pk:  # Solo para nuevas configuraciones
            SiteConfiguration.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return "Site configuration"
    
    class Meta:
        verbose_name = "Update images"
        verbose_name_plural = "Update images"
        ordering = ['-updated_at']

    


    
    
    