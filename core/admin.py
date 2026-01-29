from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import ClientProfile

# Define como o perfil aparece dentro da página do Usuário no Admin
class ClientProfileInline(admin.StackedInline):
    model = ClientProfile
    can_delete = False
    verbose_name_plural = 'Dados do Cliente (Excel/Dashboard)'

# Reconfigura o Admin de Usuário padrão para incluir seus dados
class UserAdmin(BaseUserAdmin):
    inlines = (ClientProfileInline,)
    list_display = ('username', 'first_name', 'get_plan', 'is_staff')

    def get_plan(self, instance):
        return instance.profile.plan_type
    get_plan.short_description = 'Plano'

# Registra tudo
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
