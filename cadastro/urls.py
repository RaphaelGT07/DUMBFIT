from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('perfil/', views.perfil_cliente, name='perfil_cliente'),
    path('cadastro/concluido/', views.cadastro_concluido, name='cadastro_concluido'),
    path('painel-admin/', views.admin_portal_login, name='admin_portal_login'),
    path('painel-admin/usuarios/', views.admin_user_management, name='admin_user_management'),
    path('painel-admin/usuarios/dados/', views.admin_user_management_data, name='admin_user_management_data'),
    path('painel-admin/usuarios/acao/', views.admin_user_management_action, name='admin_user_management_action'),
    path('dev-login/', views.dev_login, name='dev_login'),
    path('dev-logout/', views.dev_logout, name='dev_logout'),
    path('dev-dashboard/', views.dev_dashboard, name='dev_dashboard'),
]
