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











def get_active_config():
    """Obtiene la configuración activa o crea una nueva"""
    return SiteConfiguration.objects.filter(is_active=True).first() or SiteConfiguration.objects.create()




def serve_default_image(request, field_name):
    """Sirve directamente una imagen predeterminada"""
    # Ruta a la imagen predeterminada
    image_path = os.path.join(settings.BASE_DIR, 'static', 'default_images', f'default_{field_name}.jpg')
    
    if os.path.exists(image_path):
        return FileResponse(open(image_path, 'rb'), content_type='image/jpeg')
    
    # Si no existe, usar un placeholder
    placeholder_path = os.path.join(settings.BASE_DIR, 'static', 'default_images', 'placeholder.jpg')
    if os.path.exists(placeholder_path):
        return FileResponse(open(placeholder_path, 'rb'), content_type='image/jpeg')
    
    return HttpResponse("Imagen no encontrada", status=404)



def get_safe_image_url(request, config, field_name):
    """Obtiene URL segura de imagen con fallback a default"""
    image_field = getattr(config, field_name, None)
    
    # CASO 1: Imagen subida por el administrador
    if image_field and hasattr(image_field, 'url') and bool(image_field):
        try:
            # Verificar si el archivo existe en el disco
            if os.path.exists(image_field.path):
                # Esta URL apunta a MEDIA_URL (imágenes subidas)
                return request.build_absolute_uri(image_field.url)
        except (ValueError, FileNotFoundError, AttributeError):
            pass
    
    # CASO 2: Usar la vista personalizada que sabemos que funciona
    return request.build_absolute_uri(f"/default-image/{field_name}/")








@api_view(['GET'])
@permission_classes([AllowAny])
def about_api(request):
    try:
        config = get_active_config()
        response_data = {
            'success': True,
            'data': {
                'company_pictures': [
                    get_safe_image_url(request, config, f'company_picture_{i}')
                    for i in range(1, 6)
                ],
                'team': {
                    'admin': get_safe_image_url(request, config, 'admin_perfil'),
                    'admin_2': get_safe_image_url(request, config, 'admin_2_perfil'),
                    'architect': get_safe_image_url(request, config, 'architect')
                },
                'metadata': {
                    'last_updated': config.updated_at.isoformat()
                }
            }
        }
        response = Response(response_data)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)






    




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











@api_view(['GET'])
@permission_classes([AllowAny])
def gallery_api(request):
    try:
        config = get_active_config()
        response_data = {
            'success': True,
            'data': [
    {
        'category': 'bathrooms',
        'images': [
            {'image': get_safe_image_url(request, config, f'bathroom_{i}')}
            for i in range(1, 11)
        ]
    },
    {
        'category': 'kitchens',
        'images': [
            {'image': get_safe_image_url(request, config, f'kitchen_{i}')}
            for i in range(1, 11)
        ]
    },
    {
        'category': 'fireplaces',
        'images': [
            {'image': get_safe_image_url(request, config, f'fireplace_{i}')}
            for i in range(1,11)
        ]
    }
]
,
            'metadata': {
                'last_updated': config.updated_at.isoformat()
            }
        }
        response = Response(response_data)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def index_api(request):
    try:
        config = get_active_config()
        response_data = {
            'success': True,
            'data': {
                'carousel': [
                    get_safe_image_url(request, config, 'image_carrousel_1'),
                    get_safe_image_url(request, config, 'image_carrousel_2'),
                    get_safe_image_url(request, config, 'image_carrousel_3')
                ],
                'materials': {
                    'granite': [
                        get_safe_image_url(request, config, 'granite_countertop_1'),
                        get_safe_image_url(request, config, 'granite_countertop_2')
                    ],
                    'quartz': [
                        get_safe_image_url(request, config, 'quartz_countertop_1'),
                        get_safe_image_url(request, config, 'quartz_countertop_2')
                    ],
                    'quartzite': [
                        get_safe_image_url(request, config, 'quartzite_countertop_1'),
                        get_safe_image_url(request, config, 'quartzite_countertop_2')
                    ]
                },
                'comparison': {
                    'before_after': {
                        'before': get_safe_image_url(request, config, 'image_before'),
                        'after': get_safe_image_url(request, config, 'image_after')
                    },
                    'scrollable': [
                        get_safe_image_url(request, config, 'image_scrolleable_1'),
                        get_safe_image_url(request, config, 'image_scrolleable_2'),
                        get_safe_image_url(request, config, 'image_scrolleable_3')
                    ]
                },
                'colors': {
                    # Pass the color values directly - they'll be None if not set
                    # React will handle the default colors on the frontend
                    'primary': config.primary_color,
                    'secondary': config.secondary_color,
                    'buttons': config.buttons_color
                },
                'metadata': {
                    'last_updated': config.updated_at.isoformat(),
                    'has_custom_images': any(
                        bool(getattr(config, f.name))
                        for f in config._meta.get_fields()
                        if isinstance(f, ImageField) and hasattr(config, f.name)
                    )
                }
            }
        }
        response = Response(response_data)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)






