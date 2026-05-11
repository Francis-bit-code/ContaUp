import database
from receitas import cadastrar_receita, relatorio_receitas, editar_receita, deletar_receita
from despesas import cadastrar_despesa, relatorio_despesas, editar_despesa, deletar_despesa
from relatorios import mostrar_saldo, relatorio_geral
from backup import exportar_backup, importar_backup


def exibir_menu():
    print("\n========== ContaUP ==========")
    print("--- RECEITAS ---")
    print("  1 - Cadastrar receita")
    print("  2 - Listar receitas")
    print("  3 - Editar receita")
    print("  4 - Deletar receita")
    print("--- DESPESAS ---")
    print("  5 - Cadastrar despesa")
    print("  6 - Listar despesas")
    print("  7 - Editar despesa")
    print("  8 - Deletar despesa")
    print("--- RELATORIOS ---")
    print("  9 - Mostrar saldo")
    print(" 10 - Relatorio geral")
    print("--- BACKUP ---")
    print(" 11 - Exportar backup")
    print(" 12 - Importar backup")
    print("  0 - Sair")
    print("=" * 30)


def main():
    database.inicializar_banco()
    print("Bem-vindo ao ContaUP!")

    while True:
        exibir_menu()
        try:
            opcao = int(input("Escolha uma opcao: "))
        except ValueError:
            print("Digite um numero valido!")
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
            relatorio_geral()
        elif opcao == 11:
            exportar_backup()
        elif opcao == 12:
            importar_backup()
        elif opcao == 0:
            print("Sistema encerrado. Ate logo!")
            break
        else:
            print("Opcao invalida!")

    database.fechar_banco()


if __name__ == "__main__":
    main()