from django.utils import timezone
from django.contrib import admin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, path
from django.utils.html import format_html
from django.http import HttpResponse
from urllib.parse import quote
from .serializers import SiteConfigurationSerializer, OrderSerializer, CommentSerializer, ScheduleSerializer
from .models import Order, Comment, Schedule, SiteConfiguration,Schedule
from django.contrib import admin
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from django.db.models import ImageField
from django.core.files.storage import default_storage


 
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
    ordering = ["-date"]

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

            contact_page_url = request.build_absolute_uri(
                reverse('orders:contact_page', args=[order.id])
            )
            body = f"""Dear {order.client_name},

Your order is scheduled for {schedule.time_slot} on {schedule.date}.
The approximate price is $XXX.XX.

You can view and respond to this order here: {contact_page_url}

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
    serializer_class = SiteConfigurationSerializer
    list_display = ("primary_color", "secondary_color", "buttons_color", "updated_at", "is_active")
    list_filter = ("updated_at", "is_active")
    ordering = ("-updated_at",)
    save_on_top = True
    actions = ["activate_config"]
    
    # Campos editables directamente en el listado
    list_editable = ("is_active",)
    
    # Añadir botón de eliminación personalizado
    def get_list_display_links(self, request, list_display):
        return ["id"]  # Hacer clickable solo el ID
    
    fieldsets = (
        ("Color Settings", {
            "classes": ("collapse",),
            "fields": (
                ("primary_color", "secondary_color", "buttons_color"),
            )
        }),
        ("Main Carousel", {
            "fields": (
                "image_carrousel_1",
                "image_carrousel_2",
                "image_carrousel_3",
            )
        }),
        
        ("Material Showcase", {
            "classes": ("collapse",),
            "fields": (
                ("granite_countertop_1", "granite_countertop_2"),
                ("quartz_countertop_1", "quartz_countertop_2"),
                ("quartzite_countertop_1", "quartzite_countertop_2"),
            )
        }),
        
        ("Comparison Section", {
            "fields": (
                "image_before",
                "image_after",
            )
        }),
        
        ("Scrollable Images", {
            "fields": (
                "image_scrolleable_1",
                "image_scrolleable_2",
                "image_scrolleable_3",
            )
        }),
        
        ("Bathroom Gallery", {
            "classes": ("collapse",),
            "fields": [f"bathroom_{i}" for i in range(1, 11)],
        }),
        
        ("Kitchen Gallery", {
            "classes": ("collapse",),
            "fields": [f"kitchen_{i}" for i in range(1, 11)],
        }),
        
        ("Fireplace Gallery", {
            "classes": ("collapse",),
            "fields": [f"fireplace_{i}" for i in range(1, 11)],
        }),
        
        
        
        ("About Us Page", {
            "classes": ("collapse",),
            "fields": (
                ("company_picture_1", "company_picture_2", "company_picture_3"),
                ("company_picture_4", "company_picture_5"),
                ("admin_perfil", "admin_2_perfil", "architect"),
            )
        }),
    )

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    def save_model(self, request, obj, form, change):
        """Guarda solo campos modificados y actualiza timestamps"""
        if change:
            original = SiteConfiguration.objects.get(pk=obj.pk)
            for field_name in form.changed_data:
                field = obj._meta.get_field(field_name)
                if isinstance(field, ImageField):
                    old_file = getattr(original, field_name)
                    if old_file:
                        old_file.delete(save=False)
        
        obj.updated_at = timezone.now()
        super().save_model(request, obj, form, change)

    def activate_config(self, request, queryset):
        """Activa una configuración específica"""
        config = queryset.first()
        SiteConfiguration.objects.filter(is_active=True).update(is_active=False)
        config.is_active = True
        config.save()
        self.message_user(request, f"Configuración {config.id} activada")
    activate_config.short_description = "Activate configuration"

    def delete_model(self, request, obj):
        """Elimina una configuración y sus archivos asociados"""
        # Eliminar archivos físicos
        for field in obj._meta.get_fields():
            if isinstance(field, ImageField):
                if file := getattr(obj, field.name):
                    if default_storage.exists(file.name):
                        default_storage.delete(file.name)
        # Eliminar registro de la BD
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Eliminación masiva para acciones de admin"""
        for obj in queryset:
            self.delete_model(request, obj)
        self.message_user(request, f"{queryset.count()} configuraciones eliminadas")