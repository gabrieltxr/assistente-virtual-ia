"""
Testes automatizados para src/bia.py — cobrem os casos documentados em
docs/04-avaliacao-metricas.md.

Rodar com:
    cd assistente-virtual-ia
    python -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from bia import Bia


class TestBia(unittest.TestCase):
    def setUp(self):
        self.bia = Bia(pasta_data=str(RAIZ / "data"))

    def test_conceito_conhecido(self):
        resposta = self.bia.responder("o que é CDI?")
        self.assertIn("Certificado de Depósito Interbancário", resposta)

    def test_fora_de_escopo_admite_nao_saber(self):
        resposta = self.bia.responder("qual o melhor time de futebol do brasil?")
        self.assertIn("não tenho informação suficiente", resposta)

    def test_conceito_prioritario_sobre_produto(self):
        # "o que é reserva de emergência?" deve responder o CONCEITO,
        # não o produto Tesouro Selic (ver nota em docs/04).
        resposta = self.bia.responder("o que é reserva de emergência?")
        self.assertIn("valor guardado para imprevistos", resposta)

    def test_pedido_explicito_de_produto(self):
        resposta = self.bia.responder("qual produto você indica para reserva de emergência?")
        self.assertIn("Tesouro Selic", resposta)
        self.assertIn("não é uma recomendação", resposta)

    def test_calculo_juros_compostos(self):
        resposta = self.bia.responder("quanto rende 1000 reais em 12 meses a 1% ao mes?")
        self.assertIn("1126.83", resposta)

    def test_contexto_recalculo(self):
        self.bia.responder("quanto rende 1000 reais em 12 meses a 1% ao mes?")
        resposta = self.bia.responder("e se fossem 24 meses?")
        self.assertIn("24 meses", resposta)
        self.assertIn("1269.73", resposta)

    def test_personalizacao_gastos(self):
        resposta = self.bia.responder("onde estou gastando mais?")
        self.assertIn("moradia", resposta)


if __name__ == "__main__":
    unittest.main()
