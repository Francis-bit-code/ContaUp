from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from database import conectar, listar_categorias, listar_subcategorias, buscar_categoria
from funcoes import converter_valor, converter_inteiro, validar_data, mes_atual, data_atual
from rotas.auth import login_obrigatorio


lancamentos_bp = Blueprint('lancamentos', __name__)


@lancamentos_bp.route('/lancamentos')
@login_obrigatorio
def lancamentos():
    usuario_id = session.get('usuario_id')
    mes = request.args.get('mes', mes_atual())
    tipo = request.args.get('tipo', '')

    conexao = conectar()
    cursor = conexao.cursor()

    if tipo in ['receita', 'despesa']:
        cursor.execute(
            '''
            SELECT
                lancamentos.*,
                categorias.nome AS categoria,
                subcategorias.nome AS subcategoria
            FROM lancamentos
            JOIN categorias ON categorias.id = lancamentos.categoria_id
            LEFT JOIN subcategorias ON subcategorias.id = lancamentos.subcategoria_id
            WHERE lancamentos.usuario_id = ?
            AND lancamentos.ativo = 1
            AND lancamentos.tipo = ?
            AND substr(lancamentos.data, 1, 7) = ?
            ORDER BY lancamentos.data DESC, lancamentos.id DESC
            ''',
            (usuario_id, tipo, mes)
        )
    else:
        cursor.execute(
            '''
            SELECT
                lancamentos.*,
                categorias.nome AS categoria,
                subcategorias.nome AS subcategoria
            FROM lancamentos
            JOIN categorias ON categorias.id = lancamentos.categoria_id
            LEFT JOIN subcategorias ON subcategorias.id = lancamentos.subcategoria_id
            WHERE lancamentos.usuario_id = ?
            AND lancamentos.ativo = 1
            AND substr(lancamentos.data, 1, 7) = ?
            ORDER BY lancamentos.data DESC, lancamentos.id DESC
            ''',
            (usuario_id, mes)
        )

    lancamentos_lista = cursor.fetchall()
    conexao.close()

    return render_template(
        'lancamentos.html',
        lancamentos=lancamentos_lista,
        categorias=listar_categorias(usuario_id),
        subcategorias=listar_subcategorias(usuario_id),
        mes=mes,
        tipo=tipo,
        data_padrao=data_atual()
    )


def validar_lancamento(usuario_id, tipo, categoria_id, subcategoria_id):
    categoria = buscar_categoria(usuario_id, categoria_id)

    if not categoria:
        return False, 'Categoria não encontrada.'

    if categoria['tipo'] != tipo:
        return False, 'O tipo do lançamento precisa ser igual ao tipo da categoria.'

    if categoria['usa_subcategorias'] == 1 and not subcategoria_id:
        return False, 'Essa categoria precisa de uma subcategoria.'

    if subcategoria_id:
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute(
            '''
            SELECT id
            FROM subcategorias
            WHERE id = ?
            AND usuario_id = ?
            AND categoria_id = ?
            AND ativo = 1
            ''',
            (subcategoria_id, usuario_id, categoria_id)
        )

        subcategoria = cursor.fetchone()
        conexao.close()

        if not subcategoria:
            return False, 'Subcategoria inválida para essa categoria.'

    return True, ''


