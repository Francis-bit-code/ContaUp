import sqlite3
from datetime import datetime

# banco
conexao = sqlite3.connect("banco.db")
cursor = conexao.cursor()

# tabela
cursor.execute("""
    CREATE TABLE IF NOT EXISTS receitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        valor REAL NOT NULL,
        categoria TEXT NOT NULL,
        data TEXT
    )
""")

conexao.commit()


# valida valor
def validar_valor():
    while True:
        try:
            valor = float(input("Digite o valor da receita: "))
            if valor <= 0:
                print("Valor inválido!")
                continue
            return valor
        except ValueError:
            print("Digite um número válido!")


# valida data
def validar_data():
    while True:
        data = input("Digite a data (dd/mm/aaaa): ")
        try:
            datetime.strptime(data, "%d/%m/%Y")
            return data
        except ValueError:
            print("Data inválida!")


# cadastrar receita
def cadastrar_receita():
    print("\n=== CADASTRO ===")

    valor = validar_valor()

    categoria = input("Categoria: ").strip()
    while categoria == "":
        print("Obrigatório!")
        categoria = input("Categoria: ").strip()

    data = validar_data()

    cursor.execute(
        "INSERT INTO receitas (valor, categoria, data) VALUES (?, ?, ?)",
        (valor, categoria, data)
    )

    conexao.commit()

    print("Receita salva!")


# listar receitas
def relatorio_receitas():
    cursor.execute("SELECT * FROM receitas")
    linhas = cursor.fetchall()

    print("\n=== RECEITAS ===")
    print(f"{'ID':<5} {'VALOR':<12} {'CATEGORIA':<20} {'DATA'}")

    if not linhas:
        print("Vazio")
        return

    for linha in linhas:
        print(f"{linha[0]:<5} R$ {linha[1]:<10.2f} {linha[2]:<20} {linha[3]}")

# tabela de despesa
cursor.execute("""
    CREATE TABLE IF NOT EXISTS despesas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        valor REAL NOT NULL,
        categoria TEXT NOT NULL,
        data TEXT
    )
""")

conexao.commit()
# cadastrar despesa
def cadastrar_despesa():
    print("\n=== DESPESA ===")

    valor = validar_valor()

    categoria = input("Categoria: ").strip()
    while categoria == "":
        print("Obrigatório!")
        categoria = input("Categoria: ").strip()

    data = validar_data()

    cursor.execute(
        "INSERT INTO despesas (valor, categoria, data) VALUES (?, ?, ?)",
        (valor, categoria, data)
    )

    conexao.commit()

    print("Despesa salva!")

# relatorio das despesass
def relatorio_despesas():
    cursor.execute("SELECT * FROM despesas")
    linhas = cursor.fetchall()

    print("\n=== DESPESAS ===")
    print(f"{'ID':<5} {'VALOR':<12} {'CATEGORIA':<20} {'DATA'}")

    if not linhas:
        print("Vazio")
        return

    for linha in linhas:
        print(f"{linha[0]:<5} R$ {linha[1]:<10.2f} {linha[2]:<20} {linha[3]}")


# calcular saldo
def mostrar_saldo():

    # soma receitas
    cursor.execute("SELECT SUM(valor) FROM receitas")
    total_receitas = cursor.fetchone()[0]

    # soma despesas
    cursor.execute("SELECT SUM(valor) FROM despesas")
    total_despesas = cursor.fetchone()[0]

    # evita erro se tabela estiver vazia
    if total_receitas is None:
        total_receitas = 0

    if total_despesas is None:
        total_despesas = 0

    saldo = total_receitas - total_despesas

    print("\n=== SALDO ===")
    print(f"Total receitas: R$ {total_receitas:.2f}")
    print(f"Total despesas: R$ {total_despesas:.2f}")
    print(f"Saldo atual:    R$ {saldo:.2f}")

# menu
while True:
    print("1 - Cadastrar receita")
    print("2 - Listar receitas")
    print("3 - Cadastrar despesa")
    print("4 - Listar despesas")
    print("5 - Mostrar Saldo")
    print("6 - Sair")

    try:
        opcao = int(input("Escolha: "))
    except ValueError:
        print("Inválido")
        continue

    if opcao == 1:
        cadastrar_receita()

    elif opcao == 2:
        relatorio_receitas()

    elif opcao == 3:
        cadastrar_despesa()

    elif opcao == 4:
        relatorio_despesas()

    elif opcao == 5:
        mostrar_saldo()
    elif opcao == 6:
        break

conexao.close()
