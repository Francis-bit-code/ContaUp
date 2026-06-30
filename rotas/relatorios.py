from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from database import conectar, listar_gastos_fixos, listar_renda_extra, listar_rendas_fixas
from funcoes import mes_atual, calcular_parcelamento, calcular_total_gastos_fixos, data_atual, calcular_total_rendas_fixas, preparar_rendas_fixas_mes
from rotas.auth import login_obrigatorio


relatorios_bp = Blueprint('relatorios', __name__)


def buscar_dados_relatorio(usuario_id, mes):
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
            lancamentos.tipo,
            COALESCE(SUM(lancamentos.valor), 0) AS total
        FROM lancamentos
        JOIN categorias ON categorias.id = lancamentos.categoria_id
        WHERE lancamentos.usuario_id = ?
        AND lancamentos.ativo = 1
        AND substr(lancamentos.data, 1, 7) = ?
        GROUP BY categorias.nome, lancamentos.tipo
        ORDER BY lancamentos.tipo, total DESC
        ''',
        (usuario_id, mes)
    )

    resumo_categorias = cursor.fetchall()

    cursor.execute(
        '''
        SELECT
            forma_pagamento,
            COALESCE(SUM(valor), 0) AS total
        FROM lancamentos
        WHERE usuario_id = ?
        AND tipo = 'despesa'
        AND ativo = 1
        AND substr(data, 1, 7) = ?
        GROUP BY forma_pagamento
        ORDER BY total DESC
        ''',
        (usuario_id, mes)
    )

    resumo_pagamentos = cursor.fetchall()

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
        ORDER BY cartoes.nome, compras_cartao.data_compra DESC
        ''',
        (usuario_id,)
    )

    compras_cartao = cursor.fetchall()

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
        SELECT *
        FROM relatorios_mensais
        WHERE usuario_id = ?
        AND mes = ?
        AND ativo = 1
        ORDER BY id DESC
        LIMIT 1
        ''',
        (usuario_id, mes)
    )

    fechamento_atual = cursor.fetchone()

    cursor.execute(
        '''
        SELECT *
        FROM relatorios_mensais
        WHERE usuario_id = ?
        AND mes < ?
        AND ativo = 1
        ORDER BY mes DESC
        LIMIT 1
        ''',
        (usuario_id, mes)
    )

    fechamento_anterior = cursor.fetchone()

    conexao.close()

    total_parcelas_cartao = 0
    total_pendente_cartao = 0
    resumo_cartoes = []

    for compra in compras_cartao:
        dados = calcular_parcelamento(
            compra['data_compra'],
            compra['parcelas_total'],
            compra['valor_total']
        )

        if dados['status'] == 'Em andamento':
            total_parcelas_cartao += dados['valor_parcela']

            resumo_cartoes.append({
                'cartao': compra['cartao'],
                'descricao': compra['descricao'],
                'valor_parcela': dados['valor_parcela'],
                'parcela_atual': dados['parcela_atual'],
                'parcelas_total': compra['parcelas_total'],
                'parcelas_pendentes': dados['parcelas_pendentes'],
                'valor_pendente': dados['valor_pendente']
            })

        total_pendente_cartao += dados['valor_pendente']

    gastos_fixos = listar_gastos_fixos(usuario_id)
    total_gastos_fixos = calcular_total_gastos_fixos(gastos_fixos, total_parcelas_cartao)
    rendas_extra = listar_renda_extra(usuario_id)
    total_renda_extra = 0

    for renda in rendas_extra:
        total_renda_extra += renda['valor']

    rendas_fixas = listar_rendas_fixas(usuario_id)
    rendas_fixas_mes = preparar_rendas_fixas_mes(rendas_fixas, mes)
    total_renda_fixa = calcular_total_rendas_fixas(rendas_fixas)
    total_receitas = total_receitas_lancamentos + total_renda_fixa
    saldo = total_receitas - total_despesas
    saldo_previsto = saldo - total_gastos_fixos

    return {
        'mes': mes,
        'total_receitas': total_receitas,
        'total_receitas_lancamentos': total_receitas_lancamentos,
        'total_renda_fixa': total_renda_fixa,
        'rendas_fixas_mes': rendas_fixas_mes,
        'total_despesas': total_despesas,
        'saldo': saldo,
        'saldo_previsto': saldo_previsto,
        'resumo_categorias': resumo_categorias,
        'resumo_pagamentos': resumo_pagamentos,
        'gastos_fixos': gastos_fixos,
        'total_gastos_fixos': total_gastos_fixos,
        'total_parcelas_cartao': total_parcelas_cartao,
        'total_pendente_cartao': total_pendente_cartao,
        'resumo_cartoes': resumo_cartoes,
        'total_planejado': total_planejado,
        'rendas_extra': rendas_extra,
        'total_renda_extra': total_renda_extra,
        'maior_categoria': maior_categoria,
        'fechamento_atual': fechamento_atual,
        'fechamento_anterior': fechamento_anterior
    }


@relatorios_bp.route('/relatorios')
@login_obrigatorio
def relatorios():
    usuario_id = session.get('usuario_id')
    mes = request.args.get('mes', mes_atual())
    dados = buscar_dados_relatorio(usuario_id, mes)

    return render_template('relatorios.html', **dados)


@relatorios_bp.route('/relatorios/gerar', methods=['POST'])
@login_obrigatorio
def gerar_relatorio_mensal():
    usuario_id = session.get('usuario_id')
    mes = request.form.get('mes', mes_atual())
    dados = buscar_dados_relatorio(usuario_id, mes)
    maior_categoria = None

    if dados['maior_categoria']:
        maior_categoria = dados['maior_categoria']['categoria']

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE relatorios_mensais
        SET ativo = 0
        WHERE usuario_id = ?
        AND mes = ?
        ''',
        (usuario_id, mes)
    )

    cursor.execute(
        '''
        INSERT INTO relatorios_mensais (
            usuario_id,
            mes,
            total_receitas,
            total_despesas,
            saldo,
            total_gastos_fixos,
            total_parcelas_cartao,
            total_pendente_cartao,
            total_renda_extra,
            total_planejado,
            maior_categoria,
            data_geracao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            usuario_id,
            mes,
            dados['total_receitas'],
            dados['total_despesas'],
            dados['saldo'],
            dados['total_gastos_fixos'],
            dados['total_parcelas_cartao'],
            dados['total_pendente_cartao'],
            dados['total_renda_extra'],
            dados['total_planejado'],
            maior_categoria,
            data_atual()
        )
    )

    conexao.commit()
    conexao.close()

    flash('Fechamento mensal gerado com sucesso.', 'sucesso')
    return redirect(url_for('relatorios.relatorios', mes=mes))
