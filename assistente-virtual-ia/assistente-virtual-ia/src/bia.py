"""
Bia — Assistente Virtual de Relacionamento Financeiro.

Este módulo concentra a "lógica de conversa": decide qual tipo de pedido
a pessoa usuária fez (conceito, produto, cálculo, dados pessoais) e monta
uma resposta com base APENAS na base de conhecimento e nos dados
fornecidos — sem inventar informação financeira.

Este é o "modo simples sem API": não há chamada a nenhum LLM externo.
As respostas são compostas por templates + dados reais da base, o que
torna o comportamento 100% previsível e testável (ver docs/04).
"""

import re
import unicodedata

from retrieval import BaseConhecimento
from calculos import juros_compostos, simulacao_financiamento_price, resumo_gastos

NAO_SEI_TEMPLATE = (
    "Ainda não tenho informação suficiente na minha base de conhecimento para "
    "responder isso com segurança. Posso te ajudar com dúvidas sobre {temas}. "
    "Se quiser, reformule a pergunta ou pergunte sobre um desses temas."
)

TEMAS_DISPONIVEIS = (
    "conceitos financeiros (CDI, Selic, reserva de emergência, Tesouro Direto, "
    "juros compostos, score de crédito, cartão de crédito, financiamento, "
    "diversificação, inflação), produtos financeiros e simulações de juros "
    "compostos ou financiamento"
)


def _normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def _extrair_numero(padrao: str, texto: str):
    match = re.search(padrao, texto)
    if not match:
        return None
    valor = match.group(1).replace(".", "").replace(",", ".")
    try:
        return float(valor)
    except ValueError:
        return None


def _extrair_parametros_calculo(texto: str) -> dict:
    """Extrai valor (R$), taxa (%) e prazo (meses) de uma frase em linguagem natural."""
    texto_norm = _normalizar(texto)

    valor = _extrair_numero(r"r?\$?\s?([\d\.,]+)\s*(?:reais|r\$)", texto_norm)
    if valor is None:
        valor = _extrair_numero(r"r\$\s?([\d\.,]+)", texto_norm)

    taxa = _extrair_numero(r"([\d\.,]+)\s?%", texto_norm)
    taxa_decimal = (taxa / 100) if taxa is not None else None

    meses = _extrair_numero(r"([\d\.,]+)\s?mes(?:es)?", texto_norm)
    anos = _extrair_numero(r"([\d\.,]+)\s?ano(?:s)?", texto_norm)
    if meses is None and anos is not None:
        meses = anos * 12

    return {
        "valor": valor,
        "taxa_decimal": taxa_decimal,
        "meses": int(meses) if meses is not None else None,
    }


