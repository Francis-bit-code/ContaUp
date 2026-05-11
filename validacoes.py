from datetime import datetime


def validar_valor():
    while True:
        try:
            valor = float(input("Digite o valor: "))
            if valor <= 0:
                print("Valor invalido! Digite um numero maior que zero.")
                continue
            return valor
        except ValueError:
            print("Digite um numero valido!")


def validar_data():
    while True:
        data = input("Digite a data (dd/mm/aaaa): ")
        try:
            datetime.strptime(data, "%d/%m/%Y")
            return data
        except ValueError:
            print("Data invalida! Use o formato dd/mm/aaaa.")


def validar_categoria():
    while True:
        categoria = input("Categoria: ").strip()
        if categoria == "":
            print("Campo obrigatorio! Digite uma categoria.")
        else:
            return categoria
