from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from database import conectar, listar_planejamentos, listar_gastos_fixos, listar_rendas_fixas
from funcoes import (
    converter_valor,
    validar_data,
    mes_atual,
    analisar_planejamento,
    calcular_parcelamento,
    calcular_total_gastos_fixos,
    calcular_total_rendas_fixas
)
from rotas.auth import login_obrigatorio


planejamento_bp = Blueprint('planejamento', __name__)


@planejamento_bp.route('/planejamento')
@login_obrigatorio
def planejamento():
    usuario_id = session.get('usuario_id')
    mes = request.args.get('mes', mes_atual())
    planejamentos = listar_planejamentos(usuario_id)
    gastos_fixos = listar_gastos_fixos(usuario_id)

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
        SELECT *
        FROM compras_cartao
        WHERE usuario_id = ?
        AND ativo = 1
        ''',
        (usuario_id,)
    )

    compras_cartao = cursor.fetchall()
    conexao.close()

    total_parcelas_cartao = 0

    for compra in compras_cartao:
        dados = calcular_parcelamento(
            compra['data_compra'],
            compra['parcelas_total'],
            compra['valor_total']
        )

        if dados['status'] == 'Em andamento':
            total_parcelas_cartao += dados['valor_parcela']

    rendas_fixas = listar_rendas_fixas(usuario_id)
    total_renda_fixa = calcular_total_rendas_fixas(rendas_fixas)
    total_receitas = total_receitas_lancamentos + total_renda_fixa
    saldo = total_receitas - total_despesas
    total_gastos_fixos = calcular_total_gastos_fixos(gastos_fixos, total_parcelas_cartao)
    saldo_previsto = saldo - total_gastos_fixos
    planejamentos_formatados = []

    for item in planejamentos:
        planejamentos_formatados.append({
            'id': item['id'],
            'descricao': item['descricao'],
            'valor_estimado': item['valor_estimado'],
            'data_desejada': item['data_desejada'],
            'prioridade': item['prioridade'],
            'observacao': item['observacao'],
            'realizado': item['realizado'],
            'analise': analisar_planejamento(item['valor_estimado'], saldo_previsto)
        })

    return render_template(
        'planejamento.html',
        planejamentos=planejamentos_formatados,
        mes=mes,
        total_receitas=total_receitas,
        total_renda_fixa=total_renda_fixa,
        total_despesas=total_despesas,
        total_gastos_fixos=total_gastos_fixos,
        saldo=saldo,
        saldo_previsto=saldo_previsto
    )


@planejamento_bp.route('/planejamento/novo', methods=['POST'])
@login_obrigatorio
def novo_planejamento():
    usuario_id = session.get('usuario_id')
    descricao = request.form.get('descricao', '').strip()
    valor_estimado = converter_valor(request.form.get('valor_estimado', ''))
    data_desejada = request.form.get('data_desejada', '').strip()
    prioridade = request.form.get('prioridade', 'Média').strip()
    observacao = request.form.get('observacao', '').strip()

    if not descricao or valor_estimado is None:
        flash('Preencha descrição e valor estimado.', 'erro')
        return redirect(url_for('planejamento.planejamento'))

    if data_desejada and not validar_data(data_desejada):
        flash('Data desejada inválida.', 'erro')
        return redirect(url_for('planejamento.planejamento'))

    if data_desejada == '':
        data_desejada = None

    if prioridade not in ['Baixa', 'Média', 'Alta']:
        prioridade = 'Média'

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        INSERT INTO planejamentos (
            usuario_id,
            descricao,
            valor_estimado,
            data_desejada,
            prioridade,
            observacao
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (usuario_id, descricao, valor_estimado, data_desejada, prioridade, observacao)
    )

    conexao.commit()
    conexao.close()

    flash('Planejamento cadastrado com sucesso.', 'sucesso')
    return redirect(url_for('planejamento.planejamento'))


@planejamento_bp.route('/planejamento/editar/<int:planejamento_id>', methods=['POST'])
@login_obrigatorio
def editar_planejamento(planejamento_id):
    usuario_id = session.get('usuario_id')
    descricao = request.form.get('descricao', '').strip()
    valor_estimado = converter_valor(request.form.get('valor_estimado', ''))
    data_desejada = request.form.get('data_desejada', '').strip()
    prioridade = request.form.get('prioridade', 'Média').strip()
    observacao = request.form.get('observacao', '').strip()

    if not descricao or valor_estimado is None:
        flash('Preencha descrição e valor estimado.', 'erro')
        return redirect(url_for('planejamento.planejamento'))

    if data_desejada and not validar_data(data_desejada):
        flash('Data desejada inválida.', 'erro')
        return redirect(url_for('planejamento.planejamento'))

    if data_desejada == '':
        data_desejada = None

    if prioridade not in ['Baixa', 'Média', 'Alta']:
        prioridade = 'Média'

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE planejamentos
        SET descricao = ?,
            valor_estimado = ?,
            data_desejada = ?,
            prioridade = ?,
            observacao = ?
        WHERE id = ?
        AND usuario_id = ?
        AND ativo = 1
        ''',
        (descricao, valor_estimado, data_desejada, prioridade, observacao, planejamento_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Planejamento atualizado com sucesso.', 'sucesso')
    return redirect(url_for('planejamento.planejamento'))


@planejamento_bp.route('/planejamento/concluir/<int:planejamento_id>')
@login_obrigatorio
def concluir_planejamento(planejamento_id):
    usuario_id = session.get('usuario_id')

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE planejamentos
        SET realizado = 1
        WHERE id = ?
        AND usuario_id = ?
        AND ativo = 1
        ''',
        (planejamento_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Planejamento marcado como realizado.', 'sucesso')
    return redirect(url_for('planejamento.planejamento'))


@planejamento_bp.route('/planejamento/reabrir/<int:planejamento_id>')
@login_obrigatorio
def reabrir_planejamento(planejamento_id):
    usuario_id = session.get('usuario_id')

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE planejamentos
        SET realizado = 0
        WHERE id = ?
        AND usuario_id = ?
        AND ativo = 1
        ''',
        (planejamento_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Planejamento voltou para pendente.', 'sucesso')
    return redirect(url_for('planejamento.planejamento'))


@planejamento_bp.route('/planejamento/excluir/<int:planejamento_id>')
@login_obrigatorio
def excluir_planejamento(planejamento_id):
    usuario_id = session.get('usuario_id')

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE planejamentos
        SET ativo = 0
        WHERE id = ?
        AND usuario_id = ?
        ''',
        (planejamento_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Planejamento desativado com sucesso.', 'sucesso')
    return redirect(url_for('planejamento.planejamento'))
