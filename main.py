import sqlite3

# CONTROLE DO SISTEMA
sistema_ativo = True
usuario_logado = None

# MENU LOGIN / CADASTRO
def menu_login():
    print("=== CONTAUP ===")
    print("1 - Login")
    print("2 - Cadastro")
    print("0 - Sair")

    return input("Escolha uma opção: ")

# MENU PRINCIPAL
def menu_principal():
    print("=== MENU PRINCIPAL ===")
    print("1 - Receitas")
    print("2 - Despesas")
    print("3 - Ver saldo")
    print("4 - Logout")
    print("0 - Sair")

    return input("Escolha uma opção: ")

# MENU RECEITAS
def menu_receitas():
    print("=== RECEITAS ===")
    print("1 - Adicionar receita")
    print("2 - Listar receitas")
    print("3 - Total de receitas")
    print("0 - Voltar")

    return input("Escolha uma opção: ")

# MENU DESPESAS
def menu_despesas():
    print("=== DESPESAS ===")
    print("1 - Adicionar despesa")
    print("2 - Listar despesas")
    print("3 - Total de despesas")
    print("0 - Voltar")

    return input("Escolha uma opção: ")


# LOOP PRINCIPAL DO SISTEMA
while sistema_ativo:

    if usuario_logado is None:
        opcao = menu_login()

        if opcao == "1":
            print("Fazer login aqui (SQLite depois)")
            usuario_logado = "teste" # simulação


        elif opcao == "2":
            print("Cadastro aqui (SQLite depois)")

        elif opcao == "0":
            sistema_ativo = False

    else:
        opcao = menu_principal()

        if opcao == "1":
            # RECEITAS

            subopcao = menu_receitas()

            if subopcao == "1":
                print("Adicionar receita (SQLite depois)")

            elif subopcao == "2":
                print("Listar receitas (SQLite depois)")

            elif subopcao == "3":
                print("Total de receitas (SQLite depois)")

        elif opcao == "2":
            print("Despesas (mesma ideia das receitas)")

        elif opcao == "3":
            print("Calcular saldo (receitas - despesas)")

        elif opcao == "4":
            usuario_logado = None
            print("Logout realizado")

        elif opcao == "0":
            sistema_ativo = False


print("Sistema encerrado")
