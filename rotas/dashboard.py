from flask import Blueprint, render_template, request, session

from database import conectar, listar_gastos_fixos, listar_rendas_fixas
from funcoes import (
    mes_atual,
    calcular_parcelamento,
    calcular_total_gastos_fixos,
    analisar_situacao_financeira,
    calcular_total_rendas_fixas,
    preparar_rendas_fixas_mes
)
from rotas.auth import login_obrigatorio


dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_obrigatorio
def dashboard():
    usuario_id = session.get('usuario_id')
    mes = request.args.get('mes', mes_atual())

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT COALESCE(SUM(valor), 0) AS total
        FROM lancamentos
        WHERE usuario_id = ?
        AND tipo = 'receita'
        AND ativo = 1
        AND substr(data, 1, 7) = ?
        ''',
        (usuario_id, mes)
    )

    total_receitas_lancamentos = cursor.fetchone()['total']

    cursor.execute(
        '''
        SELECT COALESCE(SUM(valor), 0) AS total
        FROM lancamentos
        WHERE usuario_id = ?
        AND tipo = 'despesa'
        AND ativo = 1
        AND substr(data, 1, 7) = ?
        ''',
        (usuario_id, mes)
    )

    total_despesas = cursor.fetchone()['total']

    cursor.execute(
        '''
        SELECT
            categorias.nome AS categoria,
            COALESCE(SUM(lancamentos.valor), 0) AS total
        FROM lancamentos
        JOIN categorias ON categorias.id = lancamentos.categoria_id
        WHERE lancamentos.usuario_id = ?
        AND lancamentos.tipo = 'despesa'
        AND lancamentos.ativo = 1
        AND substr(lancamentos.data, 1, 7) = ?
        GROUP BY categorias.nome
        ORDER BY total DESC
        LIMIT 1
        ''',
        (usuario_id, mes)
    )

    maior_categoria = cursor.fetchone()

    cursor.execute(
        '''
        SELECT
            categorias.nome AS categoria,
            COALESCE(SUM(lancamentos.valor), 0) AS total
        FROM lancamentos
        JOIN categorias ON categorias.id = lancamentos.categoria_id
        WHERE lancamentos.usuario_id = ?
        AND lancamentos.tipo = 'despesa'
        AND lancamentos.ativo = 1
        AND substr(lancamentos.data, 1, 7) = ?
        GROUP BY categorias.nome
        ORDER BY total DESC
        ''',
        (usuario_id, mes)
    )

    despesas_por_categoria = cursor.fetchall()

    cursor.execute(
        '''
        SELECT
            lancamentos.id,
            lancamentos.tipo,
            lancamentos.descricao,
            lancamentos.valor,
            lancamentos.data,
            lancamentos.forma_pagamento,
            categorias.nome AS categoria,
            subcategorias.nome AS subcategoria
        FROM lancamentos
        JOIN categorias ON categorias.id = lancamentos.categoria_id
        LEFT JOIN subcategorias ON subcategorias.id = lancamentos.subcategoria_id
        WHERE lancamentos.usuario_id = ?
        AND lancamentos.ativo = 1
        ORDER BY lancamentos.data DESC, lancamentos.id DESC
        LIMIT 5
        ''',
        (usuario_id,)
    )

    ultimos_lancamentos = cursor.fetchall()

    cursor.execute(
        '''
        SELECT
            compras_cartao.*,
            cartoes.nome AS cartao
        FROM compras_cartao
        JOIN cartoes ON cartoes.id = compras_cartao.cartao_id
        WHERE compras_cartao.usuario_id = ?
        AND compras_cartao.ativo = 1
        AND cartoes.ativo = 1
        ''',
        (usuario_id,)
    )

    compras_cartao = cursor.fetchall()
    total_parcelas_cartao = 0
    total_pendente_cartao = 0
    parcelas_ativas = []

    for compra in compras_cartao:
        dados = calcular_parcelamento(
            compra['data_compra'],
            compra['parcelas_total'],
            compra['valor_total']
        )

        if dados['status'] == 'Em andamento':
            total_parcelas_cartao += dados['valor_parcela']

            parcelas_ativas.append({
                'descricao': compra['descricao'],
                'cartao': compra['cartao'],
                'valor_parcela': dados['valor_parcela'],
                'parcela_atual': dados['parcela_atual'],
                'parcelas_total': compra['parcelas_total'],
                'parcelas_pendentes': dados['parcelas_pendentes']
            })

        total_pendente_cartao += dados['valor_pendente']

    cursor.execute(
        '''
        SELECT COALESCE(SUM(valor_estimado), 0) AS total
        FROM planejamentos
        WHERE usuario_id = ?
        AND ativo = 1
        AND realizado = 0
        ''',
        (usuario_id,)
    )

    total_planejado = cursor.fetchone()['total']

    cursor.execute(
        '''
        SELECT COALESCE(SUM(valor), 0) AS total
        FROM renda_extra
        WHERE usuario_id = ?
        AND ativo = 1
        ''',
        (usuario_id,)
    )

    total_renda_extra = cursor.fetchone()['total']
    conexao.close()

    rendas_fixas = listar_rendas_fixas(usuario_id)
    rendas_fixas_mes = preparar_rendas_fixas_mes(rendas_fixas, mes)
    total_renda_fixa = calcular_total_rendas_fixas(rendas_fixas)
    total_receitas = total_receitas_lancamentos + total_renda_fixa
    saldo = total_receitas - total_despesas

    gastos_fixos = listar_gastos_fixos(usuario_id)
    total_gastos_fixos = calcular_total_gastos_fixos(gastos_fixos, total_parcelas_cartao)
    situacao = analisar_situacao_financeira(saldo, total_gastos_fixos)
    saldo_previsto = saldo - total_gastos_fixos

    return render_template(
        'dashboard.html',
        mes=mes,
        total_receitas=total_receitas,
        total_receitas_lancamentos=total_receitas_lancamentos,
        total_renda_fixa=total_renda_fixa,
        rendas_fixas_mes=rendas_fixas_mes,
        total_despesas=total_despesas,
        saldo=saldo,
        saldo_previsto=saldo_previsto,
        maior_categoria=maior_categoria,
        despesas_por_categoria=despesas_por_categoria,
        ultimos_lancamentos=ultimos_lancamentos,
        gastos_fixos=gastos_fixos,
        total_gastos_fixos=total_gastos_fixos,
        total_parcelas_cartao=total_parcelas_cartao,
        total_pendente_cartao=total_pendente_cartao,
        parcelas_ativas=parcelas_ativas,
        total_planejado=total_planejado,
        total_renda_extra=total_renda_extra,
        situacao=situacao
    )
