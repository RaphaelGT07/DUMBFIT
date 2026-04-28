from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_exempt

from .models import Avaliacao, Cadastro, Cliente


def criar_avaliacoes_iniciais(cliente):
    if cliente.avaliacoes.exists():
        return

    Avaliacao.objects.bulk_create(
        [
            Avaliacao(
                cliente=cliente,
                titulo="Avaliacao fisica",
                nota="5.0",
                comentario="Perfil cadastrado com sucesso e pronto para iniciar a jornada de treino.",
            ),
            Avaliacao(
                cliente=cliente,
                titulo="Frequencia recomendada",
                nota="4.8",
                comentario="Plano inicial sugerido para rotina semanal com acompanhamento da equipe DumbFit.",
            ),
            Avaliacao(
                cliente=cliente,
                titulo="Atendimento",
                nota="5.0",
                comentario="Cadastro identificado e liberado para suporte personalizado da academia.",
            ),
        ]
    )


@csrf_exempt
def index(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        tipo = request.POST.get("tipo", "cadastro").strip() or "cadastro"
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        if not nome or not email or not telefone:
            if is_ajax:
                return JsonResponse(
                    {"ok": False, "message": "Preencha nome, e-mail e telefone para continuar."},
                    status=400,
                )
            query = urlencode({"status": "error"})
            return redirect(f"/?{query}")

        cliente, _ = Cliente.objects.update_or_create(
            email=email,
            defaults={
                "nome": nome,
                "telefone": telefone,
                "status": "ativo" if tipo == "login" else "analise",
            },
        )
        criar_avaliacoes_iniciais(cliente)

        registro = Cadastro.objects.create(
            cliente=cliente,
            nome=nome,
            email=email,
            telefone=telefone,
            tipo=tipo,
        )
        success_message = (
            f"Login enviado com sucesso, {nome}. Em breve entraremos em contato."
            if tipo == "login"
            else f"Cadastro realizado com sucesso, {nome}. Seus dados foram salvos."
        )

        if is_ajax:
            payload = {"ok": True, "message": success_message, "tipo": tipo, "nome": nome}
            if tipo == "login":
                query = urlencode({"id": cliente.id})
                payload["redirect_url"] = f"/perfil/?{query}"
            if tipo == "cadastro":
                query = urlencode({"id": cliente.id})
                payload["redirect_url"] = f"/cadastro/concluido/?{query}"
            return JsonResponse(payload)

        if tipo == "login":
            query = urlencode({"id": cliente.id})
            return redirect(f"/perfil/?{query}")

        if tipo == "cadastro":
            query = urlencode({"id": cliente.id})
            return redirect(f"/cadastro/concluido/?{query}")

        query = urlencode({"status": "success", "tipo": tipo, "nome": nome})
        return redirect(f"/?{query}")

    return render(request, "index.html")


def cadastro_concluido(request):
    cliente_id = request.GET.get("id", "").strip()
    if not cliente_id:
        raise Http404("Cadastro nao encontrado.")

    cliente = get_object_or_404(Cliente, id=cliente_id)
    primeiro_nome = cliente.nome.split()[0] if cliente.nome else "Aluno"
    context = {
        "registro": cliente,
        "primeiro_nome": primeiro_nome,
        "iniciais": "".join(parte[0] for parte in cliente.nome.split()[:2]).upper() if cliente.nome else "DF",
    }
    return render(request, "cadastro/cadastro_concluido.html", context)


def perfil_cliente(request):
    cliente_id = request.GET.get("id", "").strip()
    if not cliente_id:
        raise Http404("Perfil nao encontrado.")

    cliente = get_object_or_404(Cliente, id=cliente_id)
    primeiro_nome = cliente.nome.split()[0] if cliente.nome else "Cliente"
    context = {
        "registro": cliente,
        "primeiro_nome": primeiro_nome,
        "iniciais": "".join(parte[0] for parte in cliente.nome.split()[:2]).upper() if cliente.nome else "DF",
        "avaliacoes": cliente.avaliacoes.all(),
    }
    return render(request, "cadastro/perfil_cliente.html", context)


def dev_login(request):
    if request.user.is_authenticated:
        return redirect("dev_dashboard")

    context = {"error_message": ""}

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is None:
            context["error_message"] = "Usuario ou senha invalidos."
        else:
            login(request, user)
            return redirect("dev_dashboard")

    return render(request, "cadastro/dev_login.html", context)


def dev_logout(request):
    logout(request)
    return redirect("dev_login")


@login_required(login_url="dev_login")
def dev_dashboard(request):
    registros = Cadastro.objects.all()
    clientes = Cliente.objects.all()
    context = {
        "registros": registros,
        "clientes": clientes,
        "total_registros": registros.count(),
        "total_login": registros.filter(tipo="login").count(),
        "total_cadastro": registros.filter(tipo="cadastro").count(),
        "total_clientes": clientes.count(),
    }
    return render(request, "cadastro/dev_dashboard.html", context)
