from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('perfil/', views.perfil_cliente, name='perfil_cliente'),
    path('cadastro/concluido/', views.cadastro_concluido, name='cadastro_concluido'),
    path('dev-login/', views.dev_login, name='dev_login'),
    path('dev-logout/', views.dev_logout, name='dev_logout'),
    path('dev-dashboard/', views.dev_dashboard, name='dev_dashboard'),
]
