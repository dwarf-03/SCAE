from django.contrib import admin
from .models import Cliente, DocumentoCliente

# Documentos del cliente como tabla inline
class DocumentoClienteInline(admin.TabularInline):
    model = DocumentoCliente
    extra = 1

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'numero_documento', 'telefono', 
                    'ciudad', 'verificado', 'tiene_deuda', 'deuda_total']
    list_filter = ['verificado', 'tiene_deuda', 'tipo_documento', 'ciudad']
    search_fields = ['numero_documento', 'usuario__first_name', 
                    'usuario__last_name', 'usuario__email']
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']
    inlines = [DocumentoClienteInline]

@admin.register(DocumentoCliente)
class DocumentoClienteAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'tipo', 'descripcion', 'fecha_subida']
    list_filter = ['tipo']