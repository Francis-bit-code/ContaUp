import sqlite3
from datetime import datetime

# conexão com banco
conexao = sqlite3.connect("banco.db")
cursor = conexao.cursor()

# tabela receitas
cursor.execute("""
    CREATE TABLE IF NOT EXISTS receitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        valor REAL NOT NULL,
        categoria TEXT NOT NULL,
        data TEXT
    )
""")

# tabela despesas
cursor.execute("""
    CREATE TABLE IF NOT EXISTS despesas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        valor REAL NOT NULL,
        categoria TEXT NOT NULL,
        data TEXT
    )
""")

conexao.commit()


# validar valor
def validar_valor():

    while True:

        try:
            valor = float(input("Digite o valor: "))

            if valor <= 0:
                print("Valor inválido!")
                continue

            return valor

        except ValueError:
            print("Digite um número válido!")


# validar data
def validar_data():

    while True:

        data = input("Digite a data (dd/mm/aaaa): ")

        try:
            datetime.strptime(data, "%d/%m/%Y")
            return data

        except ValueError:
            print("Data inválida!")


# validar categoria
def validar_categoria():

    while True:

        categoria = input("Categoria: ").strip()

        if categoria == "":
            print("Campo obrigatório!")

        else:
            return categoria


# cadastrar receita
def cadastrar_receita():

    print("\n=== CADASTRAR RECEITA ===")

    valor = validar_valor()
    categoria = validar_categoria()
    data = validar_data()

    cursor.execute(
        "INSERT INTO receitas (valor, categoria, data) VALUES (?, ?, ?)",
        (valor, categoria, data)
    )

    conexao.commit()

    print("Receita cadastrada!")


# cadastrar despesa
def cadastrar_despesa():

    print("\n=== CADASTRAR DESPESA ===")

    valor = validar_valor()
    categoria = validar_categoria()
    data = validar_data()

    cursor.execute(
        "INSERT INTO despesas (valor, categoria, data) VALUES (?, ?, ?)",
        (valor, categoria, data)
    )

    conexao.commit()

    print("Despesa cadastrada!")


# listar receitas
def relatorio_receitas():

    cursor.execute("SELECT * FROM receitas")

    linhas = cursor.fetchall()

    print("\n=== RECEITAS ===")

    print(f"{'ID':<5} {'VALOR':<12} {'CATEGORIA':<20} {'DATA'}")

    if not linhas:
        print("Nenhuma receita cadastrada!")
        return

    for linha in linhas:
        print(f"{linha[0]:<5} R$ {linha[1]:<10.2f} {linha[2]:<20} {linha[3]}")


# listar despesas
def relatorio_despesas():

    cursor.execute("SELECT * FROM despesas")

    linhas = cursor.fetchall()

    print("\n=== DESPESAS ===")

    print(f"{'ID':<5} {'VALOR':<12} {'CATEGORIA':<20} {'DATA'}")

    if not linhas:
        print("Nenhuma despesa cadastrada!")
        return

    for linha in linhas:
        print(f"{linha[0]:<5} R$ {linha[1]:<10.2f} {linha[2]:<20} {linha[3]}")


# mostrar saldo
def mostrar_saldo():

    cursor.execute("SELECT SUM(valor) FROM receitas")
    total_receitas = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(valor) FROM despesas")
    total_despesas = cursor.fetchone()[0]

    if total_receitas is None:
        total_receitas = 0

    if total_despesas is None:
        total_despesas = 0

    saldo = total_receitas - total_despesas

    print("\n=== SALDO ===")

    print(f"Total receitas: R$ {total_receitas:.2f}")
    print(f"Total despesas: R$ {total_despesas:.2f}")
    print(f"Saldo atual:    R$ {saldo:.2f}")


# editar receita
def editar_receita():

    print("\n=== EDITAR RECEITA ===")

    relatorio_receitas()

    try:
        id_receita = int(input("\nDigite o ID da receita: "))

    except ValueError:
        print("ID inválido!")
        return

    cursor.execute(
        "SELECT * FROM receitas WHERE id = ?",
        (id_receita,)
    )

    receita = cursor.fetchone()

    if receita is None:
        print("Receita não encontrada!")
        return

    print("\n=== DADOS ATUAIS ===")

    print(f"Valor: {receita[1]}")
    print(f"Categoria: {receita[2]}")
    print(f"Data: {receita[3]}")

    novo_valor = input("Novo valor: ")
    nova_categoria = input("Nova categoria: ")
    nova_data = input("Nova data: ")

    valor = receita[1]
    categoria = receita[2]
    data = receita[3]

    if novo_valor != "":

        try:
            valor = float(novo_valor)

        except ValueError:
            print("Valor inválido!")
            return

    if nova_categoria != "":
        categoria = nova_categoria

    if nova_data != "":

        try:
            datetime.strptime(nova_data, "%d/%m/%Y")
            data = nova_data

        except ValueError:
            print("Data inválida!")
            return

    cursor.execute("""
        UPDATE receitas
        SET valor = ?, categoria = ?, data = ?
        WHERE id = ?
    """, (valor, categoria, data, id_receita))

    conexao.commit()

    print("Receita atualizada!")


