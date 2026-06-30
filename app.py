from flask import Flask

from database import inicializar_banco, criar_usuario_padrao, criar_categorias_padrao_para_todos
from funcoes import formatar_moeda
from rotas.auth import auth_bp
from rotas.dashboard import dashboard_bp
from rotas.categorias import categorias_bp
from rotas.lancamentos import lancamentos_bp
from rotas.cartoes import cartoes_bp
from rotas.gastos_fixos import gastos_fixos_bp
from rotas.planejamento import planejamento_bp
from rotas.renda_extra import renda_extra_bp
from rotas.renda_fixa import renda_fixa_bp
from rotas.relatorios import relatorios_bp


app = Flask(__name__)
app.config['SECRET_KEY'] = 'contaup-chave-dev'


inicializar_banco()
criar_usuario_padrao()
criar_categorias_padrao_para_todos()


@app.context_processor
def funcoes_globais():
    return {
        'formatar_moeda': formatar_moeda
    }


app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(categorias_bp)
app.register_blueprint(lancamentos_bp)
app.register_blueprint(cartoes_bp)
app.register_blueprint(gastos_fixos_bp)
app.register_blueprint(planejamento_bp)
app.register_blueprint(renda_extra_bp)
app.register_blueprint(renda_fixa_bp)
app.register_blueprint(relatorios_bp)


if __name__ == '__main__':
    app.run(debug=True)
