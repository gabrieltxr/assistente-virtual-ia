"""
Cálculos financeiros demonstrativos usados pela Bia.

Todas as funções são puras (recebem números, devolvem números) para
serem fáceis de testar isoladamente — ver docs/04-avaliacao-metricas.md.
"""


def juros_compostos(valor_inicial: float, taxa_mensal: float, meses: int) -> dict:
    """
    Calcula o valor final de um investimento com juros compostos.

    taxa_mensal deve estar em decimal (1% ao mês = 0.01).
    """
    valor_final = valor_inicial * ((1 + taxa_mensal) ** meses)
    juros_ganhos = valor_final - valor_inicial
    return {
        "valor_inicial": round(valor_inicial, 2),
        "taxa_mensal": taxa_mensal,
        "meses": meses,
        "valor_final": round(valor_final, 2),
        "juros_ganhos": round(juros_ganhos, 2),
    }


def simulacao_financiamento_price(valor_financiado: float, taxa_mensal: float, meses: int) -> dict:
    """
    Simula uma parcela fixa (Tabela Price) para um financiamento.

    Fórmula: PMT = PV * i / (1 - (1 + i) ** -n)
    """
    if taxa_mensal == 0:
        parcela = valor_financiado / meses
    else:
        i = taxa_mensal
        parcela = valor_financiado * i / (1 - (1 + i) ** (-meses))

    total_pago = parcela * meses
    total_juros = total_pago - valor_financiado
    return {
        "valor_financiado": round(valor_financiado, 2),
        "taxa_mensal": taxa_mensal,
        "meses": meses,
        "parcela_mensal": round(parcela, 2),
        "total_pago": round(total_pago, 2),
        "total_juros": round(total_juros, 2),
    }


def resumo_gastos(gastos_por_categoria: dict) -> dict:
    """Ordena os gastos por categoria do maior para o menor e calcula o total."""
    total = sum(gastos_por_categoria.values())
    ordenado = sorted(gastos_por_categoria.items(), key=lambda x: x[1], reverse=True)
    maior_categoria, maior_valor = ordenado[0]
    percentual_maior = (maior_valor / total * 100) if total else 0
    return {
        "total": round(total, 2),
        "ordenado": ordenado,
        "maior_categoria": maior_categoria,
        "maior_valor": round(maior_valor, 2),
        "percentual_maior": round(percentual_maior, 1),
    }
