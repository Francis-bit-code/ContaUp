from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

from database import buscar_usuario_por_email, cadastrar_usuario


auth_bp = Blueprint('auth', __name__)


def usuario_logado():
    return session.get('usuario_id')


def login_obrigatorio(funcao):
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        if not usuario_logado():
            flash('Faça login para acessar o sistema.', 'aviso')
            return redirect(url_for('auth.login'))

        return funcao(*args, **kwargs)

    return wrapper


@auth_bp.route('/')
def index():
    if usuario_logado():
        return redirect(url_for('dashboard.dashboard'))

    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '').strip()

        if not email or not senha:
            flash('Preencha e-mail e senha.', 'erro')
            return redirect(url_for('auth.login'))

        usuario = buscar_usuario_por_email(email)

        if usuario and check_password_hash(usuario['senha'], senha):
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['nome']
            nome_usuario = usuario['nome']
            flash(f'Bem-vindo, {nome_usuario}!', 'sucesso')
            return redirect(url_for('dashboard.dashboard'))

        flash('E-mail ou senha incorretos.', 'erro')
        return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '').strip()
        confirmar = request.form.get('confirmar', '').strip()

        if not nome or not email or not senha or not confirmar:
            flash('Preencha todos os campos.', 'erro')
            return redirect(url_for('auth.cadastro'))

        if len(senha) < 4:
            flash('A senha precisa ter pelo menos 4 caracteres.', 'erro')
            return redirect(url_for('auth.cadastro'))

        if senha != confirmar:
            flash('As senhas não conferem.', 'erro')
            return redirect(url_for('auth.cadastro'))

        usuario_existente = buscar_usuario_por_email(email)

        if usuario_existente:
            flash('Este e-mail já está cadastrado.', 'erro')
            return redirect(url_for('auth.cadastro'))

        cadastrar_usuario(nome, email, senha)
        flash('Conta criada com sucesso. Agora faça login.', 'sucesso')
        return redirect(url_for('auth.login'))

    return render_template('cadastro.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'sucesso')
    return redirect(url_for('auth.login'))
