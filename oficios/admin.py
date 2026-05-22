from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Perfil

# ============================================
# Configuración del modelo Perfil
# ============================================
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'telefono', 'ubicacion', 'disponible', 'get_oficio_o_empresa')
    list_filter = ('tipo', 'disponible', 'rubro')
    search_fields = ('usuario__username', 'usuario__email', 'telefono', 'ubicacion', 'nombre_empresa', 'oficios')
    list_editable = ('disponible',)
    readonly_fields = ('usuario',)
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('usuario', 'tipo')
        }),
        ('Datos de Contacto', {
            'fields': ('telefono', 'ubicacion')
        }),
        ('Datos Profesionales (para Trabajador)', {
            'fields': ('oficios', 'descripcion_personal', 'disponible'),
            'classes': ('collapse',)
        }),
        ('Datos de Empresa (para Empleador)', {
            'fields': ('nombre_empresa', 'rubro'),
            'classes': ('collapse',)
        }),
    )
    
    def get_oficio_o_empresa(self, obj):
        if obj.tipo == 'trabajador':
            return obj.oficios or 'No especificado'
        else:
            return obj.nombre_empresa or 'No especificado'
    get_oficio_o_empresa.short_description = 'Oficio / Empresa'


# ============================================
# Extender el admin de Usuario para ver perfiles relacionados
# ============================================
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_tipo', 'get_telefono')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'perfil__tipo')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'perfil__telefono')
    inlines = [PerfilInline]
    
    def get_tipo(self, obj):
        if hasattr(obj, 'perfil'):
            return obj.perfil.tipo
        return 'No definido'
    get_tipo.short_description = 'Tipo'
    
    def get_telefono(self, obj):
        if hasattr(obj, 'perfil'):
            return obj.perfil.telefono
        return 'No registrado'
    get_telefono.short_description = 'Teléfono'


# Re-registrar User con el admin personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ============================================
# Configuración del sitio admin
# ============================================
admin.site.site_header = 'Administración CHAMBA'
admin.site.site_title = 'CHAMBA Admin'
admin.site.index_title = 'Panel de control - CHAMBA'