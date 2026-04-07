def cadastrar_receita(receitas):
    print("=== CADASTRO DE RECEITAS ===")
    
    while True:
        try:
            valor = float(input("Digite o valor da receita: "))
            if valor <= 0:
                print("O valor deve ser maior que zero!")
                continue
            break
        except ValueError:
            print("Digite um número válido!")
    
    while True:
        descricao = input("Digite a descrição: ")
        if descricao.strip() == "":
            print("A descrição não pode ser vazia!")
        else:
            break

    while True:
        data = input("Digite a data (dd/mm/aaaa): ")
        if "/" not in data:
            print("Formato inválido! Use dd/mm/aaaa")
        else:
            break

    receita = {
        "valor": valor,
        "descricao": descricao,
        "data": data
    }

    receitas.append(receita)

    print("Receita cadastrada com sucesso!")

    print("\nReceita cadastrada:")
    print(f"Valor: R${valor:.2f}")
    print(f"Descrição: {descricao}")
    print(f"Data: {data}")

receitas = []
cadastrar_receita(receitas)




