from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

class Wine(models.Model):
    WINE_TYPES = (
        ('Tinto', 'Tinto'),
        ('Branco', 'Branco'),
        ('Rosé', 'Rosé'),
        ('Espumante', 'Espumante'),
        ('Fortificado', 'Fortificado'),
        ('Sobremesa', 'Sobremesa'),
    )

    # Vínculo: De quem é este vinho?
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wines')
    
    # Dados de Entrada (Obrigatórios pelo Cliente)
    name = models.CharField(max_length=255, verbose_name="Nome do Vinho")
    vintage = models.CharField(max_length=10, verbose_name="Safra") # Char para aceitar "NV"
    type = models.CharField(max_length=50, choices=WINE_TYPES, default='Tinto', verbose_name="Tipo")
    
    # Dados Enriquecidos (Preenchidos pela API/Serviço ou Manualmente)
    country = models.CharField(max_length=100, default='Outros', verbose_name="País")
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name="Região (ex: Bordeaux)")
    sub_region = models.CharField(max_length=100, blank=True, null=True, verbose_name="Sub-Região (ex: Pauillac)")
    
    # Dados Financeiros e Estoque
    # O cliente edita Quantity. O Admin edita Price.
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço (Unit)")
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(0)], verbose_name="Garrafas")
    
    # Notas e Inteligência
    score_rp = models.CharField(max_length=10, blank=True, null=True, verbose_name="RP")
    score_ws = models.CharField(max_length=10, blank=True, null=True, verbose_name="WS")
    drink_from = models.IntegerField(blank=True, null=True, verbose_name="Beber de")
    drink_to = models.IntegerField(blank=True, null=True, verbose_name="Beber até")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_value(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.name} ({self.vintage})"

    class Meta:
        ordering = ['country', 'region', 'name']
        verbose_name = "Vinho"
        verbose_name_plural = "Vinhos"

class AuditLog(models.Model):
    ACTIONS = (
        ('ADD', 'Adicionou'),
        ('REMOVE', 'Removeu'),
        ('EDIT', 'Editou'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTIONS)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)