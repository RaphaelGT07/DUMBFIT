from django.contrib import admin

from .models import Avaliacao, Cadastro, Cliente


class AvaliacaoInline(admin.TabularInline):
    model = Avaliacao
    extra = 0


@admin.register(Cadastro)
class CadastroAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "telefone", "tipo", "cliente", "criado_em")
    search_fields = ("nome", "email", "telefone")
    list_filter = ("tipo", "criado_em")


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "telefone", "status", "criado_em")
    search_fields = ("nome", "email", "telefone")
    list_filter = ("status", "criado_em")
    inlines = [AvaliacaoInline]


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("cliente", "titulo", "nota", "criado_em")
    search_fields = ("cliente__nome", "titulo", "comentario")
    list_filter = ("criado_em",)
