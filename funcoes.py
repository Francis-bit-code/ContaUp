from datetime import datetime, date, timedelta
import calendar


def formatar_moeda(valor):
    if valor is None:
        valor = 0

    return f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def converter_valor(valor_texto):
    valor_texto = str(valor_texto).strip()

    if not valor_texto:
        return None

    valor_texto = valor_texto.replace('R$', '').replace(' ', '')

    if ',' in valor_texto and '.' in valor_texto:
        valor_texto = valor_texto.replace('.', '').replace(',', '.')
    elif ',' in valor_texto:
        valor_texto = valor_texto.replace(',', '.')

    try:
        valor = float(valor_texto)

        if valor <= 0:
            return None

        return valor
    except ValueError:
        return None


def converter_inteiro(valor_texto):
    valor_texto = str(valor_texto).strip()

    if valor_texto == '':
        return None

    try:
        valor = int(valor_texto)

        if valor <= 0:
            return None

        return valor
    except ValueError:
        return None


def mes_atual():
    return datetime.now().strftime('%Y-%m')


def data_atual():
    return datetime.now().strftime('%Y-%m-%d')


def validar_data(data_texto):
    try:
        datetime.strptime(data_texto, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def calcular_parcelamento(data_compra, parcelas_total, valor_total):
    try:
        data = datetime.strptime(data_compra, '%Y-%m-%d')
        parcelas_total = int(parcelas_total)
        valor_total = float(valor_total)
    except ValueError:
        return {
            'parcela_atual': 0,
            'parcelas_pagas': 0,
            'parcelas_pendentes': 0,
            'valor_parcela': 0,
            'valor_pendente': 0,
            'status': 'Dados inválidos'
        }

    if parcelas_total <= 0 or valor_total <= 0:
        return {
            'parcela_atual': 0,
            'parcelas_pagas': 0,
            'parcelas_pendentes': 0,
            'valor_parcela': 0,
            'valor_pendente': 0,
            'status': 'Dados inválidos'
        }

    hoje = datetime.now()
    meses = (hoje.year - data.year) * 12 + hoje.month - data.month + 1
    valor_parcela = valor_total / parcelas_total

    if meses <= 0:
        parcela_atual = 0
        parcelas_pagas = 0
        parcelas_pendentes = parcelas_total
        status = 'Ainda não iniciou'
    elif meses > parcelas_total:
        parcela_atual = parcelas_total
        parcelas_pagas = parcelas_total
        parcelas_pendentes = 0
        status = 'Quitada'
    else:
        parcela_atual = meses
        parcelas_pagas = meses - 1
        parcelas_pendentes = parcelas_total - meses
        status = 'Em andamento'

    valor_pendente = parcelas_pendentes * valor_parcela

    return {
        'parcela_atual': parcela_atual,
        'parcelas_pagas': parcelas_pagas,
        'parcelas_pendentes': parcelas_pendentes,
        'valor_parcela': valor_parcela,
        'valor_pendente': valor_pendente,
        'status': status
    }


def analisar_situacao_financeira(saldo, total_gastos_fixos):
    if saldo < 0:
        return {
            'nivel': 'negativo',
            'titulo': 'Vamos nos atentar!',
            'mensagem': 'Você está gastando mais do que recebe. Revise seus gastos fixos, parcelas e despesas do mês.'
        }

    if saldo <= total_gastos_fixos:
        return {
            'nivel': 'risco',
            'titulo': 'Atenção ao orçamento!',
            'mensagem': 'Seu saldo está muito próximo dos compromissos fixos. Evite novas despesas antes de organizar o mês.'
        }

    if saldo <= 200:
        return {
            'nivel': 'risco',
            'titulo': 'Você está na risca!',
            'mensagem': 'Seu saldo está positivo, mas ainda apertado. Continue acompanhando os lançamentos.'
        }

    return {
        'nivel': 'positivo',
        'titulo': 'Parabéns!',
        'mensagem': 'Você está seguindo no caminho certo. Continue economizando e mantendo seus gastos controlados.'
    }


def analisar_planejamento(valor_estimado, saldo):
    if saldo >= valor_estimado:
        return 'Com o saldo previsto, esse planejamento parece possível sem comprometer tanto o orçamento.'

    falta = valor_estimado - saldo
    return f'Ainda faltam {formatar_moeda(falta)} para realizar esse planejamento com mais segurança.'


def dica_renda_extra(total_renda_extra):
    if total_renda_extra <= 0:
        return 'Cadastre rendas extras para acompanhar valores que podem ser separados para objetivos financeiros.'

    if total_renda_extra < 100:
        return 'Você já começou a separar uma renda extra. Continue acumulando antes de assumir novos gastos.'

    if total_renda_extra < 500:
        return 'Sua renda extra está crescendo. Uma boa ideia é separar parte desse valor para uma reserva de emergência.'

    return 'Você acumulou uma boa renda extra. Antes de investir, estude opções de baixo risco e mantenha sua reserva de emergência em dia.'


def calcular_totais_cartao(compras):
    total_parcelas_ativas = 0
    total_pendente = 0
    compras_formatadas = []

    for compra in compras:
        dados = calcular_parcelamento(
            compra['data_compra'],
            compra['parcelas_total'],
            compra['valor_total']
        )

        if dados['status'] == 'Em andamento':
            total_parcelas_ativas += dados['valor_parcela']

        total_pendente += dados['valor_pendente']

        compras_formatadas.append({
            'id': compra['id'],
            'descricao': compra['descricao'],
            'valor_total': compra['valor_total'],
            'data_compra': compra['data_compra'],
            'parcelas_total': compra['parcelas_total'],
            'categoria': compra['categoria'],
            'subcategoria': compra['subcategoria'],
            'parcela_atual': dados['parcela_atual'],
            'parcelas_pagas': dados['parcelas_pagas'],
            'parcelas_pendentes': dados['parcelas_pendentes'],
            'valor_parcela': dados['valor_parcela'],
            'valor_pendente': dados['valor_pendente'],
            'status': dados['status']
        })

    return {
        'compras': compras_formatadas,
        'total_parcelas_ativas': total_parcelas_ativas,
        'total_pendente': total_pendente
    }


def calcular_total_gastos_fixos(gastos_fixos, total_parcelas_cartao):
    total = total_parcelas_cartao

    for gasto in gastos_fixos:
        total += gasto['valor']

    return total


def calcular_data_renda_fixa(mes, tipo_recebimento, dia_recebimento):
    try:
        ano, mes_numero = mes.split('-')
        ano = int(ano)
        mes_numero = int(mes_numero)
        dia_recebimento = int(dia_recebimento)
    except ValueError:
        return ''

    if tipo_recebimento == 'dia_mes':
        ultimo_dia = calendar.monthrange(ano, mes_numero)[1]
        dia = min(dia_recebimento, ultimo_dia)
        return date(ano, mes_numero, dia).strftime('%Y-%m-%d')

    contador = 0
    dia = date(ano, mes_numero, 1)

    while dia.month == mes_numero:
        if dia.weekday() < 5:
            contador += 1

            if contador == dia_recebimento:
                return dia.strftime('%Y-%m-%d')

        dia += timedelta(days=1)

    ultimo_dia = calendar.monthrange(ano, mes_numero)[1]
    return date(ano, mes_numero, ultimo_dia).strftime('%Y-%m-%d')


def formatar_data_br(data_texto):
    try:
        data = datetime.strptime(data_texto, '%Y-%m-%d')
        return data.strftime('%d/%m/%Y')
    except ValueError:
        return data_texto


def preparar_rendas_fixas_mes(rendas_fixas, mes):
    rendas_formatadas = []

    for renda in rendas_fixas:
        data_prevista = calcular_data_renda_fixa(
            mes,
            renda['tipo_recebimento'],
            renda['dia_recebimento']
        )

        if renda['tipo_recebimento'] == 'dia_util':
            texto_recebimento = f'{renda["dia_recebimento"]}º dia útil do mês'
        else:
            texto_recebimento = f'Dia {renda["dia_recebimento"]} de todo mês'

        rendas_formatadas.append({
            'id': renda['id'],
            'descricao': renda['descricao'],
            'valor': renda['valor'],
            'tipo_recebimento': renda['tipo_recebimento'],
            'dia_recebimento': renda['dia_recebimento'],
            'categoria_id': renda['categoria_id'],
            'categoria': renda['categoria'],
            'data_prevista': data_prevista,
            'data_prevista_formatada': formatar_data_br(data_prevista),
            'texto_recebimento': texto_recebimento
        })

    return rendas_formatadas


def calcular_total_rendas_fixas(rendas_fixas):
    total = 0

    for renda in rendas_fixas:
        total += renda['valor']

    return total
