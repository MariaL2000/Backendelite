from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import (
    CommentSerializer, 
    OrderSerializer, 
    ScheduleSerializer,
    
)

from .models import Comment, Client, Order, SiteConfiguration
from django.shortcuts import  get_object_or_404
from django.core.mail import send_mail
import random
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes



def get_active_configs():
    """Return all active configurations ordered by newest first"""
    return SiteConfiguration.objects.filter(is_active=True).order_by('-updated_at')

def get_safe_image_url(request, config, field_name):
    """Get Cloudinary URL"""
    image_field = getattr(config, field_name, None)
    if image_field and hasattr(image_field, 'url'):
        return image_field.url
    return None

def merge_images_from_configs(request, configs, field_name):
    """Get most recent image from active configs"""
    for config in configs:
        url = get_safe_image_url(request, config, field_name)
        if url:
            return url
    return None

def get_most_recent_image(configs, field_name):
    """Get most recent non-null Cloudinary image"""
    for config in configs:
        image = getattr(config, field_name, None)
        if image and hasattr(image, 'public_id'):
            return image
    return None






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
            
            
            email_data = {
                "subject": f"Order Details - {order.id}",
                "body": f"""Dear {order.client_name},
                Your order is scheduled for {schedule.time_slot} on {schedule.date}.
                The approximate price is $XXX.XX.
                You can accept or reject the offer sending us an email.
                Thank you for choosing"""
            }
            
            return Response({"email_data": email_data, "schedule": serializer.data}, 
                          status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({"order_id": order_id})













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
def index_api(request):
    try:
        configs = get_active_configs()
        if not configs:
            configs = [SiteConfiguration.objects.create()]

        # Get main carousel images (1-3)
        main_carousel = []
        for i in range(1, 4):
            field_name = f'image_carrousel_{i}'
            url = None
            for config in configs:
                if getattr(config, field_name, None):
                    url = get_safe_image_url(request, config, field_name)
                    break
            if not url:
                url = get_safe_image_url(request, configs[0], field_name)
            main_carousel.append(url)
            
        # Get second carousel images (4-6)
        second_carousel = []
        for i in range(4, 7):
            field_name = f'image_carrousel_{i}'
            url = None
            for config in configs:
                if getattr(config, field_name, None):
                    url = get_safe_image_url(request, config, field_name)
                    break
            if not url:
                url = get_safe_image_url(request, configs[0], field_name)
            second_carousel.append(url)

        # Get material showcase images
        materials = {}
        for material in ['quartz', 'granite', 'marble', 'quartzite']:
            field_name = f'image_{material}'
            url = None
            for config in configs:
                if getattr(config, field_name, None):
                    url = get_safe_image_url(request, config, field_name)
                    break
            if not url:
                url = get_safe_image_url(request, configs[0], field_name)
            materials[material] = url

        # Get random gallery images
        galleries = {}
        for gallery_type in ['bathroom', 'kitchen', 'fireplace']:
            available_images = []
            for i in range(1, 11):
                field_name = f'{gallery_type}_{i}'
                url = None
                for config in configs:
                    if getattr(config, field_name, None):
                        url = get_safe_image_url(request, config, field_name)
                        if url:
                            available_images.append(url)
                        break
            
            # Select 3 random images if available
            galleries[gallery_type] = random.sample(
                available_images, 
                min(3, len(available_images))
            ) if available_images else []

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
                'main_carousel': main_carousel,
                'second_carousel': second_carousel,
                'materials': materials,
                'galleries': galleries,
                'comparison': {'before_after': before_after},
                'colors': {
                    'primary': configs[0].primary_color,
                    'secondary': configs[0].secondary_color
                    
                }
            }
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)