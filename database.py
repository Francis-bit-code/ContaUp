import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / 'contaup.db'


def conectar():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    conexao.execute('PRAGMA foreign_keys = ON')
    return conexao


def inicializar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('receita', 'despesa')),
            usa_subcategorias INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subcategorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            categoria_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            categoria_id INTEGER NOT NULL,
            subcategoria_id INTEGER,
            tipo TEXT NOT NULL CHECK(tipo IN ('receita', 'despesa')),
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            forma_pagamento TEXT DEFAULT 'Não informado',
            parcelas INTEGER DEFAULT 1,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE CASCADE,
            FOREIGN KEY (subcategoria_id) REFERENCES subcategorias(id) ON DELETE SET NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cartoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            banco TEXT,
            limite_total REAL DEFAULT 0,
            dia_fechamento INTEGER,
            dia_vencimento INTEGER,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compras_cartao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            cartao_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            valor_total REAL NOT NULL,
            data_compra TEXT NOT NULL,
            parcelas_total INTEGER NOT NULL,
            categoria_id INTEGER,
            subcategoria_id INTEGER,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (cartao_id) REFERENCES cartoes(id) ON DELETE CASCADE,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL,
            FOREIGN KEY (subcategoria_id) REFERENCES subcategorias(id) ON DELETE SET NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos_fixos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            dia_vencimento INTEGER,
            categoria_id INTEGER,
            forma_pagamento TEXT DEFAULT 'Não informado',
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planejamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            valor_estimado REAL NOT NULL,
            data_desejada TEXT,
            prioridade TEXT DEFAULT 'Média',
            observacao TEXT,
            realizado INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rendas_fixas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo_recebimento TEXT NOT NULL CHECK(tipo_recebimento IN ('dia_mes', 'dia_util')),
            dia_recebimento INTEGER NOT NULL,
            categoria_id INTEGER,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS renda_extra (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            origem TEXT,
            objetivo TEXT DEFAULT 'Investimento',
            data TEXT NOT NULL,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relatorios_mensais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            mes TEXT NOT NULL,
            total_receitas REAL DEFAULT 0,
            total_despesas REAL DEFAULT 0,
            saldo REAL DEFAULT 0,
            total_gastos_fixos REAL DEFAULT 0,
            total_parcelas_cartao REAL DEFAULT 0,
            total_pendente_cartao REAL DEFAULT 0,
            total_renda_extra REAL DEFAULT 0,
            total_planejado REAL DEFAULT 0,
            maior_categoria TEXT,
            data_geracao TEXT NOT NULL,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    ''')

    conexao.commit()
    conexao.close()


def criar_usuario_padrao():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT id FROM usuarios
        WHERE email = ?
        ''',
        ('admin@contaup.com',)
    )

    usuario = cursor.fetchone()

    if usuario is None:
        senha = generate_password_hash('1234')

        cursor.execute(
            '''
            INSERT INTO usuarios (nome, email, senha)
            VALUES (?, ?, ?)
            ''',
            ('Administrador', 'admin@contaup.com', senha)
        )

        conexao.commit()

    conexao.close()


def buscar_usuario_por_email(email):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT * FROM usuarios
        WHERE email = ?
        ''',
        (email,)
    )

    usuario = cursor.fetchone()
    conexao.close()

    return usuario


def cadastrar_usuario(nome, email, senha):
    conexao = conectar()
    cursor = conexao.cursor()
    senha_hash = generate_password_hash(senha)

    cursor.execute(
        '''
        INSERT INTO usuarios (nome, email, senha)
        VALUES (?, ?, ?)
        ''',
        (nome, email, senha_hash)
    )

    usuario_id = cursor.lastrowid
    conexao.commit()
    conexao.close()

    criar_categorias_padrao(usuario_id)

    return usuario_id


def listar_categorias(usuario_id, tipo=None):
    conexao = conectar()
    cursor = conexao.cursor()

    if tipo:
        cursor.execute(
            '''
            SELECT * FROM categorias
            WHERE usuario_id = ?
            AND tipo = ?
            AND ativo = 1
            ORDER BY nome
            ''',
            (usuario_id, tipo)
        )
    else:
        cursor.execute(
            '''
            SELECT * FROM categorias
            WHERE usuario_id = ?
            AND ativo = 1
            ORDER BY tipo DESC, nome
            ''',
            (usuario_id,)
        )

    categorias = cursor.fetchall()
    conexao.close()

    return categorias


def buscar_categoria(usuario_id, categoria_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT * FROM categorias
        WHERE id = ?
        AND usuario_id = ?
        AND ativo = 1
        ''',
        (categoria_id, usuario_id)
    )

    categoria = cursor.fetchone()
    conexao.close()

    return categoria


