from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from database import conectar, listar_categorias, listar_rendas_fixas, buscar_categoria_salario
from funcoes import (
    converter_valor,
    converter_inteiro,
    mes_atual,
    preparar_rendas_fixas_mes,
    calcular_total_rendas_fixas
)
from rotas.auth import login_obrigatorio


renda_fixa_bp = Blueprint('renda_fixa', __name__)


@renda_fixa_bp.route('/renda-fixa')
@login_obrigatorio
def renda_fixa():
    usuario_id = session.get('usuario_id')
    mes = request.args.get('mes', mes_atual())
    categorias = listar_categorias(usuario_id, 'receita')
    rendas = listar_rendas_fixas(usuario_id)
    rendas_formatadas = preparar_rendas_fixas_mes(rendas, mes)
    total_renda_fixa = calcular_total_rendas_fixas(rendas)

    return render_template(
        'renda_fixa.html',
        mes=mes,
        categorias=categorias,
        rendas=rendas_formatadas,
        total_renda_fixa=total_renda_fixa
    )


@renda_fixa_bp.route('/renda-fixa/nova', methods=['POST'])
@login_obrigatorio
def nova_renda_fixa():
    usuario_id = session.get('usuario_id')

    descricao = request.form.get('descricao', '').strip()
    valor = converter_valor(request.form.get('valor', ''))
    tipo_recebimento = request.form.get('tipo_recebimento', '').strip()
    dia_recebimento = converter_inteiro(request.form.get('dia_recebimento', ''))
    categoria_id = request.form.get('categoria_id', '').strip()

    if not descricao or valor is None or tipo_recebimento not in ['dia_mes', 'dia_util'] or dia_recebimento is None:
        flash('Preencha descrição, valor e forma de recebimento.', 'erro')
        return redirect(url_for('renda_fixa.renda_fixa'))

    if tipo_recebimento == 'dia_mes' and dia_recebimento > 31:
        flash('Para dia fixo, informe um dia entre 1 e 31.', 'erro')
        return redirect(url_for('renda_fixa.renda_fixa'))

    if tipo_recebimento == 'dia_util' and dia_recebimento > 22:
        flash('Para dia útil, informe um número entre 1 e 22.', 'erro')
        return redirect(url_for('renda_fixa.renda_fixa'))

    if categoria_id == '':
        categoria_id = buscar_categoria_salario(usuario_id)
    else:
        categoria_id = int(categoria_id)

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        INSERT INTO rendas_fixas (
            usuario_id,
            descricao,
            valor,
            tipo_recebimento,
            dia_recebimento,
            categoria_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (
            usuario_id,
            descricao,
            valor,
            tipo_recebimento,
            dia_recebimento,
            categoria_id
        )
    )

    conexao.commit()
    conexao.close()

    flash('Renda fixa cadastrada com sucesso.', 'sucesso')

    return redirect(url_for('renda_fixa.renda_fixa'))


@renda_fixa_bp.route('/renda-fixa/editar/<int:renda_id>', methods=['POST'])
@login_obrigatorio
def editar_renda_fixa(renda_id):
    usuario_id = session.get('usuario_id')

    descricao = request.form.get('descricao', '').strip()
    valor = converter_valor(request.form.get('valor', ''))
    tipo_recebimento = request.form.get('tipo_recebimento', '').strip()
    dia_recebimento = converter_inteiro(request.form.get('dia_recebimento', ''))
    categoria_id = request.form.get('categoria_id', '').strip()

    if not descricao or valor is None or tipo_recebimento not in ['dia_mes', 'dia_util'] or dia_recebimento is None:
        flash('Preencha descrição, valor e forma de recebimento.', 'erro')
        return redirect(url_for('renda_fixa.renda_fixa'))

    if tipo_recebimento == 'dia_mes' and dia_recebimento > 31:
        flash('Para dia fixo, informe um dia entre 1 e 31.', 'erro')
        return redirect(url_for('renda_fixa.renda_fixa'))

    if tipo_recebimento == 'dia_util' and dia_recebimento > 22:
        flash('Para dia útil, informe um número entre 1 e 22.', 'erro')
        return redirect(url_for('renda_fixa.renda_fixa'))

    if categoria_id == '':
        categoria_id = buscar_categoria_salario(usuario_id)
    else:
        categoria_id = int(categoria_id)

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT id
        FROM rendas_fixas
        WHERE id = ?
        AND usuario_id = ?
        AND ativo = 1
        ''',
        (renda_id, usuario_id)
    )

    renda = cursor.fetchone()

    if not renda:
        conexao.close()
        flash('Renda fixa não encontrada.', 'erro')
        return redirect(url_for('renda_fixa.renda_fixa'))

    cursor.execute(
        '''
        UPDATE rendas_fixas
        SET descricao = ?,
            valor = ?,
            tipo_recebimento = ?,
            dia_recebimento = ?,
            categoria_id = ?
        WHERE id = ?
        AND usuario_id = ?
        ''',
        (
            descricao,
            valor,
            tipo_recebimento,
            dia_recebimento,
            categoria_id,
            renda_id,
            usuario_id
        )
    )

    conexao.commit()
    conexao.close()

    flash('Renda fixa atualizada com sucesso.', 'sucesso')

    return redirect(url_for('renda_fixa.renda_fixa'))


@renda_fixa_bp.route('/renda-fixa/excluir/<int:renda_id>')
@login_obrigatorio
def excluir_renda_fixa(renda_id):
    usuario_id = session.get('usuario_id')

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        UPDATE rendas_fixas
        SET ativo = 0
        WHERE id = ?
        AND usuario_id = ?
        AND ativo = 1
        ''',
        (renda_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    flash('Renda fixa desativada com sucesso.', 'sucesso')

    return redirect(url_for('renda_fixa.renda_fixa'))
