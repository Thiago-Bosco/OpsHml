from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Procedimento, Categoria, HistoricoProcedimento ,Report



@login_required
def buscar_procedimentos(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    prioridade = request.GET.get('prioridade', '')
    
    procedimentos = Procedimento.objects.filter(ativo=True).select_related('categoria', 'criado_por')
    
    if query:
        procedimentos = procedimentos.filter(
            Q(titulo__icontains=query) |
            Q(descricao__icontains=query) |
            Q(solucao__icontains=query) |
            Q(tags__icontains=query)
        )
    
    if categoria_id:
        procedimentos = procedimentos.filter(categoria_id=categoria_id)
    
    if prioridade:
        procedimentos = procedimentos.filter(prioridade=prioridade)
    
    # Paginação
    paginator = Paginator(procedimentos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categorias = Categoria.objects.all()
    prioridades = Procedimento.PRIORIDADE_CHOICES
    
    context = {
        'procedimentos': page_obj,
        'categorias': categorias,
        'prioridades': prioridades,
        'query': query,
        'categoria_selecionada': categoria_id,
        'prioridade_selecionada': prioridade,
    }
    
    return render(request, 'procedimentos/buscar.html', context)

@login_required
def detalhe_procedimento(request, procedimento_id):
    procedimento = get_object_or_404(Procedimento, id=procedimento_id, ativo=True)
    
    # Incrementar visualização
    procedimento.incrementar_visualizacao()
    
    # Registrar no histórico
    HistoricoProcedimento.objects.create(
        procedimento=procedimento,
        usuario=request.user,
        acao='visualizado'
    )
    
    # Procedimentos relacionados (mesma categoria)
    relacionados = Procedimento.objects.filter(
        categoria=procedimento.categoria,
        ativo=True
    ).exclude(id=procedimento.id)[:5]
    
    context = {
        'procedimento': procedimento,
        'relacionados': relacionados,
    }
    
    return render(request, 'procedimentos/detalhe.html', context)

@login_required
def api_busca_rapida(request):
    """API para busca rápida via AJAX"""
    query = request.GET.get('q', '')
    
    if len(query) < 3:
        return JsonResponse({'resultados': []})
    
    procedimentos = Procedimento.objects.filter(
        Q(titulo__icontains=query) |
        Q(tags__icontains=query),
        ativo=True
    ).select_related('categoria')[:10]
    
    resultados = []
    for proc in procedimentos:
        resultados.append({
            'id': proc.id,
            'titulo': proc.titulo,
            'categoria': proc.categoria.nome,
            'prioridade': proc.get_prioridade_display(),
            'url': f'/procedimentos/{proc.id}/'
        })
    
    return JsonResponse({'resultados': resultados})

def reportar_problema(request):
    if request.method == 'POST':
        procedimento_id = request.POST.get('procedimento_id')
        motivo = request.POST.get('motivo')

        if procedimento_id and motivo:
            try:
                procedimento = Procedimento.objects.get(id=procedimento_id)
                # Criação do Report
                Report.objects.create(procedimento=procedimento, motivo=motivo)

                return JsonResponse({'success': True})

            except Procedimento.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Procedimento não encontrado.'})

        return JsonResponse({'success': False, 'message': 'Faltando dados necessários.'})
    else:
        return JsonResponse({'success': False, 'message': 'Método inválido.'})
    

    