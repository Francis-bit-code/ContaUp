import pickle
import database
from datetime import datetime


def exportar_backup():
    """Exporta todos os dados do banco para um arquivo pickle."""

    database.cursor.execute("SELECT * FROM receitas")
    receitas = database.cursor.fetchall()

    database.cursor.execute("SELECT * FROM despesas")
    despesas = database.cursor.fetchall()

    dados = {
        "receitas": receitas,
        "despesas": despesas,
        "data_backup": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    with open("backup.pkl", "wb") as f:
        pickle.dump(dados, f)

    print(f"\nBackup exportado com sucesso!")
    print(f"Arquivo: backup.pkl")
    print(f"Receitas salvas: {len(receitas)}")
    print(f"Despesas salvas: {len(despesas)}")
    print(f"Data: {dados['data_backup']}")


def importar_backup():
    """IMOPORTA DADOS DE UM ARQUIVO PICKLE PARA O BANCO"""

    try:
        with open("backup.pkl", "rb") as f:
            dados = pickle.load(f)

    except FileNotFoundError:
        print("\nArquivo backup.pkl nao encontrado!")
        return

    receitas = dados.get("receitas", [])
    despesas = dados.get("despesas", [])
    data_backup = dados.get("data_backup", "desconhecida")

    print(f"\n=== IMPORTAR BACKUP ===")
    print(f"Data do backup: {data_backup}")
    print(f"Receitas encontradas: {len(receitas)}")
    print(f"Despesas encontradas: {len(despesas)}")

    confirmar = input("\nDeseja importar? Os dados atuais serao mantidos. (s/n): ").lower()

    if confirmar != "s":
        print("Operacao cancelada!")
        return

    for r in receitas:
        database.cursor.execute(
            "INSERT OR IGNORE INTO receitas (id, valor, categoria, data) VALUES (?, ?, ?, ?)",
            (r[0], r[1], r[2], r[3])
        )

    for d in despesas:
        database.cursor.execute(
            "INSERT OR IGNORE INTO despesas (id, valor, categoria, data) VALUES (?, ?, ?, ?)",
            (d[0], d[1], d[2], d[3])
        )

    database.conexao.commit()

    print("Backup importado com sucesso!")
