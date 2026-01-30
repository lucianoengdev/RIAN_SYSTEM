from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

class ClientProfile(models.Model):
    # Relacionamento 1 para 1 com o sistema de login padrão do Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Configurações do Cliente
    is_active_client = models.BooleanField(default=True, verbose_name="Cliente Ativo")
    plan_type = models.CharField(max_length=50, default='Standard', verbose_name="Plano Contratado")
    
    # O "Coração" do sistema: Aqui guardaremos os dados do Excel
    # Exemplo de estrutura: {"Faturamento": "R$ 50k", "Status": "Em dia"}
    data_snapshot = models.JSONField(default=dict, blank=True, verbose_name="Dados do Dashboard (JSON)")

    def __str__(self):
        return f"Perfil de {self.user.username}"

# Cria automaticamente um perfil quando você cria um User no admin
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Se o usuário acabou de ser criado, cria o perfil.
    Se o usuário já existe mas não tem perfil (caso do seu erro), cria o perfil agora.
    Se já tem perfil, apenas salva.
    """
    try:
        instance.profile.save()
    except ObjectDoesNotExist:
        ClientProfile.objects.create(user=instance)