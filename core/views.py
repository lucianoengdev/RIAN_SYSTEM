from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Sum
from .models import Wine, AuditLog
from .services import fetch_wine_data
import csv
import io

# Função auxiliar para verificar se é admin
def is_admin(user):
    return user.is_staff

@login_required
def dashboard(request):
    # Busca SÓ os vinhos do usuário logado
    wines = Wine.objects.filter(user=request.user)
    
    # Agrupa países para criar as ABAS
    countries = wines.values_list('country', flat=True).distinct()
    
    # Cálculo do Caixa (Valor total da adega)
    total_value = wines.aggregate(Sum('price'))['price__sum'] or 0
    
    # Se for ADMIN, busca logs recentes e a lista de usuários para o dropdown
    logs = None
    all_users_list = []
    
    if request.user.is_staff:
        logs = AuditLog.objects.all().order_by('-timestamp')[:10]
        # Pega todos os usuários que NÃO são staff (ou seja, clientes)
        all_users_list = User.objects.filter(is_staff=False)

    context = {
        'wines': wines,
        'countries': countries,
        'total_value': total_value,
        'is_admin': request.user.is_staff,
        'logs': logs,
        'all_users': all_users_list,  # <--- A vírgula aqui e na linha anterior são essenciais
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
        Wine.objects.create(
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

def clean_qty(value):
    try:
        if not value:
            return 1
        # Remove espaços
        value = str(value).strip()
        # Converte '1.0' -> 1.0 -> 1
        return int(float(value))
    except (ValueError, TypeError):
        # Se der erro (ex: veio texto), assume 1
        return 1

@login_required
@user_passes_test(is_admin)
def import_legacy(request):
    if request.method == 'POST':
        target_user_id = request.POST.get('target_user')
        csv_file = request.FILES.get('csv_file')
        
        if not target_user_id or not csv_file:
            return redirect('dashboard')
            
        target_user = get_object_or_404(User, id=target_user_id)
        
        try:
            file_data = csv_file.read().decode('utf-8-sig').splitlines()
            reader = csv.DictReader(file_data)
            
            count = 0
            for row in reader:
                row = {k.strip(): v for k, v in row.items() if k}
                
                name_key = next((k for k in row.keys() if 'vinho' in k.lower()), None)
                vintage_key = next((k for k in row.keys() if 'safra' in k.lower()), None)
                qty_key = next((k for k in row.keys() if 'estoque' in k.lower()), None)
                
                if name_key and row[name_key]:
                    # CORREÇÃO AQUI: Usamos a função clean_qty
                    raw_qty = row.get(qty_key, '1')
                    final_qty = clean_qty(raw_qty)

                    Wine.objects.create(
                        user=target_user,
                        name=row[name_key],
                        vintage=row.get(vintage_key, 'NV'),
                        quantity=final_qty, # Agora é um inteiro garantido
                        country="Importado (Editar)", 
                        price=0
                    )
                    count += 1
            
            AuditLog.objects.create(
                user=request.user,
                action='IMPORT',
                details=f"Importou {count} vinhos para o cliente {target_user.username}"
            )
            print(f"Importados {count} vinhos para {target_user.username}")
            
        except Exception as e:
            print(f"Erro na importação: {e}")

    return redirect('dashboard')