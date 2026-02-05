from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Sum
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Wine, AuditLog
from .services import search_wine_api

ROWS_PER_PAGE = 45

def is_admin(user):
    return user.is_staff

@login_required
def client_list(request):
    """
    PAINEL ADMIN: Lista todos os clientes para você 'entrar' na adega deles.
    """
    if not request.user.is_staff:
        return redirect('dashboard')
        
    clients = User.objects.filter(is_staff=False)
    return render(request, 'core/client_list.html', {'clients': clients})

@login_required
def dashboard(request, user_id=None):
    """
    Visão Geral. 
    Se user_id for passado E quem pede for admin, mostra a adega daquele user.
    Caso contrário, mostra a adega do próprio usuário logado.
    """
    # 1. Define de quem é a adega que vamos olhar
    target_user = request.user
    if user_id and request.user.is_staff:
        target_user = get_object_or_404(User, id=user_id)
    
    # 2. Busca os vinhos desse usuário alvo
    wines = Wine.objects.filter(user=target_user)
    
    # 3. Monta os dados
    countries = wines.values_list('country', flat=True).distinct().order_by('country')
    
    summary = {}
    total_general_qty = 0
    total_general_val = 0

    for tipo in ['Tinto', 'Branco', 'Espumante', 'Rosé', 'Fortificado', 'Sobremesa']:
        qs = wines.filter(type=tipo).values('country').annotate(total_qty=Sum('quantity'), total_val=Sum('price'))
        
        # Calcula totais parciais para adicionar ao dicionário
        tipo_qty = 0
        tipo_val = 0
        cleaned_qs = []
        
        for item in qs:
            qty = item['total_qty'] or 0
            val = item['total_val'] or 0
            tipo_qty += qty
            tipo_val += val
            cleaned_qs.append(item)
            
        if cleaned_qs: # Só mostra se tiver vinho desse tipo
            summary[tipo] = {
                'items': cleaned_qs,
                'total_qty': tipo_qty,
                'total_val': tipo_val
            }
            total_general_qty += tipo_qty
            total_general_val += tipo_val

    context = {
        'countries': countries,
        'summary': summary,
        'is_admin': request.user.is_staff,
        'target_user': target_user, # Para saber de quem estamos vendo a adega
        'total_general_qty': total_general_qty,
        'total_general_val': total_general_val
    }
    return render(request, 'core/dashboard_countries.html', context)

@login_required
def region_list(request, country_name, user_id=None):
    # Lógica de 'Impersonation' (Ver como outro usuário)
    target_user = request.user
    if user_id and request.user.is_staff:
        target_user = get_object_or_404(User, id=user_id)

    wines = Wine.objects.filter(user=target_user, country=country_name)
    regions = wines.values_list('region', flat=True).distinct().order_by('region')
    
    return render(request, 'core/region_list.html', {
        'country': country_name,
        'regions': regions,
        'target_user': target_user
    })

@login_required
def wine_list(request, country_name, region_name, user_id=None):
    # Lógica de 'Impersonation'
    target_user = request.user
    if user_id and request.user.is_staff:
        target_user = get_object_or_404(User, id=user_id)

    # Filtros
    queryset = Wine.objects.filter(
        user=target_user, 
        country=country_name, 
        region=region_name
    )
    
    # Busca
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(name__icontains=query)

    # Paginação
    paginator = Paginator(queryset, ROWS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Linhas Fantasmas
    current_count = len(page_obj.object_list)
    empty_rows = range(ROWS_PER_PAGE - current_count)

    return render(request, 'core/wine_grid.html', {
        'country': country_name,
        'region': region_name,
        'page_obj': page_obj,
        'empty_rows': empty_rows,
        'is_admin': request.user.is_staff,
        'target_user': target_user
    })

# --- AÇÕES DE EDIÇÃO ---

@login_required
@require_POST
def update_stock(request, wine_id):
    """Aumenta ou diminui estoque via botões + e -"""
    wine = get_object_or_404(Wine, id=wine_id)
    
    # Segurança: Só pode mexer se for dono OU admin
    if wine.user != request.user and not request.user.is_staff:
        return redirect('dashboard')
    
    action = request.POST.get('action') # 'increase' ou 'decrease'
    
    if action == 'increase':
        wine.quantity += 1
    elif action == 'decrease' and wine.quantity > 0:
        wine.quantity -= 1
    
    wine.save()
    
    # Redireciona de volta para a mesma página (preserva filtros)
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def delete_wine(request, wine_id):
    wine = get_object_or_404(Wine, id=wine_id)
    
    # Segurança
    if wine.user != request.user and not request.user.is_staff:
        return redirect('dashboard')
        
    if request.method == 'POST':
        wine.delete()
        # Tenta voltar para a lista, se não der vai pro dashboard
        return redirect('dashboard')
        
    return render(request, 'core/confirm_delete.html', {'wine': wine})

# --- ADICIONAR (Mantido igual, mas garantindo que salva para o user certo) ---
# Nota: Por enquanto, Adicionar Vinho sempre adiciona para quem está logado.
# Se o Admin quiser adicionar para o cliente, precisaremos ajustar isso depois.
# Vou manter o código anterior do Add aqui, apenas certifique-se que ele está no arquivo.

@login_required
def add_wine_step1(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        vintage = request.POST.get('vintage')
        w_type = request.POST.get('type')
        candidates = search_wine_api(name, vintage)
        request.session['wine_candidates'] = candidates
        request.session['temp_form_data'] = {'name': name, 'vintage': vintage, 'type': w_type}
        return redirect('add_wine_step2')
    return render(request, 'core/add_wine_step1.html')

@login_required
def add_wine_step2(request):
    candidates = request.session.get('wine_candidates', [])
    form_data = request.session.get('temp_form_data', {})
    if request.method == 'POST':
        selected_index = request.POST.get('selected_index')
        
        # Define para quem o vinho será criado
        # Por padrão é para o usuário logado. 
        # (Futuramente, se o Admin estiver criando para outro, ajustaremos aqui)
        target_user = request.user 

        if selected_index == 'manual':
            # Criação Manual (apenas dados básicos)
            Wine.objects.create(
                user=target_user,
                name=form_data['name'],
                vintage=form_data['vintage'],
                type=form_data['type'],
                country='Outros', # Default
                quantity=int(request.POST.get('quantity', 1))
            )
        else:
            # Criação via API (dados enriquecidos)
            idx = int(selected_index)
            chosen = candidates[idx]
            
            Wine.objects.create(
                user=target_user,
                name=chosen['name'],
                vintage=chosen['vintage'],
                type=form_data['type'], # O tipo o usuário definiu no passo 1
                country=chosen['country'],
                region=chosen['region'],
                price=chosen['price'],
                score_rp=chosen['score_rp'],
                score_ws=chosen['score_ws'],
                drink_from=chosen['drink_from'],
                drink_to=chosen['drink_to'],
                quantity=int(request.POST.get('quantity', 1))
            )
            
        return redirect('dashboard')

    return render(request, 'core/add_wine_step2.html', {
        'candidates': candidates,
        'form_data': form_data
    })