# editar despesa
def editar_despesa():

    print("\n=== EDITAR DESPESA ===")

    relatorio_despesas()

    try:
        id_despesa = int(input("\nDigite o ID da despesa: "))

    except ValueError:
        print("ID inválido!")
        return

    cursor.execute(
        "SELECT * FROM despesas WHERE id = ?",
        (id_despesa,)
    )

    despesa = cursor.fetchone()

    if despesa is None:
        print("Despesa não encontrada!")
        return

    print("\n=== DADOS ATUAIS ===")

    print(f"Valor: {despesa[1]}")
    print(f"Categoria: {despesa[2]}")
    print(f"Data: {despesa[3]}")

    novo_valor = input("Novo valor: ")
    nova_categoria = input("Nova categoria: ")
    nova_data = input("Nova data: ")

    valor = despesa[1]
    categoria = despesa[2]
    data = despesa[3]

    if novo_valor != "":

        try:
            valor = float(novo_valor)

        except ValueError:
            print("Valor inválido!")
            return

    if nova_categoria != "":
        categoria = nova_categoria

    if nova_data != "":

        try:
            datetime.strptime(nova_data, "%d/%m/%Y")
            data = nova_data

        except ValueError:
            print("Data inválida!")
            return

    cursor.execute("""
        UPDATE despesas
        SET valor = ?, categoria = ?, data = ?
        WHERE id = ?
    """, (valor, categoria, data, id_despesa))

    conexao.commit()

    print("Despesa atualizada!")


# deletar receita
def deletar_receita():

    print("\n=== DELETAR RECEITA ===")

    relatorio_receitas()

    try:
        id_receita = int(input("\nDigite o ID da receita: "))

    except ValueError:
        print("ID inválido!")
        return

    cursor.execute(
        "SELECT * FROM receitas WHERE id = ?",
        (id_receita,)
    )

    receita = cursor.fetchone()

    if receita is None:
        print("Receita não encontrada!")
        return

    confirmar = input("Deseja realmente excluir? (s/n): ").lower()

    if confirmar == "s":

        cursor.execute(
            "DELETE FROM receitas WHERE id = ?",
            (id_receita,)
        )

        conexao.commit()

        print("Receita excluída!")

    else:
        print("Operação cancelada!")


# deletar despesa
def deletar_despesa():

    print("\n=== DELETAR DESPESA ===")

    relatorio_despesas()

    try:
        id_despesa = int(input("\nDigite o ID da despesa: "))

    except ValueError:
        print("ID inválido!")
        return

    cursor.execute(
        "SELECT * FROM despesas WHERE id = ?",
        (id_despesa,)
    )

    despesa = cursor.fetchone()

    if despesa is None:
        print("Despesa não encontrada!")
        return

    confirmar = input("Deseja realmente excluir? (s/n): ").lower()

    if confirmar == "s":

        cursor.execute(
            "DELETE FROM despesas WHERE id = ?",
            (id_despesa,)
        )

        conexao.commit()

        print("Despesa excluída!")

    else:
        print("Operação cancelada!")


# menu principal
while True:

    print("\n===== CONTROLE FINANCEIRO =====")

    print("1 - Cadastrar receita")
    print("2 - Listar receitas")
    print("3 - Editar receita")
    print("4 - Deletar receita")

    print("5 - Cadastrar despesa")
    print("6 - Listar despesas")
    print("7 - Editar despesa")
    print("8 - Deletar despesa")

    print("9 - Mostrar saldo")
    print("10 - Sair")

    try:
        opcao = int(input("\nEscolha: "))

    except ValueError:
        print("Digite um número válido!")
        continue

    if opcao == 1:
        cadastrar_receita()

    elif opcao == 2:
        relatorio_receitas()

    elif opcao == 3:
        editar_receita()

    elif opcao == 4:
        deletar_receita()

    elif opcao == 5:
        cadastrar_despesa()

    elif opcao == 6:
        relatorio_despesas()

    elif opcao == 7:
        editar_despesa()

    elif opcao == 8:
        deletar_despesa()

    elif opcao == 9:
        mostrar_saldo()

    elif opcao == 10:
        print("Sistema encerrado!")
        break

    else:
        print("Opção inválida!")


conexao.close()
