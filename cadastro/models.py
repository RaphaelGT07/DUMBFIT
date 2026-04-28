from django.db import models


class Cliente(models.Model):
    STATUS_CHOICES = [
        ("ativo", "Ativo"),
        ("analise", "Em analise"),
    ]

    nome = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="analise")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.nome


class Cadastro(models.Model):
    TIPO_CHOICES = [
        ("login", "Login"),
        ("cadastro", "Cadastro"),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="historico_acessos",
        null=True,
        blank=True,
    )
    nome = models.CharField(max_length=120)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Cadastro"
        verbose_name_plural = "Cadastros"

    def __str__(self):
        return f"{self.nome} - {self.get_tipo_display()}"


class Avaliacao(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="avaliacoes")
    titulo = models.CharField(max_length=120)
    nota = models.DecimalField(max_digits=2, decimal_places=1)
    comentario = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Avaliacao"
        verbose_name_plural = "Avaliacoes"

    def __str__(self):
        return f"{self.cliente.nome} - {self.titulo}"
