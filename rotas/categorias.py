from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from database import conectar, listar_categorias, listar_subcategorias, buscar_categoria
from rotas.auth import login_obrigatorio


categorias_bp = Blueprint('categorias', __name__)


@categorias_bp.route('/categorias')
@login_obrigatorio
def categorias():
    usuario_id = session.get('usuario_id')
    categorias_lista = listar_categorias(usuario_id)
    subcategorias_lista = listar_subcategorias(usuario_id)

    return render_template(
        'categorias.html',
        categorias=categorias_lista,
        subcategorias=subcategorias_lista
    )


@categorias_bp.route('/categorias/nova', methods=['POST'])
@login_obrigatorio
def nova_categoria():
    usuario_id = session.get('usuario_id')
    nome = request.form.get('nome', '').strip()
    tipo = request.form.get('tipo', '').strip()
    usa_subcategorias = request.form.get('usa_subcategorias', '0').strip()

    if not nome or tipo not in ['receita', 'despesa']:
        flash('Preencha o nome e o tipo da categoria.', 'erro')
        return redirect(url_for('categorias.categorias'))

    if usa_subcategorias not in ['0', '1']:
        usa_subcategorias = '0'

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT id
        FROM categorias
        WHERE usuario_id = ?
        AND lower(nome) = lower(?)
        AND tipo = ?
        AND ativo = 1
        ''',
        (usuario_id, nome, tipo)
    )

    categoria_existente = cursor.fetchone()

    if categoria_existente:
        conexao.close()
        flash('Essa categoria já existe.', 'erro')
        return redirect(url_for('categorias.categorias'))

    cursor.execute(
        '''
        INSERT INTO categorias (
            usuario_id,
            nome,
            tipo,
            usa_subcategorias
        )
        VALUES (?, ?, ?, ?)
        ''',
        (usuario_id, nome, tipo, int(usa_subcategorias))
    )

    conexao.commit()
    conexao.close()

    flash('Categoria cadastrada com sucesso.', 'sucesso')
    return redirect(url_for('categorias.categorias'))


@categorias_bp.route('/categorias/editar/<int:categoria_id>', methods=['POST'])
@login_obrigatorio
def editar_categoria(categoria_id):
    usuario_id = session.get('usuario_id')
    nome = request.form.get('nome', '').strip()
    tipo = request.form.get('tipo', '').strip()
    usa_subcategorias = request.form.get('usa_subcategorias', '0').strip()

    if not nome or tipo not in ['receita', 'despesa']:
        flash('Preencha o nome e o tipo da categoria.', 'erro')
        return redirect(url_for('categorias.categorias'))

    if usa_subcategorias not in ['0', '1']:
        usa_subcategorias = '0'

    categoria = buscar_categoria(usuario_id, categoria_id)

    if not categoria:
        flash('Categoria não encontrada.', 'erro')
        return redirect(url_for('categorias.categorias'))

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE categorias
        SET nome = ?,
            tipo = ?,
            usa_subcategorias = ?
        WHERE id = ?
        AND usuario_id = ?
        ''',
        (nome, tipo, int(usa_subcategorias), categoria_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Categoria atualizada com sucesso.', 'sucesso')
    return redirect(url_for('categorias.categorias'))


@categorias_bp.route('/categorias/excluir/<int:categoria_id>')
@login_obrigatorio
def excluir_categoria(categoria_id):
    usuario_id = session.get('usuario_id')

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE categorias
        SET ativo = 0
        WHERE id = ?
        AND usuario_id = ?
        ''',
        (categoria_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Categoria desativada com sucesso.', 'sucesso')
    return redirect(url_for('categorias.categorias'))


@categorias_bp.route('/subcategorias/nova', methods=['POST'])
@login_obrigatorio
def nova_subcategoria():
    usuario_id = session.get('usuario_id')
    categoria_id = request.form.get('categoria_id', '').strip()
    nome = request.form.get('nome', '').strip()

    if not categoria_id or not nome:
        flash('Selecione a categoria e informe o nome da subcategoria.', 'erro')
        return redirect(url_for('categorias.categorias'))

    categoria = buscar_categoria(usuario_id, categoria_id)

    if not categoria:
        flash('Categoria não encontrada.', 'erro')
        return redirect(url_for('categorias.categorias'))

    if categoria['usa_subcategorias'] != 1:
        flash('Essa categoria não está marcada para usar subcategorias.', 'erro')
        return redirect(url_for('categorias.categorias'))

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        INSERT INTO subcategorias (
            usuario_id,
            categoria_id,
            nome
        )
        VALUES (?, ?, ?)
        ''',
        (usuario_id, categoria_id, nome)
    )

    conexao.commit()
    conexao.close()

    flash('Subcategoria cadastrada com sucesso.', 'sucesso')
    return redirect(url_for('categorias.categorias'))


@categorias_bp.route('/subcategorias/editar/<int:subcategoria_id>', methods=['POST'])
@login_obrigatorio
def editar_subcategoria(subcategoria_id):
    usuario_id = session.get('usuario_id')
    categoria_id = request.form.get('categoria_id', '').strip()
    nome = request.form.get('nome', '').strip()

    if not categoria_id or not nome:
        flash('Preencha os dados da subcategoria.', 'erro')
        return redirect(url_for('categorias.categorias'))

    categoria = buscar_categoria(usuario_id, categoria_id)

    if not categoria or categoria['usa_subcategorias'] != 1:
        flash('Categoria inválida para subcategoria.', 'erro')
        return redirect(url_for('categorias.categorias'))

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE subcategorias
        SET nome = ?,
            categoria_id = ?
        WHERE id = ?
        AND usuario_id = ?
        AND ativo = 1
        ''',
        (nome, categoria_id, subcategoria_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Subcategoria atualizada com sucesso.', 'sucesso')
    return redirect(url_for('categorias.categorias'))


@categorias_bp.route('/subcategorias/excluir/<int:subcategoria_id>')
@login_obrigatorio
def excluir_subcategoria(subcategoria_id):
    usuario_id = session.get('usuario_id')

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE subcategorias
        SET ativo = 0
        WHERE id = ?
        AND usuario_id = ?
        ''',
        (subcategoria_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Subcategoria desativada com sucesso.', 'sucesso')
    return redirect(url_for('categorias.categorias'))
