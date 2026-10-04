💰 ContaUp

Sistema de gerenciamento financeiro desenvolvido como projeto acadêmico da disciplina de Algoritmos e Programação II (APII).

O ContaUp foi desenvolvido com o objetivo de colocar em prática conceitos de programação, organização de código, persistência de dados e desenvolvimento web, criando uma aplicação para auxiliar no controle das finanças pessoais.

📌 Sobre o projeto

O ContaUp permite organizar diferentes aspectos da vida financeira em um único sistema, oferecendo recursos para acompanhamento de:

💵 Receitas
💸 Despesas
💳 Cartões de crédito
📆 Parcelamentos
🧾 Gastos fixos
📊 Planejamento financeiro
📈 Relatórios
💰 Renda fixa
💼 Renda extra
🏷️ Categorias de lançamentos

O projeto também utiliza uma estrutura modular, separando as funcionalidades da aplicação em diferentes arquivos e rotas.

🛠️ Tecnologias utilizadas
Python
Flask
SQLite
HTML
CSS
JavaScript
Jinja2
Git/GitHub
🧠 Conceitos aplicados

Durante o desenvolvimento foram praticados conceitos como:

Programação em Python
Funções e modularização
Estruturas de dados
CRUD
Banco de dados SQLite
Persistência de dados
Desenvolvimento web com Flask
Templates com Jinja2
Organização de rotas utilizando Blueprints
Separação entre lógica, banco de dados e interface
📂 Estrutura do projeto
ContaUp/
│
├── rotas/
│   ├── auth.py
│   ├── dashboard.py
│   ├── categorias.py
│   ├── lancamentos.py
│   ├── cartoes.py
│   ├── gastos_fixos.py
│   ├── planejamento.py
│   ├── renda_extra.py
│   ├── renda_fixa.py
│   └── relatorios.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── imagens/
│
├── templates/
│
├── app.py
├── database.py
├── funcoes.py
├── contaup.db
└── requerimentos.txt
🚀 Como executar
1. Clone o repositório
git clone https://github.com/Francis-bit-code/ContaUp.git
2. Entre na pasta
cd ContaUp
3. Crie um ambiente virtual
python -m venv venv
4. Ative o ambiente virtual

Windows:

venv\Scripts\activate

Linux/macOS:

source venv/bin/activate
5. Instale as dependências
pip install -r requerimentos.txt
6. Execute a aplicação
python app.py

Depois, acesse:

http://127.0.0.1:5000

🎯 Objetivo acadêmico

O ContaUp foi desenvolvido como parte das atividades da disciplina de Algoritmos e Programação II, com o objetivo de aplicar na prática os conhecimentos adquiridos durante a disciplina.

O projeto também serviu como oportunidade para trabalhar conceitos de organização de software, banco de dados e desenvolvimento de aplicações web.

📚 Próximos passos

Algumas funcionalidades podem continuar sendo aprimoradas ao longo do desenvolvimento, incluindo:

Melhorias na interface
Validações adicionais
Novos relatórios
Melhorias na experiência do usuário
Novos recursos de planejamento financeiro


⭐ Projeto desenvolvido para fins acadêmicos e de aprendizado.
