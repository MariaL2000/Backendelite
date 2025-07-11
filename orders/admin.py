from django.contrib import admin
from django.shortcuts import  render, get_object_or_404
from django.urls import reverse, path
from django.utils.html import format_html
from django.http import HttpResponse
from urllib.parse import quote
from .serializers import  OrderSerializer, CommentSerializer, ScheduleSerializer
from .models import Order, Comment, Schedule, SiteConfiguration,Schedule
from django.contrib import admin
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from .models import SiteConfiguration
import cloudinary
from cloudinary.models import CloudinaryField
from django.utils.html import format_html
from .widgets import CloudinaryImageWidget


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    serializer_class = ScheduleSerializer
    list_display = ('time_slot', 'date', 'is_available')
    search_fields = ('time_slot', 'date')
    list_display_links = ('date',)
    list_editable = ('is_available',)
    list_filter = ('is_available', 'date')
    


    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    @admin.action(description="Mark as Available")
    def mark_as_available(self, request, queryset):
        queryset.update(is_available=True)
        self.message_user(request, f"{queryset.count()} schedules marked as available")

    @admin.action(description="Mark as Unavailable")  
    def mark_as_unavailable(self, request, queryset):
        queryset.update(is_available=False)
        self.message_user(request, f"{queryset.count()} schedules marked as unavailable")

    actions = [mark_as_available, mark_as_unavailable]


    




