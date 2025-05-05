from rest_framework import serializers
from .models import Comment, Order, Schedule, SiteConfiguration, Client
import re
from django.core.validators import validate_email

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'address']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['name', 'opinion', 'rating', 'sug']

    def validate_rating(self, value):
        if not (0 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 0 and 5.")
        return value

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['time_slot', 'date', 'is_available']

    def validate(self, data):
        if Schedule.objects.filter(date=data['date'], time_slot=data['time_slot']).exists():
            raise serializers.ValidationError("This time slot is already booked.")
        return data

class OrderSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ['client_name', 'description', 'phone', 'email', 'address', 'status', 'schedule']

    def validate_client_name(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('Client name must be at least 8 characters long.')
        return value

    def validate_email(self, value):
        try:
            validate_email(value)
            return value
        except:
            raise serializers.ValidationError('Enter a valid email address.')

    def validate_phone(self, value):
        if not re.match(r'^\d+$', value):
            raise serializers.ValidationError('Phone number must contain only digits.')
        return value

    def validate_description(self, value):
        if not value:
            raise serializers.ValidationError('Description is required.')
        return value

class SiteConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteConfiguration
        fields = '__all__'

    def validate(self, data):
        existing_config = SiteConfiguration.objects.first()
        if existing_config and self.instance is None:
            raise serializers.ValidationError("Only one configuration instance is allowed.")
        return data
    
    def to_internal_value(self, data):
        """
        Asegura que los campos vacíos se guarden como NULL en la base de datos.
        """
        for field in ['primary_color', 'secondary_color', 'buttons_color']:
            if field in data and data[field] == '':
                data[field] = None  # Convierte campos vacíos a NULL
        return super().to_internal_value(data)

    def to_representation(self, instance):
        """
        Devuelve los valores exactos de la base de datos (incluso si son NULL).
        El frontend manejará los NULL como colores por defecto.
        """
        return super().to_representation(instance)