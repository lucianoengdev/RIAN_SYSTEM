from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Wine(models.Model):
    # Vínculo com o Dono da Adega
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wines')
    
    # Dados de Entrada (Obrigatórios)
    name = models.CharField(max_length=255, verbose_name="Nome do Vinho")
    vintage = models.CharField(max_length=4, verbose_name="Safra") # Char pois pode ser 'NV' (Non-Vintage)
    
    # Dados Enriquecidos (Preenchidos pela API ou Importação)
    country = models.CharField(max_length=100, default='Outros', verbose_name="País")
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name="Região")
    type = models.CharField(max_length=50, default='Tinto', verbose_name="Tipo (Tinto/Branco/etc)")
    
    # Dados Financeiros e de Gestão
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Estimado")
    quantity = models.IntegerField(default=1, verbose_name="Estoque")
    
    # Notas e Consumo
    score_rp = models.CharField(max_length=10, blank=True, null=True, verbose_name="Nota Robert Parker")
    score_ws = models.CharField(max_length=10, blank=True, null=True, verbose_name="Nota Wine Spectator")
    drink_window_start = models.IntegerField(blank=True, null=True, verbose_name="Beber de")
    drink_window_end = models.IntegerField(blank=True, null=True, verbose_name="Beber até")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.vintage})"

    class Meta:
        ordering = ['country', 'name']

# Log para o Moderador (Histórico)
class AuditLog(models.Model):
    ACTIONS = (
        ('ADD', 'Adicionou Vinho'),
        ('REMOVE', 'Removeu Vinho'),
        ('CONSUME', 'Bebeu/Baixou'),
        ('IMPORT', 'Importação em Massa'),
    )
    
    moderator_only = models.BooleanField(default=True) # Apenas admin vê
    user = models.ForeignKey(User, on_delete=models.CASCADE) # De quem é a adega
    action = models.CharField(max_length=20, choices=ACTIONS)
    details = models.TextField() # Ex: "Adicionou Latour 1990 (R$ 5000)"
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"