from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ClientProfile

@login_required
def dashboard_view(request):
    try:
        profile = request.user.clientprofile
    except:
        profile = ClientProfile.objects.create(user=request.user)

    data = profile.wine_data
    context = {
        'headers': data.get('headers', []),
        'rows': data.get('rows', []),
    }
    return render(request, 'core/universal_dashboard.html', context)

@login_required
def add_single_item(request):
    if request.method == 'POST':
        profile = request.user.clientprofile
        current_data = profile.wine_data
        
        headers = current_data.get('headers', [])
        new_row = []
        
        # Pega os dados do formulário na ordem correta das colunas
        for header in headers:
            value = request.POST.get(header, '')
            new_row.append(value)
        
        # Adiciona a nova linha
        if 'rows' in current_data:
            current_data['rows'].insert(0, new_row) # Adiciona no topo
        else:
            current_data['rows'] = [new_row]
            
        profile.wine_data = current_data
        profile.save()
        
    return redirect('dashboard')