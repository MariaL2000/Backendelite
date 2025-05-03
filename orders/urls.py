from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    
    path('api/send-email/<int:order_id>/', views.send_email_to_client, name='send_email_to_client'),
    path('api/confirm/<int:order_id>/', views.confirm_page_api, name='contact_page'),#esta vista tmb sera en react

    # React API Endpoints
    path('default-image/<str:field_name>/', views.serve_default_image, name='serve_default_image'),
    path('api/comments/', views.comments_api, name='comments_api'),
    path('api/contact/', views.contact_api, name='contact_api'),
    path('api/index/', views.index_api, name='index_api'),
    path('api/about/', views.about_api, name='about_api'),
    path('api/gallery/', views.gallery_api, name='gallery_api'),

]
