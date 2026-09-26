"""
Módulo de recuperação de informação (retrieval).

Implementa uma busca simples por sobreposição de palavras-chave entre a
pergunta da pessoa usuária e os itens da base de conhecimento / produtos.
Não usa embeddings nem API externa — é 100% local e determinístico,
o que facilita testar e explicar o comportamento do assistente.
"""

import json
import re
import unicodedata
from pathlib import Path

# Limiar mínimo de similaridade para considerar que a base "tem resposta".
# Abaixo disso, a Bia deve admitir que não sabe, em vez de inventar.
LIMIAR_CONFIANCA = 0.20

STOPWORDS = {
    "o", "a", "os", "as", "de", "da", "do", "das", "dos", "um", "uma",
    "e", "é", "para", "por", "com", "que", "qual", "quais", "como",
    "eu", "me", "minha", "meu", "sobre", "no", "na", "nos", "nas",
    "sera", "será", "vou", "quero", "gostaria", "pode", "pra", "isso",
}


def _normalizar(texto: str) -> str:
    """Minúsculas + remoção de acentos, para comparar palavras de forma robusta."""
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto


def _tokenizar(texto: str) -> set:
    texto = _normalizar(texto)
    palavras = re.findall(r"[a-z0-9]+", texto)
    return {p for p in palavras if p not in STOPWORDS and len(p) > 1}


def _carregar_json(caminho: Path) -> list:
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


class BaseConhecimento:
    """Carrega e permite consultar a base de conhecimento e o catálogo de produtos."""

    def __init__(self, pasta_data: str):
        pasta = Path(pasta_data)
        self.faq = _carregar_json(pasta / "base_conhecimento.json")
        self.produtos = _carregar_json(pasta / "produtos_financeiros.json")
        self.perfil = _carregar_json(pasta / "perfil_usuario.json")

        # Pré-processa os tokens de cada item para acelerar a busca.
        for item in self.faq:
            campo = " ".join(item.get("tags", [])) + " " + item.get("pergunta", "")
            item["_tokens"] = _tokenizar(campo)
        for item in self.produtos:
            campo = " ".join(item.get("tags", [])) + " " + item.get("nome", "")
            item["_tokens"] = _tokenizar(campo)

    def _melhor_match(self, pergunta_usuario: str, itens: list):
        tokens_pergunta = _tokenizar(pergunta_usuario)
        if not tokens_pergunta:
            return None, 0.0

        melhor_item, melhor_score = None, 0.0
        for item in itens:
            tokens_item = item["_tokens"]
            if not tokens_item:
                continue
            intersecao = tokens_pergunta & tokens_item
            # Jaccard simples: intersecção sobre união dos conjuntos.
            uniao = tokens_pergunta | tokens_item
            score = len(intersecao) / len(uniao) if uniao else 0.0
            if score > melhor_score:
                melhor_item, melhor_score = item, score
        return melhor_item, melhor_score

    def buscar_conceito(self, pergunta_usuario: str):
        """Retorna (item, score) do conceito/FAQ mais relevante, ou (None, 0) se nada relevante."""
        item, score = self._melhor_match(pergunta_usuario, self.faq)
        if score < LIMIAR_CONFIANCA:
            return None, score
        return item, score

    def buscar_produto(self, pergunta_usuario: str):
        """Retorna (item, score) do produto mais relevante, ou (None, 0) se nada relevante."""
        item, score = self._melhor_match(pergunta_usuario, self.produtos)
        if score < LIMIAR_CONFIANCA:
            return None, score
        return item, score