def listar_subcategorias(usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT
            subcategorias.id,
            subcategorias.nome,
            subcategorias.categoria_id,
            categorias.nome AS categoria,
            categorias.tipo
        FROM subcategorias
        JOIN categorias ON categorias.id = subcategorias.categoria_id
        WHERE subcategorias.usuario_id = ?
        AND subcategorias.ativo = 1
        AND categorias.ativo = 1
        ORDER BY categorias.nome, subcategorias.nome
        ''',
        (usuario_id,)
    )

    subcategorias = cursor.fetchall()
    conexao.close()

    return subcategorias


def listar_subcategorias_por_categoria(usuario_id, categoria_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT * FROM subcategorias
        WHERE usuario_id = ?
        AND categoria_id = ?
        AND ativo = 1
        ORDER BY nome
        ''',
        (usuario_id, categoria_id)
    )

    subcategorias = cursor.fetchall()
    conexao.close()

    return subcategorias


def listar_cartoes(usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT * FROM cartoes
        WHERE usuario_id = ?
        AND ativo = 1
        ORDER BY nome
        ''',
        (usuario_id,)
    )

    cartoes = cursor.fetchall()
    conexao.close()

    return cartoes


def buscar_cartao(usuario_id, cartao_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT * FROM cartoes
        WHERE id = ?
        AND usuario_id = ?
        AND ativo = 1
        ''',
        (cartao_id, usuario_id)
    )

    cartao = cursor.fetchone()
    conexao.close()

    return cartao


def listar_compras_cartao(usuario_id, cartao_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT
            compras_cartao.*,
            categorias.nome AS categoria,
            subcategorias.nome AS subcategoria
        FROM compras_cartao
        LEFT JOIN categorias ON categorias.id = compras_cartao.categoria_id
        LEFT JOIN subcategorias ON subcategorias.id = compras_cartao.subcategoria_id
        WHERE compras_cartao.usuario_id = ?
        AND compras_cartao.cartao_id = ?
        AND compras_cartao.ativo = 1
        ORDER BY compras_cartao.data_compra DESC, compras_cartao.id DESC
        ''',
        (usuario_id, cartao_id)
    )

    compras = cursor.fetchall()
    conexao.close()

    return compras


def listar_gastos_fixos(usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT
            gastos_fixos.*,
            categorias.nome AS categoria
        FROM gastos_fixos
        LEFT JOIN categorias ON categorias.id = gastos_fixos.categoria_id
        WHERE gastos_fixos.usuario_id = ?
        AND gastos_fixos.ativo = 1
        ORDER BY gastos_fixos.dia_vencimento, gastos_fixos.descricao
        ''',
        (usuario_id,)
    )

    gastos = cursor.fetchall()
    conexao.close()

    return gastos


def listar_planejamentos(usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT * FROM planejamentos
        WHERE usuario_id = ?
        AND ativo = 1
        ORDER BY realizado, data_desejada, prioridade
        ''',
        (usuario_id,)
    )

    planejamentos = cursor.fetchall()
    conexao.close()

    return planejamentos


def listar_renda_extra(usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT * FROM renda_extra
        WHERE usuario_id = ?
        AND ativo = 1
        ORDER BY data DESC, id DESC
        ''',
        (usuario_id,)
    )

    rendas = cursor.fetchall()
    conexao.close()

    return rendas



