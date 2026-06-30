from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from database import conectar, listar_renda_extra
from funcoes import converter_valor, validar_data, data_atual, dica_renda_extra
from rotas.auth import login_obrigatorio


renda_extra_bp = Blueprint('renda_extra', __name__)


@renda_extra_bp.route('/renda-extra')
@login_obrigatorio
def renda_extra():
    usuario_id = session.get('usuario_id')
    rendas = listar_renda_extra(usuario_id)
    total_renda_extra = 0

    for renda in rendas:
        total_renda_extra += renda['valor']

    dica = dica_renda_extra(total_renda_extra)

    return render_template(
        'renda_extra.html',
        rendas=rendas,
        total_renda_extra=total_renda_extra,
        dica=dica,
        data_padrao=data_atual()
    )


@renda_extra_bp.route('/renda-extra/nova', methods=['POST'])
@login_obrigatorio
def nova_renda_extra():
    usuario_id = session.get('usuario_id')
    descricao = request.form.get('descricao', '').strip()
    valor = converter_valor(request.form.get('valor', ''))
    origem = request.form.get('origem', '').strip()
    objetivo = request.form.get('objetivo', '').strip()
    data = request.form.get('data', '').strip()

    if not descricao or valor is None or not data:
        flash('Preencha descrição, valor e data.', 'erro')
        return redirect(url_for('renda_extra.renda_extra'))

    if not validar_data(data):
        flash('Data inválida.', 'erro')
        return redirect(url_for('renda_extra.renda_extra'))

    if not origem:
        origem = 'Não informado'

    if not objetivo:
        objetivo = 'Investimento'

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        INSERT INTO renda_extra (
            usuario_id,
            descricao,
            valor,
            origem,
            objetivo,
            data
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (usuario_id, descricao, valor, origem, objetivo, data)
    )

    conexao.commit()
    conexao.close()

    flash('Renda extra cadastrada com sucesso.', 'sucesso')
    return redirect(url_for('renda_extra.renda_extra'))


@renda_extra_bp.route('/renda-extra/editar/<int:renda_id>', methods=['POST'])
@login_obrigatorio
def editar_renda_extra(renda_id):
    usuario_id = session.get('usuario_id')
    descricao = request.form.get('descricao', '').strip()
    valor = converter_valor(request.form.get('valor', ''))
    origem = request.form.get('origem', '').strip()
    objetivo = request.form.get('objetivo', '').strip()
    data = request.form.get('data', '').strip()

    if not descricao or valor is None or not data:
        flash('Preencha descrição, valor e data.', 'erro')
        return redirect(url_for('renda_extra.renda_extra'))

    if not validar_data(data):
        flash('Data inválida.', 'erro')
        return redirect(url_for('renda_extra.renda_extra'))

    if not origem:
        origem = 'Não informado'

    if not objetivo:
        objetivo = 'Investimento'

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE renda_extra
        SET descricao = ?,
            valor = ?,
            origem = ?,
            objetivo = ?,
            data = ?
        WHERE id = ?
        AND usuario_id = ?
        AND ativo = 1
        ''',
        (descricao, valor, origem, objetivo, data, renda_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Renda extra atualizada com sucesso.', 'sucesso')
    return redirect(url_for('renda_extra.renda_extra'))


@renda_extra_bp.route('/renda-extra/excluir/<int:renda_id>')
@login_obrigatorio
def excluir_renda_extra(renda_id):
    usuario_id = session.get('usuario_id')

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE renda_extra
        SET ativo = 0
        WHERE id = ?
        AND usuario_id = ?
        ''',
        (renda_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Renda extra desativada com sucesso.', 'sucesso')
    return redirect(url_for('renda_extra.renda_extra'))
