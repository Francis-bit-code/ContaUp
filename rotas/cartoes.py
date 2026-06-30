from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from database import (
    conectar,
    listar_cartoes,
    buscar_cartao,
    listar_compras_cartao,
    listar_categorias,
    listar_subcategorias,
    buscar_categoria
)
from funcoes import converter_valor, converter_inteiro, validar_data, calcular_totais_cartao, data_atual
from rotas.auth import login_obrigatorio


cartoes_bp = Blueprint('cartoes', __name__)


@cartoes_bp.route('/cartoes')
@login_obrigatorio
def cartoes():
    usuario_id = session.get('usuario_id')
    cartoes_lista = listar_cartoes(usuario_id)

    total_pendente = 0
    total_parcelas_ativas = 0

    for cartao in cartoes_lista:
        compras = listar_compras_cartao(usuario_id, cartao['id'])
        totais = calcular_totais_cartao(compras)
        total_pendente += totais['total_pendente']
        total_parcelas_ativas += totais['total_parcelas_ativas']

    return render_template(
        'cartoes.html',
        cartoes=cartoes_lista,
        total_pendente=total_pendente,
        total_parcelas_ativas=total_parcelas_ativas
    )


@cartoes_bp.route('/cartoes/novo', methods=['POST'])
@login_obrigatorio
def novo_cartao():
    usuario_id = session.get('usuario_id')
    nome = request.form.get('nome', '').strip()
    banco = request.form.get('banco', '').strip()
    limite_total = converter_valor(request.form.get('limite_total', '')) or 0
    dia_fechamento = converter_inteiro(request.form.get('dia_fechamento', ''))
    dia_vencimento = converter_inteiro(request.form.get('dia_vencimento', ''))

    if not nome:
        flash('Informe o nome do cartão.', 'erro')
        return redirect(url_for('cartoes.cartoes'))

    if dia_fechamento and dia_fechamento > 31:
        flash('Dia de fechamento inválido.', 'erro')
        return redirect(url_for('cartoes.cartoes'))

    if dia_vencimento and dia_vencimento > 31:
        flash('Dia de vencimento inválido.', 'erro')
        return redirect(url_for('cartoes.cartoes'))

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        INSERT INTO cartoes (
            usuario_id,
            nome,
            banco,
            limite_total,
            dia_fechamento,
            dia_vencimento
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (usuario_id, nome, banco, limite_total, dia_fechamento, dia_vencimento)
    )

    conexao.commit()
    conexao.close()

    flash('Cartão cadastrado com sucesso.', 'sucesso')
    return redirect(url_for('cartoes.cartoes'))


@cartoes_bp.route('/cartoes/editar/<int:cartao_id>', methods=['POST'])
@login_obrigatorio
def editar_cartao(cartao_id):
    usuario_id = session.get('usuario_id')
    nome = request.form.get('nome', '').strip()
    banco = request.form.get('banco', '').strip()
    limite_total = converter_valor(request.form.get('limite_total', '')) or 0
    dia_fechamento = converter_inteiro(request.form.get('dia_fechamento', ''))
    dia_vencimento = converter_inteiro(request.form.get('dia_vencimento', ''))

    if not nome:
        flash('Informe o nome do cartão.', 'erro')
        return redirect(url_for('cartoes.cartoes'))

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE cartoes
        SET nome = ?,
            banco = ?,
            limite_total = ?,
            dia_fechamento = ?,
            dia_vencimento = ?
        WHERE id = ?
        AND usuario_id = ?
        AND ativo = 1
        ''',
        (nome, banco, limite_total, dia_fechamento, dia_vencimento, cartao_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Cartão atualizado com sucesso.', 'sucesso')
    return redirect(url_for('cartoes.cartoes'))


@cartoes_bp.route('/cartoes/excluir/<int:cartao_id>')
@login_obrigatorio
def excluir_cartao(cartao_id):
    usuario_id = session.get('usuario_id')

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE cartoes
        SET ativo = 0
        WHERE id = ?
        AND usuario_id = ?
        ''',
        (cartao_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Cartão desativado com sucesso.', 'sucesso')
    return redirect(url_for('cartoes.cartoes'))


@cartoes_bp.route('/cartoes/<int:cartao_id>')
@login_obrigatorio
def detalhe_cartao(cartao_id):
    usuario_id = session.get('usuario_id')
    cartao = buscar_cartao(usuario_id, cartao_id)

    if not cartao:
        flash('Cartão não encontrado.', 'erro')
        return redirect(url_for('cartoes.cartoes'))

    compras = listar_compras_cartao(usuario_id, cartao_id)
    totais = calcular_totais_cartao(compras)

    return render_template(
        'cartao_detalhe.html',
        cartao=cartao,
        compras=totais['compras'],
        total_parcelas_ativas=totais['total_parcelas_ativas'],
        total_pendente=totais['total_pendente'],
        categorias=listar_categorias(usuario_id, 'despesa'),
        subcategorias=listar_subcategorias(usuario_id),
        data_padrao=data_atual()
    )


def validar_categoria_compra(usuario_id, categoria_id, subcategoria_id):
    if not categoria_id:
        return True, ''

    categoria = buscar_categoria(usuario_id, categoria_id)

    if not categoria:
        return False, 'Categoria não encontrada.'

    if categoria['tipo'] != 'despesa':
        return False, 'Compras de cartão precisam usar categoria de despesa.'

    if categoria['usa_subcategorias'] == 1 and not subcategoria_id:
        return False, 'Essa categoria precisa de uma subcategoria.'

    return True, ''


@cartoes_bp.route('/cartoes/<int:cartao_id>/compras/nova', methods=['POST'])
@login_obrigatorio
def nova_compra_cartao(cartao_id):
    usuario_id = session.get('usuario_id')
    cartao = buscar_cartao(usuario_id, cartao_id)

    if not cartao:
        flash('Cartão não encontrado.', 'erro')
        return redirect(url_for('cartoes.cartoes'))

    descricao = request.form.get('descricao', '').strip()
    valor_total = converter_valor(request.form.get('valor_total', ''))
    data_compra = request.form.get('data_compra', '').strip()
    parcelas_total = converter_inteiro(request.form.get('parcelas_total', ''))
    categoria_id = request.form.get('categoria_id', '').strip()
    subcategoria_id = request.form.get('subcategoria_id', '').strip()

    if not descricao or valor_total is None or not data_compra or parcelas_total is None:
        flash('Preencha descrição, valor, data e parcelas.', 'erro')
        return redirect(url_for('cartoes.detalhe_cartao', cartao_id=cartao_id))

    if not validar_data(data_compra):
        flash('Data da compra inválida.', 'erro')
        return redirect(url_for('cartoes.detalhe_cartao', cartao_id=cartao_id))

    valido, mensagem = validar_categoria_compra(usuario_id, categoria_id, subcategoria_id)

    if not valido:
        flash(mensagem, 'erro')
        return redirect(url_for('cartoes.detalhe_cartao', cartao_id=cartao_id))

    if categoria_id == '':
        categoria_id = None

    if subcategoria_id == '':
        subcategoria_id = None

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        INSERT INTO compras_cartao (
            usuario_id,
            cartao_id,
            descricao,
            valor_total,
            data_compra,
            parcelas_total,
            categoria_id,
            subcategoria_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            usuario_id,
            cartao_id,
            descricao,
            valor_total,
            data_compra,
            parcelas_total,
            categoria_id,
            subcategoria_id
        )
    )

    conexao.commit()
    conexao.close()

    flash('Dívida do cartão cadastrada com sucesso.', 'sucesso')
    return redirect(url_for('cartoes.detalhe_cartao', cartao_id=cartao_id))


