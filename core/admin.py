from django.contrib import admin
from .models import Wine, AuditLog

@admin.register(Wine)
class WineAdmin(admin.ModelAdmin):
    # O que aparece na lista de vinhos do Admin
    list_display = ('name', 'vintage', 'country', 'type', 'quantity', 'price', 'user')
    # Filtros laterais para você achar rápido
    list_filter = ('country', 'type', 'user')
    # Barra de pesquisa (busca por nome ou região)
    search_fields = ('name', 'region')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    # Log de segurança para você ver quem fez o que
    list_display = ('timestamp', 'user', 'action', 'details')
    list_filter = ('action', 'user')
    # O log é apenas leitura (ninguém pode alterar o passado)
    readonly_fields = ('timestamp', 'user', 'action', 'details')

    def has_add_permission(self, request):
        return False