class Bia:
    def __init__(self, pasta_data: str = "../data"):
        self.base = BaseConhecimento(pasta_data)
        self.ultimo_calculo = None  # guarda o último cálculo para permitir "e se..." (contexto)
        self.ultimo_topico = None   # guarda o último conceito explicado (contexto)

    # ---------------------- Detecção de intenção ----------------------

    def _detectar_intencao(self, texto: str) -> str:
        t = _normalizar(texto)

        if any(p in t for p in ["oi", "ola", "boa tarde", "bom dia", "boa noite"]) and len(t) < 20:
            return "saudacao"

        if any(p in t for p in ["quanto rendeu", "quanto rende", "juros compostos", "simular investimento", "simule um investimento"]):
            return "calculo_juros"

        if any(p in t for p in ["financiamento", "financiar", "parcela do financiamento", "simular financiamento"]):
            return "calculo_financiamento"

        if t.strip().startswith("e se") or t.strip().startswith("e com") or t.strip().startswith("e para"):
            if self.ultimo_calculo:
                return "recalculo"

        if any(p in t for p in ["onde estou gastando", "meus gastos", "gastos do mes", "estou gastando"]):
            return "gastos"

        if any(p in t for p in ["meu saldo", "quanto tenho na conta", "saldo da conta"]):
            return "saldo"

        return "conhecimento"  # fallback: busca em conceitos e produtos

    # ---------------------- Handlers de intenção ----------------------

    def _responder_saudacao(self) -> str:
        nome = self.base.perfil.get("nome", "")
        return (
            f"Olá{', ' + nome if nome else ''}! Eu sou a Bia, sua assistente de relacionamento "
            f"financeiro. Posso te ajudar com {TEMAS_DISPONIVEIS}. O que você gostaria de saber?"
        )

    def _responder_calculo_juros(self, texto: str) -> str:
        params = _extrair_parametros_calculo(texto)
        faltando = [k for k, v in params.items() if v is None]
        if faltando:
            return (
                "Para simular os juros compostos, preciso de três informações: o valor inicial "
                "(em reais), a taxa mensal (em %) e o prazo (em meses). Pode me passar, por "
                "exemplo: 'quanto rende 1000 reais em 12 meses a 1% ao mês?'"
            )
        resultado = juros_compostos(params["valor"], params["taxa_decimal"], params["meses"])
        self.ultimo_calculo = {"tipo": "juros", **params}
        return (
            f"Simulando R$ {resultado['valor_inicial']:.2f} com {resultado['taxa_mensal']*100:.2f}% "
            f"ao mês por {resultado['meses']} meses: o valor final seria de aproximadamente "
            f"R$ {resultado['valor_final']:.2f}, ou seja, R$ {resultado['juros_ganhos']:.2f} de "
            f"rendimento. Lembrando que esta é uma simulação simplificada, sem considerar impostos "
            f"ou taxas do produto. Quer testar com outro valor ou prazo?"
        )

    def _responder_calculo_financiamento(self, texto: str) -> str:
        params = _extrair_parametros_calculo(texto)
        faltando = [k for k, v in params.items() if v is None]
        if faltando:
            return (
                "Para simular um financiamento, preciso do valor financiado (em reais), da taxa "
                "de juros mensal (em %) e do número de parcelas (em meses). Por exemplo: "
                "'simular financiamento de 20000 reais em 36 meses a 1,5% ao mês'."
            )
        resultado = simulacao_financiamento_price(params["valor"], params["taxa_decimal"], params["meses"])
        self.ultimo_calculo = {"tipo": "financiamento", **params}
        return (
            f"Para um financiamento de R$ {resultado['valor_financiado']:.2f} em "
            f"{resultado['meses']} parcelas a {resultado['taxa_mensal']*100:.2f}% ao mês, a "
            f"parcela mensal seria de aproximadamente R$ {resultado['parcela_mensal']:.2f}, "
            f"totalizando R$ {resultado['total_pago']:.2f} pagos, dos quais "
            f"R$ {resultado['total_juros']:.2f} são juros. Vale comparar essa taxa com o CET "
            f"(Custo Efetivo Total) informado pela instituição antes de decidir. Quer simular "
            f"outro cenário?"
        )

    def _responder_recalculo(self, texto: str) -> str:
        novos = _extrair_parametros_calculo(texto)
        base = dict(self.ultimo_calculo)
        for chave in ["valor", "taxa_decimal", "meses"]:
            if novos.get(chave) is not None:
                base[chave] = novos[chave]

        if base["tipo"] == "juros":
            resultado = juros_compostos(base["valor"], base["taxa_decimal"], base["meses"])
            self.ultimo_calculo = base
            return (
                f"Refazendo com os novos números: R$ {resultado['valor_inicial']:.2f} a "
                f"{resultado['taxa_mensal']*100:.2f}% ao mês por {resultado['meses']} meses "
                f"resultaria em R$ {resultado['valor_final']:.2f} (R$ {resultado['juros_ganhos']:.2f} "
                f"de rendimento)."
            )
        else:
            resultado = simulacao_financiamento_price(base["valor"], base["taxa_decimal"], base["meses"])
            self.ultimo_calculo = base
            return (
                f"Refazendo o financiamento: R$ {resultado['valor_financiado']:.2f} em "
                f"{resultado['meses']} parcelas a {resultado['taxa_mensal']*100:.2f}% ao mês "
                f"resultaria em parcelas de R$ {resultado['parcela_mensal']:.2f}, totalizando "
                f"R$ {resultado['total_pago']:.2f}."
            )

    def _responder_gastos(self) -> str:
        gastos = self.base.perfil.get("gastos_por_categoria_mes_atual")
        if not gastos:
            return NAO_SEI_TEMPLATE.format(temas=TEMAS_DISPONIVEIS)
        resumo = resumo_gastos(gastos)
        return (
            f"Olhando seus gastos deste mês, o total foi de R$ {resumo['total']:.2f}. A maior "
            f"categoria é '{resumo['maior_categoria']}', com R$ {resumo['maior_valor']:.2f} "
            f"({resumo['percentual_maior']:.1f}% do total). Isso é bem comum! Quer que eu explique "
            f"alguma estratégia de organização de gastos?"
        )

    def _responder_saldo(self) -> str:
        saldo = self.base.perfil.get("saldo_conta")
        if saldo is None:
            return NAO_SEI_TEMPLATE.format(temas=TEMAS_DISPONIVEIS)
        return f"Seu saldo atual em conta é de R$ {saldo:.2f}."

    def _formatar_produto(self, produto: dict) -> str:
        return (
            f"{produto['nome']}: {produto['descricao']} Nível de risco: {produto['risco']}. "
            f"Costuma ser indicado para: {produto['indicado_para']}. "
            f"Isso não é uma recomendação de investimento — é uma explicação geral do produto."
        )

    def _responder_conhecimento(self, texto: str) -> str:
        t = _normalizar(texto)
        conceito, score_c = self.base.buscar_conceito(texto)
        produto, score_p = self.base.buscar_produto(texto)

        # Se a pergunta menciona explicitamente "produto"/"indicação"/"investir em",
        # a intenção é sobre um produto específico, então ele tem prioridade.
        pede_produto = any(p in t for p in ["produto", "indica", "recomend", "investir em", "onde investir"])

        if pede_produto and produto:
            self.ultimo_topico = produto["id"]
            return self._formatar_produto(produto)

        # Caso contrário, perguntas de "o que é X" são conceituais por padrão.
        if conceito:
            self.ultimo_topico = conceito["id"]
            return conceito["resposta"]

        if produto:
            self.ultimo_topico = produto["id"]
            return self._formatar_produto(produto)

        return NAO_SEI_TEMPLATE.format(temas=TEMAS_DISPONIVEIS)

    # ---------------------- Ponto de entrada ----------------------

    def responder(self, texto: str) -> str:
        intencao = self._detectar_intencao(texto)
        if intencao == "saudacao":
            return self._responder_saudacao()
        if intencao == "calculo_juros":
            return self._responder_calculo_juros(texto)
        if intencao == "calculo_financiamento":
            return self._responder_calculo_financiamento(texto)
        if intencao == "recalculo":
            return self._responder_recalculo(texto)
        if intencao == "gastos":
            return self._responder_gastos()
        if intencao == "saldo":
            return self._responder_saldo()
        return self._responder_conhecimento(texto)
