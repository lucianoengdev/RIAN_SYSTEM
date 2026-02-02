from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Wine, AuditLog
from .services import fetch_wine_data
import csv
import io

@login_required
def dashboard(request):
    # Busca SÓ os vinhos do usuário logado
    wines = Wine.objects.filter(user=request.user)
    
    # Agrupa países para criar as ABAS
    countries = wines.values_list('country', flat=True).distinct()
    
    # Cálculo do Caixa (Valor total da adega)
    total_value = wines.aggregate(Sum('price'))['price__sum'] or 0
    
    # Se for ADMIN, busca logs recentes
    logs = None
    if request.user.is_staff:
        logs = AuditLog.objects.all().order_by('-timestamp')[:10]

    context = {
        'wines': wines,
        'countries': countries,
        'total_value': total_value,
        'is_admin': request.user.is_staff,
        'logs': logs
    }
    return render(request, 'core/user_dashboard.html', context)

@login_required
def add_wine(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        vintage = request.POST.get('vintage')
        qty = int(request.POST.get('quantity', 1))
        
        # 1. Chama a API para pegar os detalhes
        data = fetch_wine_data(name, vintage)
        
        # 2. Salva no Banco
        wine = Wine.objects.create(
            user=request.user,
            name=name,
            vintage=vintage,
            quantity=qty,
            country=data['country'],
            type=data['type'],
            price=data['price'],
            score_rp=data['score_rp'],
            score_ws=data['score_ws'],
            drink_window_start=data['drink_window_start'],
            drink_window_end=data['drink_window_end']
        )
        
        # 3. Gera Log para o Moderador
        AuditLog.objects.create(
            user=request.user,
            action='ADD',
            details=f"Adicionou {qty}x {name} {vintage} (Valor un: R$ {data['price']})"
        )
        
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def delete_wine(request, wine_id):
    # Garante que só deleta se o vinho for SEU
    wine = get_object_or_404(Wine, id=wine_id, user=request.user)
    
    AuditLog.objects.create(
        user=request.user,
        action='REMOVE',
        details=f"Removeu {wine.name} (Perda de valor: R$ {wine.price})"
    )
    
    wine.delete()
    return redirect('dashboard')

@login_required
def import_legacy(request):
    """
    Função especial para importar os CSVs antigos.
    Só roda se for POST e tiver arquivo.
    """
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        
        # Pula as linhas iniciais "sujas" (Tentativa simplificada)
        start_reading = False
        count = 0
        
        for row in reader:
            # Lógica para achar onde começa a tabela real no seu CSV
            if not start_reading:
                if row and 'Vinho' in str(row[0]): # Se achar a coluna "Vinho"
                    start_reading = True
                continue
            
            # Se a linha estiver vazia, ignora
            if not row or not row[0]:
                continue
                
            # Mapeamento do CSV antigo para o novo DB
            # Assumindo ordem: Nome, safra, RP, WS, Beber, Estoque (ajuste conforme coluna)
            try:
                Wine.objects.create(
                    user=request.user,
                    name=row[0], # Coluna 0 do CSV
                    vintage=row[5] if len(row) > 5 else 'NV', # Coluna Safra
                    country="Importado", # Depois você ajusta ou a API atualiza
                    quantity=1
                )
                count += 1
            except Exception as e:
                print(f"Erro na linha: {e}")

        AuditLog.objects.create(
            user=request.user,
            action='IMPORT',
            details=f"Importou {count} vinhos via CSV legado."
        )
        
    return redirect('dashboard')