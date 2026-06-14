from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'get_full_name', 'rol', 'activo']
    list_filter = ['rol', 'activo']
    search_fields = ['username', 'email', 'documento']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'telefono', 'documento', 'direccion', 'foto', 'activo')
        }),
    )