from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Cliente, Categoria, Procedimento, HistoricoProcedimento ,Report

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'empresa', 'email', 'telefone', 'total_procedimentos', 'ativo']
    list_filter = ['ativo', 'criado_em', 'empresa']
    search_fields = ['nome', 'empresa', 'email']
    list_editable = ['ativo']
    
    def total_procedimentos(self, obj):
        return obj.procedimentos.filter(ativo=True).count()
    total_procedimentos.short_description = 'Total de Procedimentos'

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao', 'cor_preview', 'icone_preview', 'total_procedimentos']
    list_filter = ['nome']
    search_fields = ['nome', 'descricao']
    
    def cor_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; display: inline-block; border-radius: 3px;"></div>',
            obj.cor
        )
    cor_preview.short_description = 'Cor'
    
    def icone_preview(self, obj):
        if obj.icone:
            return format_html('<i class="{}" style="font-size: 16px;"></i>', obj.icone)
        return '-'
    icone_preview.short_description = 'Ícone'
    
    def total_procedimentos(self, obj):
        return obj.procedimentos.filter(ativo=True).count()
    total_procedimentos.short_description = 'Total de Procedimentos'

class HistoricoProcedimentoInline(admin.TabularInline):
    model = HistoricoProcedimento
    extra = 0
    readonly_fields = ['usuario', 'acao', 'data', 'observacoes']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Procedimento)
class ProcedimentoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'cliente', 'prioridade_badge', 'status_badge', 'criado_por', 'visualizacoes', 'eficacia', 'ativo']
    list_filter = ['categoria', 'cliente', 'prioridade', 'status', 'ativo', 'criado_em', 'atualizado_em']
    search_fields = ['titulo', 'descricao', 'solucao', 'tags', 'cliente__nome', 'cliente__empresa']
    readonly_fields = ['criado_em', 'atualizado_em', 'visualizacoes', 'ultimo_uso', 'imagem_preview']
    inlines = [HistoricoProcedimentoInline]
    list_editable = ['ativo']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'categoria', 'cliente', 'prioridade', 'status', 'ativo')
        }),
        ('Conteúdo', {
            'fields': ('descricao', 'solucao', 'tags')
        }),
        ('Mídia e Links', {
            'fields': ('imagem', 'imagem_preview', 'link_externo', 'video_url'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('criado_por', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
        ('Estatísticas', {
            'fields': ('visualizacoes', 'ultimo_uso', 'eficacia'),
            'classes': ('collapse',)
        }),
    )
    
    def prioridade_badge(self, obj):
        cores = {
            'baixa': '#28a745',
            'media': '#ffc107', 
            'alta': '#fd7e14',
            'critica': '#dc3545'
        }
        cor = cores.get(obj.prioridade, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 500;">{}</span>',
            cor,
            obj.get_prioridade_display()
        )
    prioridade_badge.short_description = 'Prioridade'
    prioridade_badge.admin_order_field = 'prioridade'
    
    def status_badge(self, obj):
        cores = {
            'ativo': '#28a745',
            'revisao': '#ffc107',
            'desatualizado': '#fd7e14',
            'arquivado': '#6c757d'
        }
        cor = cores.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 500;">{}</span>',
            cor,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def imagem_preview(self, obj):
        if obj.imagem:
            # Exibe a imagem no seu tamanho original, sem limites de largura ou altura
            return format_html(
                '<img src="{}" style="border-radius: 5px;" />',
                obj.imagem.url
            )
        return 'Nenhuma imagem'
    
    imagem_preview.short_description = 'Preview da Imagem'    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)
        
        # Registrar no histórico
        acao = 'editado' if change else 'criado'
        HistoricoProcedimento.objects.create(
            procedimento=obj,
            usuario=request.user,
            acao=acao
        )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('categoria', 'criado_por')

@admin.register(HistoricoProcedimento)
class HistoricoProcedimentoAdmin(admin.ModelAdmin):
    list_display = ['procedimento', 'usuario', 'acao', 'data']
    list_filter = ['acao', 'data', 'usuario']
    search_fields = ['procedimento__titulo', 'usuario__username', 'observacoes']
    readonly_fields = ['procedimento', 'usuario', 'acao', 'data']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

# Customização do Admin Site
admin.site.site_header = "OpsFinder - Sistema de Procedimentos"
admin.site.site_title = "OpsFinder Admin"
admin.site.index_title = "Painel de Administração"


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('procedimento', 'motivo', 'criado_em', 'processado')
    search_fields = ('procedimento__titulo', 'motivo')
    list_filter = ('criado_em', 'processado')
    ordering = ('-criado_em',)

    # Ação personalizada
    actions = ['marcar_como_processado']

    def marcar_como_processado(self, request, queryset):
        # Marcar os relatórios selecionados como processados
        updated_count = queryset.update(processado=True)
        self.message_user(request, f'{updated_count} relatórios foram marcados como processados.')
    
    marcar_como_processado.short_description = "Marcar como processados"
