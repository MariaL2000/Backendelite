from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    
    path('api/send-email/<int:order_id>/', views.send_email_to_client, name='send_email_to_client'),
   

    # React API Endpoints
    
    path('api/comments/', views.comments_api, name='comments_api'),
    path('api/contact/', views.contact_api, name='contact_api'),
    path('api/index/', views.index_api, name='index_api'),
    path('api/gallery/', views.gallery_api, name='gallery_api'),

]