@cartoes_bp.route('/cartoes/<int:cartao_id>/compras/editar/<int:compra_id>', methods=['POST'])
@login_obrigatorio
def editar_compra_cartao(cartao_id, compra_id):
    usuario_id = session.get('usuario_id')
    descricao = request.form.get('descricao', '').strip()
    valor_total = converter_valor(request.form.get('valor_total', ''))
    data_compra = request.form.get('data_compra', '').strip()
    parcelas_total = converter_inteiro(request.form.get('parcelas_total', ''))
    categoria_id = request.form.get('categoria_id', '').strip()
    subcategoria_id = request.form.get('subcategoria_id', '').strip()

    if not descricao or valor_total is None or not data_compra or parcelas_total is None:
        flash('Preencha os dados da compra.', 'erro')
        return redirect(url_for('cartoes.detalhe_cartao', cartao_id=cartao_id))

    if not validar_data(data_compra):
        flash('Data inválida.', 'erro')
        return redirect(url_for('cartoes.detalhe_cartao', cartao_id=cartao_id))

    valido, mensagem = validar_categoria_compra(usuario_id, categoria_id, subcategoria_id)

    if not valido:
        flash(mensagem, 'erro')
        return redirect(url_for('cartoes.detalhe_cartao', cartao_id=cartao_id))

    if categoria_id == '':
        categoria_id = None

    if subcategoria_id == '':
        subcategoria_id = None

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE compras_cartao
        SET descricao = ?,
            valor_total = ?,
            data_compra = ?,
            parcelas_total = ?,
            categoria_id = ?,
            subcategoria_id = ?
        WHERE id = ?
        AND cartao_id = ?
        AND usuario_id = ?
        AND ativo = 1
        ''',
        (
            descricao,
            valor_total,
            data_compra,
            parcelas_total,
            categoria_id,
            subcategoria_id,
            compra_id,
            cartao_id,
            usuario_id
        )
    )

    conexao.commit()
    conexao.close()

    flash('Compra atualizada com sucesso.', 'sucesso')
    return redirect(url_for('cartoes.detalhe_cartao', cartao_id=cartao_id))


@cartoes_bp.route('/cartoes/<int:cartao_id>/compras/excluir/<int:compra_id>')
@login_obrigatorio
def excluir_compra_cartao(cartao_id, compra_id):
    usuario_id = session.get('usuario_id')

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE compras_cartao
        SET ativo = 0
        WHERE id = ?
        AND cartao_id = ?
        AND usuario_id = ?
        ''',
        (compra_id, cartao_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Compra desativada com sucesso.', 'sucesso')
    return redirect(url_for('cartoes.detalhe_cartao', cartao_id=cartao_id))
