from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import (
    CommentSerializer, 
    OrderSerializer, 
    ScheduleSerializer,
    SiteConfigurationSerializer
)

from django.core.exceptions import ValidationError
import os
from .models import Comment, Client, Order, SiteConfiguration
from django.http import FileResponse, HttpResponse

from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.urls import reverse
#from .forms import ScheduleSelectionForm,ClientOrderForm
from django.conf import settings
from urllib.parse import quote

from rest_framework.permissions import AllowAny

from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from django.db.models import ImageField





#vista de contacto
@api_view(['POST'])
@permission_classes([AllowAny])
def contact_api(request):
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        order = serializer.save()
        order_details = (
            f"Name: {order.client_name}\n"
            f"Email: {order.email}\n"
            f"Phone: {order.phone}\n"
            f"Address: {order.address}\n"
            f"Project Details: {order.description}\n"
        )
        
        try:
            send_mail(
                subject="New Order Received",
                message=f"New order details:\n\n{order_details}",
                from_email="mariamarreromedrano@gmail.com",
                recipient_list=["mariamarreromedrano@gmail.com"],
                fail_silently=False,
            )
            send_mail(
                subject="Your Order Confirmation",
                message=f"Dear {order.client_name},\n\n{order_details}",
                from_email="mariamarreromedrano@gmail.com",
                recipient_list=[order.email],
                fail_silently=False,
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





#vista de reviews
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def comments_api(request):
    if request.method == "POST":
        data = request.data
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            comment = serializer.save()
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Comment created successfully'
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors,
            'message': 'Invalid data provided'
        }, status=status.HTTP_400_BAD_REQUEST)

    comments = Comment.objects.all()
    serializer = CommentSerializer(comments, many=True)
    return Response({
        'success': True,
        'data': serializer.data,
        'count': comments.count()
    })




