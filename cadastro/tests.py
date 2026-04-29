from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Avaliacao, Cadastro, Cliente


class CadastroFlowTests(TestCase):
    def test_dev_dashboard_requires_login(self):
        response = self.client.get(reverse("dev_dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin_portal_login"), response.url)

    def test_dev_login_allows_dashboard_access(self):
        User.objects.create_user(username="RaphaXd", password="121261ca", is_staff=True)

        response = self.client.post(
            reverse("dev_login"),
            {"username": "RaphaXd", "password": "121261ca"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dev_dashboard"))

    def test_admin_user_management_requires_staff_login(self):
        response = self.client.get(reverse("admin_user_management"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin_portal_login"), response.url)

    def test_staff_can_view_user_management_data(self):
        User.objects.create_user(username="staff", password="senha12345", is_staff=True)
        self.client.login(username="staff", password="senha12345")

        response = self.client.get(reverse("admin_user_management_data"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["current_user"], "staff")
        self.assertFalse(data["can_manage_users"])

    def test_staff_cannot_change_user_permissions(self):
        staff = User.objects.create_user(username="staff", password="senha12345", is_staff=True)
        target = User.objects.create_user(username="target", password="senha12345")
        self.client.login(username=staff.username, password="senha12345")

        response = self.client.post(
            reverse("admin_user_management_action"),
            {"user_id": target.id, "action": "make_staff"},
        )

        target.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertFalse(target.is_staff)

    def test_superuser_can_change_user_permissions(self):
        User.objects.create_superuser(username="admin", password="senha12345")
        target = User.objects.create_user(username="target", password="senha12345")
        self.client.login(username="admin", password="senha12345")

        response = self.client.post(
            reverse("admin_user_management_action"),
            {"user_id": target.id, "action": "make_staff"},
        )

        target.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.assertTrue(target.is_staff)

    def test_admin_user_action_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        User.objects.create_superuser(username="admin", password="senha12345")
        target = User.objects.create_user(username="target", password="senha12345")
        client.login(username="admin", password="senha12345")

        response = client.post(
            reverse("admin_user_management_action"),
            {"user_id": target.id, "action": "make_staff"},
        )

        self.assertEqual(response.status_code, 403)

    def test_cannot_disable_last_active_superuser(self):
        admin = User.objects.create_superuser(username="admin", password="senha12345")
        self.client.login(username="admin", password="senha12345")

        response = self.client.post(
            reverse("admin_user_management_action"),
            {"user_id": admin.id, "action": "deactivate"},
        )

        admin.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(admin.is_active)

    def test_login_redirects_to_profile_page(self):
        response = self.client.post(
            reverse("index"),
            {
                "nome": "Raphael",
                "email": "raphael@example.com",
                "telefone": "(21) 99999-0000",
                "tipo": "login",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("perfil_cliente")))
        self.assertIn("id=", response.url)
        self.assertEqual(Cliente.objects.count(), 1)

    def test_cadastro_redirects_to_confirmation_page(self):
        response = self.client.post(
            reverse("index"),
            {
                "nome": "Raphael",
                "email": "raphael@example.com",
                "telefone": "(21) 99999-0000",
                "tipo": "cadastro",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("cadastro_concluido")))
        self.assertEqual(Cadastro.objects.count(), 1)
        self.assertEqual(Cliente.objects.count(), 1)
        self.assertIn("id=", response.url)

    def test_confirmation_page_renders_submitted_data(self):
        cliente = Cliente.objects.create(
            nome="Raphael Tuller",
            email="raphael@example.com",
            telefone="(21) 99999-0000",
        )
        response = self.client.get(
            reverse("cadastro_concluido"),
            {
                "id": cliente.id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Raphael Tuller")
        self.assertContains(response, "raphael@example.com")
        self.assertContains(response, "(21) 99999-0000")
        self.assertContains(response, "Perfil do usuario")

    def test_profile_page_renders_user_data_and_reviews(self):
        cliente = Cliente.objects.create(
            nome="Raphael Tuller",
            email="raphael@example.com",
            telefone="(21) 99999-0000",
        )
        Avaliacao.objects.create(cliente=cliente, titulo="Avaliacao fisica", nota="5.0", comentario="Tudo certo")
        response = self.client.get(
            reverse("perfil_cliente"),
            {
                "id": cliente.id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Raphael Tuller")
        self.assertContains(response, "Avaliacoes do cliente")
        self.assertContains(response, "Avaliacao fisica")

    def test_ajax_cadastro_returns_redirect_url(self):
        response = self.client.post(
            reverse("index"),
            {
                "nome": "Raphael",
                "email": "raphael@example.com",
                "telefone": "(21) 99999-0000",
                "tipo": "cadastro",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        self.assertIn(reverse("cadastro_concluido"), data["redirect_url"])
        self.assertIn("id=", data["redirect_url"])
        self.assertEqual(Cliente.objects.count(), 1)

    def test_ajax_login_returns_redirect_url(self):
        response = self.client.post(
            reverse("index"),
            {
                "nome": "Raphael",
                "email": "raphael@example.com",
                "telefone": "(21) 99999-0000",
                "tipo": "login",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        self.assertIn(reverse("perfil_cliente"), data["redirect_url"])
        self.assertIn("id=", data["redirect_url"])

    def test_cadastro_reutiliza_cliente_por_email(self):
        Cliente.objects.create(
            nome="Raphael Antigo",
            email="raphael@example.com",
            telefone="(21) 98888-0000",
        )

        self.client.post(
            reverse("index"),
            {
                "nome": "Raphael Atualizado",
                "email": "raphael@example.com",
                "telefone": "(21) 99999-0000",
                "tipo": "cadastro",
            },
        )

        self.assertEqual(Cliente.objects.count(), 1)
        cliente = Cliente.objects.get(email="raphael@example.com")
        self.assertEqual(cliente.nome, "Raphael Atualizado")
        self.assertEqual(cliente.telefone, "(21) 99999-0000")
