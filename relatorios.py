import database
from receitas import listar_receitas
from despesas import listar_despesas


def mostrar_saldo():
    database.cursor.execute("SELECT SUM(valor) FROM receitas")
    total_receitas = database.cursor.fetchone()[0] or 0

    database.cursor.execute("SELECT SUM(valor) FROM despesas")
    total_despesas = database.cursor.fetchone()[0] or 0

    saldo = total_receitas - total_despesas

    print("\n=== RESUMO FINANCEIRO ===")
    print(f"Total de receitas: R$ {total_receitas:.2f}")
    print(f"Total de despesas: R$ {total_despesas:.2f}")
    print("-" * 30)

    if saldo >= 0:
        print(f"Saldo atual:       R$ {saldo:.2f} OK")
    else:
        print(f"Saldo atual:       R$ {saldo:.2f} NEGATIVO")


def relatorio_geral():
    receitas = listar_receitas()
    despesas = listar_despesas()

    print("\n========== RELATORIO GERAL ==========")

    print("\n--- RECEITAS ---")
    print(f"{'ID':<5} {'VALOR':<12} {'CATEGORIA':<20} {'DATA'}")
    print("-" * 50)
    if receitas:
        for r in receitas:
            print(f"{r[0]:<5} R$ {r[1]:<10.2f} {r[2]:<20} {r[3]}")
    else:
        print("Nenhuma receita cadastrada.")

    print("\n--- DESPESAS ---")
    print(f"{'ID':<5} {'VALOR':<12} {'CATEGORIA':<20} {'DATA'}")
    print("-" * 50)
    if despesas:
        for d in despesas:
            print(f"{d[0]:<5} R$ {d[1]:<10.2f} {d[2]:<20} {d[3]}")
    else:
        print("Nenhuma despesa cadastrada.")

    mostrar_saldo()