@api_view(['GET', 'POST'])
def send_email_to_client(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == "POST":
        serializer = ScheduleSerializer(data=request.data)
        if serializer.is_valid():
            schedule = serializer.save()
            order.schedule = schedule
            order.save()
            
            contact_page_url = request.build_absolute_uri(
                reverse("orders:contact_page", args=[order.id])
            )
            
            email_data = {
                "subject": f"Order Details - {order.id}",
                "body": f"""Dear {order.client_name},
                Your order is scheduled for {schedule.time_slot} on {schedule.date}.
                The approximate price is $XXX.XX.
                You can accept or reject the offer here: {contact_page_url}"""
            }
            
            return Response({"email_data": email_data, "schedule": serializer.data}, 
                          status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({"order_id": order_id})


@api_view(['GET', 'POST'])
def confirm_page_api(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        action = request.data.get("action")

        if action == "accept":
            order.status = "accepted"
            order.save()
            subject = f"Order {order.id} Accepted"
            message = f"The customer has accepted the offer for order ID {order.id}."
        elif action == "reject":
            order.status = "rejected"
            order.save()
            subject = f"Order {order.id} Rejected"
            message = f"The customer has rejected the offer for order ID {order.id}."
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email="your_email@yourdomain.com",  # <-- Make sure this is configured
                recipient_list=["mariamarreromedrano@gmail.com"],
                fail_silently=False
            )
        except Exception as e:
            return Response({"error": f"Error sending email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"status": order.status}, status=status.HTTP_200_OK)

    # GET method
    serializer = OrderSerializer(order)
    return Response(serializer.data)











def get_active_configs():
    """Return all active configurations ordered by most recent"""
    return SiteConfiguration.objects.filter(is_active=True).order_by('-updated_at')


def serve_default_image(request, field_name):
    """Serve image from static/default_images"""
    # Check for admin uploaded image first
    config = get_active_configs()
    image_field = getattr(config, field_name, None)
    
    if image_field and bool(image_field):
        image_path = os.path.join(settings.BASE_DIR, 'static', 'default_images', os.path.basename(image_field.name))
        if os.path.exists(image_path):
            return FileResponse(open(image_path, 'rb'), content_type='image/jpeg')

    # Fallback to default
    default_path = os.path.join(settings.BASE_DIR, 'static', 'default_images', f'default_{field_name}.jpg')
    if os.path.exists(default_path):
        return FileResponse(open(default_path, 'rb'), content_type='image/jpeg')
    
    # Final fallback
    placeholder_path = os.path.join(settings.BASE_DIR, 'static', 'default_images', 'placeholder.jpg')
    if os.path.exists(placeholder_path):
        return FileResponse(open(placeholder_path, 'rb'), content_type='image/jpeg')
    
    return HttpResponse("Image not found", status=404)










def merge_images_from_configs(request, configs, field_name):
    """Get image from most recent config that has it, or default"""
    for config in configs:
        image = getattr(config, field_name, None)
        if image and bool(image):
            return get_safe_image_url(request, config, field_name)
    return get_safe_image_url(request, configs[0], field_name)  # Default fallback









def get_safe_image_url(request, config, field_name):
    """Get image URL with proper fallback logic"""
    # Check active configs first
    image_field = getattr(config, field_name, None)
    if image_field and bool(image_field):
        return request.build_absolute_uri(f'/static/default_images/{os.path.basename(image_field.name)}')

    # Try default image
    default_name = f'default_{field_name}.jpg'
    possible_paths = [
        os.path.join(settings.STATIC_ROOT, 'default_images', default_name),
        os.path.join(settings.BASE_DIR, 'static', 'default_images', default_name),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return request.build_absolute_uri(f'/static/default_images/{default_name}')

    # Final fallback
    return request.build_absolute_uri('/static/default_images/placeholder.jpg')

def get_most_recent_image(configs, field_name):
    """Get most recent non-null image from configs"""
    for config in configs:
        image = getattr(config, field_name, None)
        if image and bool(image):
            return image
    return None










@api_view(['GET'])
@permission_classes([AllowAny])
def gallery_api(request):
    try:
        configs = get_active_configs()
        if not configs:
            configs = [SiteConfiguration.objects.create()]

        gallery_data = []
        categories = [
            ('bathrooms', 'bathroom', 10),
            ('kitchens', 'kitchen', 10),
            ('fireplaces', 'fireplace', 10)
        ]

        for category_name, prefix, count in categories:
            images = []
            for i in range(1, count + 1):
                field_name = f'{prefix}_{i}'
                # Try to get image from each config
                image_url = None
                for config in configs:
                    if getattr(config, field_name, None):
                        image_url = get_safe_image_url(request, config, field_name)
                        break
                if not image_url:
                    image_url = get_safe_image_url(request, configs[0], field_name)
                images.append({'image': image_url})
            
            gallery_data.append({
                'category': category_name,
                'images': images
            })

        return Response({
            'success': True,
            'data': gallery_data
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def about_api(request):
    try:
        configs = get_active_configs()
        if not configs:
            configs = [SiteConfiguration.objects.create()]

        company_pictures = []
        team_images = []

        # Process company pictures
        for i in range(1, 6):
            field_name = f'company_picture_{i}'
            url = None
            for config in configs:
                if getattr(config, field_name, None):
                    url = get_safe_image_url(request, config, field_name)
                    break
            if not url:
                url = get_safe_image_url(request, configs[0], field_name)
            company_pictures.append(url)

        # Process team images
        team_fields = ['admin_perfil', 'admin_2_perfil', 'architect']
        for field_name in team_fields:
            url = None
            for config in configs:
                if getattr(config, field_name, None):
                    url = get_safe_image_url(request, config, field_name)
                    break
            if not url:
                url = get_safe_image_url(request, configs[0], field_name)
            team_images.append(url)

        return Response({
            'success': True,
            'data': {
                'company_pictures': company_pictures,
                'team': {
                    'admin': team_images[0],
                    'admin_2': team_images[1],
                    'architect': team_images[2]
                }
            }
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def index_api(request):
    try:
        configs = get_active_configs()
        if not configs:
            configs = [SiteConfiguration.objects.create()]

        # Get carousel images
        carousel = []
        for i in range(1, 4):
            field_name = f'image_carrousel_{i}'
            url = None
            for config in configs:
                if getattr(config, field_name, None):
                    url = get_safe_image_url(request, config, field_name)
                    break
            if not url:
                url = get_safe_image_url(request, configs[0], field_name)
            carousel.append(url)

        # Get materials images
        materials = {}
        for material in ['granite', 'quartz', 'quartzite']:
            materials[material] = []
            for i in range(1, 3):
                field_name = f'{material}_countertop_{i}'
                url = None
                for config in configs:
                    if getattr(config, field_name, None):
                        url = get_safe_image_url(request, config, field_name)
                        break
                if not url:
                    url = get_safe_image_url(request, configs[0], field_name)
                materials[material].append(url)

        # Get before/after images
        before_after = {}
        for field in ['image_before', 'image_after']:
            url = None
            for config in configs:
                if getattr(config, field, None):
                    url = get_safe_image_url(request, config, field)
                    break
            if not url:
                url = get_safe_image_url(request, configs[0], field)
            before_after[field.split('_')[1]] = url

        return Response({
            'success': True,
            'data': {
                'carousel': carousel,
                'materials': materials,
                'comparison': {'before_after': before_after},
                'colors': {
                    'primary': configs[0].primary_color,
                    'secondary': configs[0].secondary_color,
                    'buttons': configs[0].buttons_color
                }
            }
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)