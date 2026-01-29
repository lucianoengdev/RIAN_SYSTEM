from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ClientProfile

@login_required
def dashboard_view(request):
    user = request.user
    
    # Lógica 1: Se for o ADMIN (Moderador)
    if user.is_staff or user.is_superuser:
        # Pega todos os clientes para mostrar um resumão
        all_clients = ClientProfile.objects.all()
        
        # Aqui você fará a "soma geral" que pediu
        total_clients = all_clients.count()
        
        context = {
            'is_admin': True,
            'clients': all_clients,
            'total_clients': total_clients
        }
        return render(request, 'core/admin_dashboard.html', context)
    
    # Lógica 2: Se for CLIENTE comum
    else:
        # Acessa apenas os dados DELE
        profile = user.profile
        data = profile.data_snapshot # Aqui estarão os dados do Excel
        
        context = {
            'is_admin': False,
            'data': data,
            'client_name': user.first_name
        }
        return render(request, 'core/user_dashboard.html', context)