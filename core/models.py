from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import pandas as pd
import json
import io

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Arquivo CSV bruto
    csv_file = models.FileField(upload_to='client_csvs/', blank=True, null=True, verbose_name="Upload CSV (Lote)")
    # Onde os dados ficam salvos e prontos para uso
    wine_data = models.JSONField(default=dict, blank=True, verbose_name="Banco de Dados (JSON)")

    def save(self, *args, **kwargs):
        # Se um NOVO csv foi enviado, processamos ele
        if self.csv_file and hasattr(self.csv_file, 'file'):
            try:
                # Ler o CSV. 'header=8' pula as 8 primeiras linhas de metadados dos seus arquivos
                # Se o arquivo for diferente, o código tenta achar a linha que começa com "Vinho"
                df = pd.read_csv(self.csv_file.file, header=8) 
                
                # Se a linha 8 não for o cabeçalho, procura a linha certa
                if 'Vinho' not in df.columns and 'Pais' not in df.columns:
                     self.csv_file.file.seek(0)
                     # Lê as primeiras 20 linhas para achar onde começa
                     temp_df = pd.read_csv(self.csv_file.file, header=None, nrows=20)
                     idx = temp_df[temp_df.apply(lambda x: x.astype(str).str.contains('Vinho|Pais').any(), axis=1)].index
                     if not idx.empty:
                         self.csv_file.file.seek(0)
                         df = pd.read_csv(self.csv_file.file, header=idx[0])

                # LIMPEZA CRÍTICA: Seus CSVs têm muitas colunas vazias "Unnamed" por causa da formatação
                # Remove colunas que tenham nome "Unnamed" ou estejam vazias
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                df = df.dropna(how='all') # Remove linhas totalmente vazias
                df = df.fillna('') # Troca NaN por vazio
                
                # Transforma em estrutura para o HTML
                self.wine_data = {
                    "headers": list(df.columns),
                    "rows": df.values.tolist()
                }
                # Limpa o campo de arquivo para não reprocessar no futuro
                self.csv_file = None 
            except Exception as e:
                print(f"Erro ao processar CSV: {e}")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

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