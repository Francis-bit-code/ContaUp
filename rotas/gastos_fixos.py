from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from database import conectar, listar_gastos_fixos, listar_categorias
from funcoes import converter_valor, converter_inteiro, calcular_parcelamento, calcular_total_gastos_fixos
from rotas.auth import login_obrigatorio


gastos_fixos_bp = Blueprint('gastos_fixos', __name__)


@gastos_fixos_bp.route('/gastos-fixos')
@login_obrigatorio
def gastos_fixos():
    usuario_id = session.get('usuario_id')
    gastos = listar_gastos_fixos(usuario_id)

    conexao = conectar()
    cursor = conexao.cursor()

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
    conexao.close()

    total_parcelas_cartao = 0
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

    total_gastos_fixos = calcular_total_gastos_fixos(gastos, total_parcelas_cartao)

    return render_template(
        'gastos_fixos.html',
        gastos_fixos=gastos,
        categorias=listar_categorias(usuario_id, 'despesa'),
        total_parcelas_cartao=total_parcelas_cartao,
        total_gastos_fixos=total_gastos_fixos,
        parcelas_ativas=parcelas_ativas
    )


@gastos_fixos_bp.route('/gastos-fixos/novo', methods=['POST'])
@login_obrigatorio
def novo_gasto_fixo():
    usuario_id = session.get('usuario_id')
    descricao = request.form.get('descricao', '').strip()
    valor = converter_valor(request.form.get('valor', ''))
    dia_vencimento = converter_inteiro(request.form.get('dia_vencimento', ''))
    categoria_id = request.form.get('categoria_id', '').strip()
    forma_pagamento = request.form.get('forma_pagamento', 'Não informado').strip()

    if not descricao or valor is None:
        flash('Preencha descrição e valor.', 'erro')
        return redirect(url_for('gastos_fixos.gastos_fixos'))

    if dia_vencimento and dia_vencimento > 31:
        flash('Dia de vencimento inválido.', 'erro')
        return redirect(url_for('gastos_fixos.gastos_fixos'))

    if categoria_id == '':
        categoria_id = None

    if not forma_pagamento:
        forma_pagamento = 'Não informado'

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        INSERT INTO gastos_fixos (
            usuario_id,
            descricao,
            valor,
            dia_vencimento,
            categoria_id,
            forma_pagamento
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (usuario_id, descricao, valor, dia_vencimento, categoria_id, forma_pagamento)
    )

    conexao.commit()
    conexao.close()

    flash('Gasto fixo cadastrado com sucesso.', 'sucesso')
    return redirect(url_for('gastos_fixos.gastos_fixos'))


@gastos_fixos_bp.route('/gastos-fixos/editar/<int:gasto_id>', methods=['POST'])
@login_obrigatorio
def editar_gasto_fixo(gasto_id):
    usuario_id = session.get('usuario_id')
    descricao = request.form.get('descricao', '').strip()
    valor = converter_valor(request.form.get('valor', ''))
    dia_vencimento = converter_inteiro(request.form.get('dia_vencimento', ''))
    categoria_id = request.form.get('categoria_id', '').strip()
    forma_pagamento = request.form.get('forma_pagamento', 'Não informado').strip()

    if not descricao or valor is None:
        flash('Preencha descrição e valor.', 'erro')
        return redirect(url_for('gastos_fixos.gastos_fixos'))

    if categoria_id == '':
        categoria_id = None

    if not forma_pagamento:
        forma_pagamento = 'Não informado'

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE gastos_fixos
        SET descricao = ?,
            valor = ?,
            dia_vencimento = ?,
            categoria_id = ?,
            forma_pagamento = ?
        WHERE id = ?
        AND usuario_id = ?
        AND ativo = 1
        ''',
        (descricao, valor, dia_vencimento, categoria_id, forma_pagamento, gasto_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Gasto fixo atualizado com sucesso.', 'sucesso')
    return redirect(url_for('gastos_fixos.gastos_fixos'))


@gastos_fixos_bp.route('/gastos-fixos/excluir/<int:gasto_id>')
@login_obrigatorio
def excluir_gasto_fixo(gasto_id):
    usuario_id = session.get('usuario_id')

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE gastos_fixos
        SET ativo = 0
        WHERE id = ?
        AND usuario_id = ?
        ''',
        (gasto_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Gasto fixo desativado com sucesso.', 'sucesso')
    return redirect(url_for('gastos_fixos.gastos_fixos'))
