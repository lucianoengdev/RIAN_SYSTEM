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
    excel_file = models.FileField(upload_to='client_excels/', blank=True, null=True, verbose_name="Upload da Planilha (.xlsx)")
    data_snapshot = models.JSONField(default=dict, blank=True, verbose_name="Dados do Dashboard (JSON)")
    
    def save(self, *args, **kwargs):
        # Se houver um arquivo excel, processamos ele antes de salvar
        if self.excel_file:
            try:
                # Ler o Excel. 
                # header=8 indica que o cabeçalho está na linha 9 (baseado nos seus CSVs que começam com metadados)
                # Se quiser a planilha INTEIRA crua, mude para header=None
                df = pd.read_excel(self.excel_file.file, header=8) 
                
                # Limpeza: Substituir valores vazios (NaN) por string vazia ""
                df = df.fillna('')
                
                # Converter para formato JSON de tabela
                # Orient='split' separa colunas e dados, facilitando o loop no HTML
                data = df.to_dict(orient='split')
                
                # Salvamos no campo JSON
                self.data_snapshot = data
            except Exception as e:
                print(f"Erro ao processar Excel: {e}")
                # Opcional: Salvar o erro no JSON para debug
                
        super().save(*args, **kwargs)

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