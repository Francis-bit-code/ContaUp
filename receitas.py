from datetime import datetime
import database
from validacoes import validar_valor, validar_categoria, validar_data


def cadastrar_receita():
    print("\n=== CADASTRAR RECEITA ===")
    valor = validar_valor()
    categoria = validar_categoria()
    data = validar_data()
    database.cursor.execute(
        "INSERT INTO receitas (valor, categoria, data) VALUES (?, ?, ?)",
        (valor, categoria, data)
    )
    database.conexao.commit()
    print("Receita cadastrada com sucesso!")


def listar_receitas():
    database.cursor.execute("SELECT * FROM receitas")
    return database.cursor.fetchall()


def relatorio_receitas():
    linhas = listar_receitas()
    print("\n=== RECEITAS ===")
    print(f"{'ID':<5} {'VALOR':<12} {'CATEGORIA':<20} {'DATA'}")
    print("-" * 50)
    if not linhas:
        print("Nenhuma receita cadastrada!")
        return
    for linha in linhas:
        print(f"{linha[0]:<5} R$ {linha[1]:<10.2f} {linha[2]:<20} {linha[3]}")


def editar_receita():
    print("\n=== EDITAR RECEITA ===")
    relatorio_receitas()
    try:
        id_receita = int(input("\nDigite o ID da receita: "))
    except ValueError:
        print("ID invalido!")
        return
    database.cursor.execute("SELECT * FROM receitas WHERE id = ?", (id_receita,))
    receita = database.cursor.fetchone()
    if receita is None:
        print("Receita nao encontrada!")
        return
    print("\n=== DADOS ATUAIS ===")
    print(f"Valor:     R$ {receita[1]:.2f}")
    print(f"Categoria: {receita[2]}")
    print(f"Data:      {receita[3]}")
    print("(Pressione Enter para manter o valor atual)")
    novo_valor = input("\nNovo valor: ")
    nova_categoria = input("Nova categoria: ")
    nova_data = input("Nova data (dd/mm/aaaa): ")
    valor = receita[1]
    categoria = receita[2]
    data = receita[3]
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
        UPDATE receitas SET valor = ?, categoria = ?, data = ? WHERE id = ?
    """, (valor, categoria, data, id_receita))
    database.conexao.commit()
    print("Receita atualizada com sucesso!")


def deletar_receita():
    print("\n=== DELETAR RECEITA ===")
    relatorio_receitas()
    try:
        id_receita = int(input("\nDigite o ID da receita: "))
    except ValueError:
        print("ID invalido!")
        return
    database.cursor.execute("SELECT * FROM receitas WHERE id = ?", (id_receita,))
    receita = database.cursor.fetchone()
    if receita is None:
        print("Receita nao encontrada!")
        return
    confirmar = input(f"Deseja excluir a receita R$ {receita[1]:.2f} - {receita[2]}? (s/n): ").lower()
    if confirmar == "s":
        database.cursor.execute("DELETE FROM receitas WHERE id = ?", (id_receita,))
        database.conexao.commit()
        print("Receita excluida com sucesso!")
    else:
        print("Operacao cancelada!")
