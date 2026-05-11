from datetime import datetime
import database
from validacoes import validar_valor, validar_categoria, validar_data


def cadastrar_despesa():
    print("\n=== CADASTRAR DESPESA ===")
    valor = validar_valor()
    categoria = validar_categoria()
    data = validar_data()
    database.cursor.execute(
        "INSERT INTO despesas (valor, categoria, data) VALUES (?, ?, ?)",
        (valor, categoria, data)
    )
    database.conexao.commit()
    print("Despesa cadastrada com sucesso!")


def listar_despesas():
    database.cursor.execute("SELECT * FROM despesas")
    return database.cursor.fetchall()


def relatorio_despesas():
    linhas = listar_despesas()
    print("\n=== DESPESAS ===")
    print(f"{'ID':<5} {'VALOR':<12} {'CATEGORIA':<20} {'DATA'}")
    print("-" * 50)
    if not linhas:
        print("Nenhuma despesa cadastrada!")
        return
    for linha in linhas:
        print(f"{linha[0]:<5} R$ {linha[1]:<10.2f} {linha[2]:<20} {linha[3]}")


def editar_despesa():
    print("\n=== EDITAR DESPESA ===")
    relatorio_despesas()
    try:
        id_despesa = int(input("\nDigite o ID da despesa: "))
    except ValueError:
        print("ID invalido!")
        return
    database.cursor.execute("SELECT * FROM despesas WHERE id = ?", (id_despesa,))
    despesa = database.cursor.fetchone()
    if despesa is None:
        print("Despesa nao encontrada!")
        return
    print("\n=== DADOS ATUAIS ===")
    print(f"Valor:     R$ {despesa[1]:.2f}")
    print(f"Categoria: {despesa[2]}")
    print(f"Data:      {despesa[3]}")
    print("(Pressione Enter para manter o valor atual)")
    novo_valor = input("\nNovo valor: ")
    nova_categoria = input("Nova categoria: ")
    nova_data = input("Nova data (dd/mm/aaaa): ")
    valor = despesa[1]
    categoria = despesa[2]
    data = despesa[3]
    if novo_valor.strip() != "":
        try:
            valor = float(novo_valor)
            if valor <= 0:
                print("Valor invalido!")
                return
        except ValueError:
            print("Valor invalido!")
            return
    if nova_categoria.strip() != "":
        categoria = nova_categoria.strip()
    if nova_data.strip() != "":
        try:
            datetime.strptime(nova_data.strip(), "%d/%m/%Y")
            data = nova_data.strip()
        except ValueError:
            print("Data invalida!")
            return
    database.cursor.execute("""
        UPDATE despesas SET valor = ?, categoria = ?, data = ? WHERE id = ?
    """, (valor, categoria, data, id_despesa))
    database.conexao.commit()
    print("Despesa atualizada com sucesso!")


def deletar_despesa():
    print("\n=== DELETAR DESPESA ===")
    relatorio_despesas()
    try:
        id_despesa = int(input("\nDigite o ID da despesa: "))
    except ValueError:
        print("ID invalido!")
        return
    database.cursor.execute("SELECT * FROM despesas WHERE id = ?", (id_despesa,))
    despesa = database.cursor.fetchone()
    if despesa is None:
        print("Despesa nao encontrada!")
        return
    confirmar = input(f"Deseja excluir a despesa R$ {despesa[1]:.2f} - {despesa[2]}? (s/n): ").lower()
    if confirmar == "s":
        database.cursor.execute("DELETE FROM despesas WHERE id = ?", (id_despesa,))
        database.conexao.commit()
        print("Despesa excluida com sucesso!")
    else:
        print("Operacao cancelada!")
