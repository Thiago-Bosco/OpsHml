from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Cliente(models.Model):
    nome = models.CharField(max_length=200)
    empresa = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome']
    
    def __str__(self):
        if self.empresa:
            return f"{self.nome} ({self.empresa})"
        return self.nome

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    cor = models.CharField(max_length=7, default="#007bff", help_text="Cor em hexadecimal (ex: #007bff)")
    icone = models.CharField(max_length=50, blank=True, help_text="Nome do ícone FontAwesome (ex: fas fa-network-wired)")
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

class Procedimento(models.Model):
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('revisao', 'Em Revisão'),
        ('desatualizado', 'Desatualizado'),
        ('arquivado', 'Arquivado'),
    ]
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(help_text="Descrição detalhada do problema")
    solucao = models.TextField(help_text="Procedimento passo-a-passo para resolver")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='procedimentos')
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='procedimentos', help_text="Cliente específico (opcional)")
    tags = models.CharField(max_length=500, help_text="Tags separadas por vírgula (ex: rede, servidor, windows)")
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='media')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ativo')
    
    # Mídia e Links
    imagem = models.ImageField(upload_to='procedimentos/imagens/', blank=True, null=True,
                              help_text="Imagem ilustrativa do problema ou solução")
    link_externo = models.URLField(blank=True, help_text="Link para documentação externa")
    video_url = models.URLField(blank=True, help_text="URL do vídeo explicativo (YouTube, Vimeo, etc.)")
    
    # Metadados
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='procedimentos_criados')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True, help_text="Desmarque para arquivar o procedimento")
    
    # Estatísticas
    visualizacoes = models.PositiveIntegerField(default=0)
    ultimo_uso = models.DateTimeField(null=True, blank=True)
    eficacia = models.PositiveIntegerField(default=0, help_text="Número de vezes que resolveu o problema")
    
    class Meta:
        verbose_name = "Procedimento"
        verbose_name_plural = "Procedimentos"
        ordering = ['-atualizado_em']
        indexes = [
            models.Index(fields=['categoria', 'ativo']),
            models.Index(fields=['prioridade']),
            models.Index(fields=['tags']),
        ]
    
    def __str__(self):
        return self.titulo
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def incrementar_visualizacao(self):
        from django.utils import timezone
        self.visualizacoes += 1
        self.ultimo_uso = timezone.now()
        self.save(update_fields=['visualizacoes', 'ultimo_uso'])

class HistoricoProcedimento(models.Model):
    procedimento = models.ForeignKey(Procedimento, on_delete=models.CASCADE, related_name='historico')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    acao = models.CharField(max_length=50)  # 'visualizado', 'utilizado', 'editado'
    data = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Histórico de Procedimento"
        verbose_name_plural = "Histórico de Procedimentos"
        ordering = ['-data']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.acao} - {self.procedimento.titulo}"
    


# models.py
from django.db import models

class Report(models.Model):
    procedimento = models.ForeignKey('Procedimento', on_delete=models.CASCADE)
    motivo = models.TextField()
    processado = models.BooleanField(default=False)  # Novo campo
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report do procedimento {self.procedimento.titulo}"