@lancamentos_bp.route('/lancamentos/novo', methods=['POST'])
@login_obrigatorio
def novo_lancamento():
    usuario_id = session.get('usuario_id')
    tipo = request.form.get('tipo', '').strip()
    descricao = request.form.get('descricao', '').strip()
    valor = converter_valor(request.form.get('valor', ''))
    data = request.form.get('data', '').strip()
    categoria_id = request.form.get('categoria_id', '').strip()
    subcategoria_id = request.form.get('subcategoria_id', '').strip()
    forma_pagamento = request.form.get('forma_pagamento', 'Não informado').strip()
    parcelas = converter_inteiro(request.form.get('parcelas', '1')) or 1

    if tipo not in ['receita', 'despesa'] or not descricao or valor is None or not data or not categoria_id:
        flash('Preencha tipo, descrição, valor, data e categoria.', 'erro')
        return redirect(url_for('lancamentos.lancamentos'))

    if not validar_data(data):
        flash('Data inválida.', 'erro')
        return redirect(url_for('lancamentos.lancamentos'))

    valido, mensagem = validar_lancamento(usuario_id, tipo, categoria_id, subcategoria_id)

    if not valido:
        flash(mensagem, 'erro')
        return redirect(url_for('lancamentos.lancamentos'))

    if subcategoria_id == '':
        subcategoria_id = None

    if not forma_pagamento:
        forma_pagamento = 'Não informado'

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        INSERT INTO lancamentos (
            usuario_id,
            categoria_id,
            subcategoria_id,
            tipo,
            descricao,
            valor,
            data,
            forma_pagamento,
            parcelas
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            usuario_id,
            categoria_id,
            subcategoria_id,
            tipo,
            descricao,
            valor,
            data,
            forma_pagamento,
            parcelas
        )
    )

    conexao.commit()
    conexao.close()

    flash('Lançamento cadastrado com sucesso.', 'sucesso')
    return redirect(url_for('lancamentos.lancamentos'))


@lancamentos_bp.route('/lancamentos/editar/<int:lancamento_id>', methods=['POST'])
@login_obrigatorio
def editar_lancamento(lancamento_id):
    usuario_id = session.get('usuario_id')
    tipo = request.form.get('tipo', '').strip()
    descricao = request.form.get('descricao', '').strip()
    valor = converter_valor(request.form.get('valor', ''))
    data = request.form.get('data', '').strip()
    categoria_id = request.form.get('categoria_id', '').strip()
    subcategoria_id = request.form.get('subcategoria_id', '').strip()
    forma_pagamento = request.form.get('forma_pagamento', 'Não informado').strip()
    parcelas = converter_inteiro(request.form.get('parcelas', '1')) or 1

    if tipo not in ['receita', 'despesa'] or not descricao or valor is None or not data or not categoria_id:
        flash('Preencha os dados do lançamento.', 'erro')
        return redirect(url_for('lancamentos.lancamentos'))

    if not validar_data(data):
        flash('Data inválida.', 'erro')
        return redirect(url_for('lancamentos.lancamentos'))

    valido, mensagem = validar_lancamento(usuario_id, tipo, categoria_id, subcategoria_id)

    if not valido:
        flash(mensagem, 'erro')
        return redirect(url_for('lancamentos.lancamentos'))

    if subcategoria_id == '':
        subcategoria_id = None

    if not forma_pagamento:
        forma_pagamento = 'Não informado'

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE lancamentos
        SET categoria_id = ?,
            subcategoria_id = ?,
            tipo = ?,
            descricao = ?,
            valor = ?,
            data = ?,
            forma_pagamento = ?,
            parcelas = ?
        WHERE id = ?
        AND usuario_id = ?
        AND ativo = 1
        ''',
        (
            categoria_id,
            subcategoria_id,
            tipo,
            descricao,
            valor,
            data,
            forma_pagamento,
            parcelas,
            lancamento_id,
            usuario_id
        )
    )

    conexao.commit()
    conexao.close()

    flash('Lançamento atualizado com sucesso.', 'sucesso')
    return redirect(url_for('lancamentos.lancamentos'))


@lancamentos_bp.route('/lancamentos/excluir/<int:lancamento_id>')
@login_obrigatorio
def excluir_lancamento(lancamento_id):
    usuario_id = session.get('usuario_id')

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE lancamentos
        SET ativo = 0
        WHERE id = ?
        AND usuario_id = ?
        ''',
        (lancamento_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Lançamento desativado com sucesso.', 'sucesso')
    return redirect(url_for('lancamentos.lancamentos'))