def listar_rendas_fixas(usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT
            rendas_fixas.*,
            categorias.nome AS categoria
        FROM rendas_fixas
        LEFT JOIN categorias ON categorias.id = rendas_fixas.categoria_id
        WHERE rendas_fixas.usuario_id = ?
        AND rendas_fixas.ativo = 1
        ORDER BY rendas_fixas.descricao
        ''',
        (usuario_id,)
    )

    rendas = cursor.fetchall()
    conexao.close()

    return rendas


def buscar_categoria_salario(usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT id
        FROM categorias
        WHERE usuario_id = ?
        AND nome = 'Salário'
        AND tipo = 'receita'
        AND ativo = 1
        LIMIT 1
        ''',
        (usuario_id,)
    )

    categoria = cursor.fetchone()
    conexao.close()

    if categoria:
        return categoria['id']

    criar_categorias_padrao(usuario_id)

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT id
        FROM categorias
        WHERE usuario_id = ?
        AND nome = 'Salário'
        AND tipo = 'receita'
        AND ativo = 1
        LIMIT 1
        ''',
        (usuario_id,)
    )

    categoria = cursor.fetchone()
    conexao.close()

    if categoria:
        return categoria['id']

    return None

def obter_ou_criar_categoria_padrao(cursor, usuario_id, nome, tipo, usa_subcategorias):
    cursor.execute(
        '''
        SELECT id
        FROM categorias
        WHERE usuario_id = ?
        AND nome = ?
        AND tipo = ?
        AND ativo = 1
        LIMIT 1
        ''',
        (usuario_id, nome, tipo)
    )

    categoria = cursor.fetchone()

    if categoria:
        return categoria['id']

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
        (usuario_id, nome, tipo, usa_subcategorias)
    )

    return cursor.lastrowid


def obter_ou_criar_subcategoria_padrao(cursor, usuario_id, categoria_id, nome):
    cursor.execute(
        '''
        SELECT id
        FROM subcategorias
        WHERE usuario_id = ?
        AND categoria_id = ?
        AND nome = ?
        AND ativo = 1
        LIMIT 1
        ''',
        (usuario_id, categoria_id, nome)
    )

    subcategoria = cursor.fetchone()

    if subcategoria:
        return subcategoria['id']

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

    return cursor.lastrowid


def criar_categorias_padrao(usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()

    obter_ou_criar_categoria_padrao(cursor, usuario_id, 'Salário', 'receita', 0)
    obter_ou_criar_categoria_padrao(cursor, usuario_id, 'Pix recebido', 'receita', 0)
    obter_ou_criar_categoria_padrao(cursor, usuario_id, 'Venda', 'receita', 0)
    obter_ou_criar_categoria_padrao(cursor, usuario_id, 'Rendimento', 'receita', 0)

    alimentacao_id = obter_ou_criar_categoria_padrao(cursor, usuario_id, 'Alimentação', 'despesa', 1)

    obter_ou_criar_categoria_padrao(cursor, usuario_id, 'Moradia', 'despesa', 0)
    obter_ou_criar_categoria_padrao(cursor, usuario_id, 'Transporte', 'despesa', 0)
    obter_ou_criar_categoria_padrao(cursor, usuario_id, 'Saúde', 'despesa', 0)
    obter_ou_criar_categoria_padrao(cursor, usuario_id, 'Educação', 'despesa', 0)
    obter_ou_criar_categoria_padrao(cursor, usuario_id, 'Lazer', 'despesa', 0)
    obter_ou_criar_categoria_padrao(cursor, usuario_id, 'Gasto fixo', 'despesa', 0)
    obter_ou_criar_categoria_padrao(cursor, usuario_id, 'Cartão de crédito', 'despesa', 0)
    obter_ou_criar_categoria_padrao(cursor, usuario_id, 'Outros gastos', 'despesa', 0)

    obter_ou_criar_subcategoria_padrao(cursor, usuario_id, alimentacao_id, 'Mercado')
    obter_ou_criar_subcategoria_padrao(cursor, usuario_id, alimentacao_id, 'Lanche')
    obter_ou_criar_subcategoria_padrao(cursor, usuario_id, alimentacao_id, 'Restaurante')
    obter_ou_criar_subcategoria_padrao(cursor, usuario_id, alimentacao_id, 'Delivery')

    conexao.commit()
    conexao.close()


def criar_categorias_padrao_para_todos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        '''
        SELECT id
        FROM usuarios
        '''
    )

    usuarios = cursor.fetchall()
    conexao.close()

    for usuario in usuarios:
        criar_categorias_padrao(usuario['id'])
