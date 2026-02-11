from django.urls import path
from . import views

urlpatterns = [
    # Painéis Principais
    path('', views.dashboard, name='dashboard'),
    path('clientes/', views.client_list, name='client_list'), 
    path('cliente/<int:user_id>/', views.dashboard, name='client_dashboard'), 

    # Navegação Hierárquica (Suporta user_id opcional para Admin)
    path('adega/<str:country_name>/', views.region_list, name='region_list'),
    path('adega/<str:country_name>/u/<int:user_id>/', views.region_list, name='client_region_list'),
    
    path('adega/<str:country_name>/<str:region_name>/', views.wine_list, name='wine_list'),
    path('adega/<str:country_name>/<str:region_name>/u/<int:user_id>/', views.wine_list, name='client_wine_list'),

    # Ações de Estoque
    path('vinho/<int:wine_id>/estoque/', views.update_stock, name='update_stock'),
    path('vinho/<int:wine_id>/excluir/', views.delete_wine, name='delete_wine'),

    # Adicionar
    path('adicionar/passo-1/', views.add_wine_step1, name='add_wine_step1'),
    path('adicionar/passo-2/', views.add_wine_step2, name='add_wine_step2'),
]