from django.db import models
from django.contrib.auth.models import User

# Este modelo estende o usuário padrão para adicionar informações do seu negócio
class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Monetização e Controle
    is_active_client = models.BooleanField(default=True, verbose_name="Cliente Ativo")
    plan_type = models.CharField(max_length=50, default='Standard', verbose_name="Plano")
    
    # Campo Mágico: Aqui entraremos com os dados do Excel depois.
    # Por enquanto, ele substituirá o array 'data' do seu código React.
    # Ex: {"saldo": "R$ 5000", "status": "Em dia", "meta": "Atingida"}
    data_snapshot = models.JSONField(default=dict, blank=True, verbose_name="Dados do Dashboard")

    # Campos futuros para controle de arquivos
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

# Sinal para criar o perfil automaticamente quando um usuário é criado
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        ClientProfile.objects.create(user=instance)