@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    
    serializer_class = OrderSerializer
    list_display = ("id", "get_client_name", "description", "phone", "email", 
                   "status", "address", "date", "schedule", "send_email_link")
    list_filter = ("status", "date", "schedule")
    search_fields = ("client_name", "email", "phone")
    actions = ["generate_pdf", "mark_as_pending", "mark_as_in_progress", 
              "mark_as_completed", "mark_as_cancelled"]
    ordering = ["date"]

    list_select_related = ('schedule',)
    



    def send_email_view(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        

        if order.schedule:
            available_schedules = Schedule.objects.filter(id=order.schedule.id)
        else:
            available_schedules = Schedule.objects.filter(is_available=True)

        if request.method == 'POST':
           schedule_id = request.POST.get('schedule')
           if schedule_id:
            schedule = Schedule.objects.get(id=schedule_id)
            order.schedule = schedule
            order.save()

            
            body = f"""Dear {order.client_name},

Your order is scheduled for {schedule.time_slot} on {schedule.date}.
The approximate price is $XXX.XX.

You can view and respond to this order sending us and email.

Best regards,
Elite Countertops"""

            encoded_subject = quote(f"Order Details - {order.id}")
            encoded_body = quote(body)
            mailto_url = f"mailto:{order.email}?subject={encoded_subject}&body={encoded_body}"

            script = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <meta http-equiv="refresh" content="0;url={mailto_url}">
                </head>
                <body>
                    <script>
                        (function() {{
                            // Try to open email client
                            window.location.href = "{mailto_url}";
                            
                            // Fallback for mobile
                            setTimeout(function() {{
                                if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {{
                                    window.location.href = "{mailto_url}";
                                }}
                                // Redirect back to admin
                                setTimeout(function() {{
                                    window.location.href = "{reverse('admin:orders_order_changelist')}";
                                }}, 1000);
                            }}, 100);
                        }})();
                    </script>
                    <p style="text-align: center; margin-top: 20px;">
                        If your email client doesn't open automatically, 
                        <a href="{mailto_url}">click here</a>
                    </p>
                </body>
                </html>
            """
            return HttpResponse(script)

        context = {
        'opts': self.model._meta,
        'order': order,
        'available_schedules': available_schedules,
        'title': 'Confirm Schedule and Send Email' if order.schedule else 'Select Schedule and Send Email',}
        
        return render(request, 'admin/orders/send_email.html', context)



    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return True 

    def has_change_permission(self, request, obj=None):
        return False  # Evita que se editen horarios desde el formulario de Orders

    def has_add_permission(self, request):
        return True  # Asegúrate de que esto retorne True si quieres permitir agregar órdenes


    def get_client_name(self, obj):
        return obj.client_name

    get_client_name.short_description = "Client"



    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'api/send-email/<int:order_id>/',
                self.admin_site.admin_view(self.send_email_view),
                name='order_send_email',
            ),
            
        ]
        return custom_urls + urls


    def send_email_link(self, obj):
        url = reverse('admin:order_send_email', args=[obj.id])
        return format_html('<a class="button" href="{}">Send Email</a>', url)
    send_email_link.short_description = "Email"


    @admin.action(description="Delete selected orders")
    def delete_selected(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} orders were successfully deleted.")


    @admin.action(description="Generate PDF")
    def generate_pdf(self, request, queryset):
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="orders.pdf"'
    
    # Create the PDF document
        doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Container for the 'Flowable' objects
        elements = []
    
    # Styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        title_style.alignment = 1  # Center alignment
    
    # Add title
        title = Paragraph("Lista de Pedidos", title_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
    
    # Table data
        data = [['ID', 'Cliente', 'Descripción', 'Teléfono', 'Email', 'Estado', 'Fecha']]
    
        for order in queryset:
            data.append([
            str(order.id),
            str(order.client_name),
            str(order.description),
            str(order.phone),
            str(order.email),
            str(order.status),
            order.date.strftime("%Y-%m-%d")
        ])
    
    # Create table
        table = Table(data, repeatRows=1)
    
    # Table style
        table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f2f2f2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
    
    # Add table to elements
        elements.append(table)
    
    # Build PDF
        doc.build(elements)
        return response


    
    @admin.action(description="Mark selected orders as Pending")
    def mark_as_pending(self, request, queryset):
        queryset.update(status="pending")
        self.message_user(request, f"{queryset.count()} orders marked as pending")


    @admin.action(description="Mark selected orders as In Progress")
    def mark_as_in_progress(self, request, queryset):
        queryset.update(status="in_progress")
        self.message_user(request, f"{queryset.count()} orders marked as in progress")

    @admin.action(description="Mark selected orders as Completed")
    def mark_as_completed(self, request, queryset):
        queryset.update(status="completed")
        self.message_user(request, f"{queryset.count()} orders marked as completed")


    @admin.action(description="Mark selected orders as Cancelled")
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status="cancelled")
        self.message_user(request, f"{queryset.count()} orders marked as cancelled")



    def get_actions(self, request):
        actions = super().get_actions(request)
        if actions:
            for name, (func, name, desc) in actions.items():
                func.attrs = {
                    'background': {
                        'delete_selected': '#dc3545',
                        'generate_pdf': '#17a2b8',
                        'mark_as_pending': '#ffc107',
                        'mark_as_in_progress': '#007bff',
                        'mark_as_completed': '#28a745',
                        'mark_as_cancelled': '#dc3545'
                    }.get(name, '#6c757d')
                }
        return actions


    actions = [
        delete_selected,
        generate_pdf,
        mark_as_pending,
        mark_as_in_progress,
        mark_as_completed,
        mark_as_cancelled
    ]

    

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    serializer_class = CommentSerializer
    list_display = ("name", "opinion", "rating", "sug")
    search_fields = ("name", "opinion")
    list_filter = ("rating",)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)





@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ('id', 'updated_at', 'is_active')
    list_filter = ('updated_at', 'is_active')
    ordering = ('-updated_at',)
    save_on_top = True
    actions = ['activate_config']
    list_editable = ('is_active',)




    fieldsets = (
        ('⚙️ Configuration', {
            'description': 'Configuration status and timestamps',
            'fields': ('is_active',),
            'classes': ('wide',),
        }),
        ('🎨 Theme Colors', {
            'description': 'Customize the main color scheme of your website',
            'fields': (
                ('primary_color', 'secondary_color'),
                'buttons_color'
            ),
            'classes': ('wide', 'extrapretty'),
        }),
        ('🎠 Main Carousel', {
            'description': 'Manage the main slideshow images (Recommended size: 1920x1080px)',
            'fields': ('image_carrousel_1', 'image_carrousel_2', 'image_carrousel_3'),
            'classes': ('wide',),
        }),
        ('🎪 Second Carousel', {
            'description': 'Manage secondary slideshow images',
            'fields': ('image_carrousel_4', 'image_carrousel_5', 'image_carrousel_6'),
            'classes': ('wide',),
        }),
        ('💎 Materials Showcase', {
            'description': 'Display your premium countertop materials',
            'fields': (
                'image_quartz', 'image_granite',
                'image_marble', 'image_quartzite'
            ),
            'classes': ('wide',),
        }),
        ('✨ Before & After', {
            'description': 'Showcase transformation projects',
            'fields': ('image_before', 'image_after'),
            'classes': ('wide',),
        }),
        ('🚽 Bathroom Gallery', {
            'description': 'Bathroom renovation projects (3 random images will be shown)',
            'fields': tuple(f'bathroom_{i}' for i in range(1, 11)),
            'classes': ('wide',),
        }),
        ('🍳 Kitchen Gallery', {
            'description': 'Kitchen renovation projects (3 random images will be shown)',
             'fields': tuple(f'kitchen_{i}' for i in range(1, 11)),
            'classes': ('wide',),
        }),
        ('🔥 Fireplace Gallery', {
            'description': 'Fireplace renovation projects (3 random images will be shown)',
            'fields': tuple(f'fireplace_{i}' for i in range(1, 11)),
            'classes': ('wide',),
        }),
    )
    

    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, CloudinaryField):
            kwargs['widget'] = CloudinaryImageWidget
        return super().formfield_for_dbfield(db_field, **kwargs)

    def delete_model(self, request, obj):
        try:
            for field in obj._meta.fields:
                if isinstance(field, CloudinaryField):
                    image = getattr(obj, field.name)
                    if image and hasattr(image, 'public_id'):
                        cloudinary.uploader.destroy(image.public_id)
            super().delete_model(request, obj)
            self.message_user(request, 'Configuration deleted successfully')
        except Exception as e:
            self.message_user(request, f'Error deleting: {str(e)}', level='ERROR')
    
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)

    def activate_config(self, request, queryset):
        config = queryset.first()
        config.is_active = True
        config.save()
        self.message_user(request, f"Configuration {config.id} activated")

    activate_config.short_description = "Activate configuration"

    class Media:
        css = {
            'all': ('admin/css/cloudinary.css',)
        }