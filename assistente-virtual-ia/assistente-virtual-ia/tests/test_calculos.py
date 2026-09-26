"""
Testes automatizados para src/calculos.py.

Rodar com:
    cd assistente-virtual-ia
    python -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from calculos import juros_compostos, simulacao_financiamento_price, resumo_gastos


class TestJurosCompostos(unittest.TestCase):
    def test_valor_final_conhecido(self):
        resultado = juros_compostos(1000, 0.01, 12)
        # 1000 * 1.01^12 ≈ 1126.83
        self.assertAlmostEqual(resultado["valor_final"], 1126.83, places=2)

    def test_sem_juros_mantem_valor(self):
        resultado = juros_compostos(500, 0.0, 6)
        self.assertEqual(resultado["valor_final"], 500)


class TestFinanciamento(unittest.TestCase):
    def test_parcela_positiva(self):
        resultado = simulacao_financiamento_price(20000, 0.015, 36)
        self.assertGreater(resultado["parcela_mensal"], 0)
        self.assertGreater(resultado["total_pago"], 20000)

    def test_sem_juros_divide_igualmente(self):
        resultado = simulacao_financiamento_price(1200, 0.0, 12)
        self.assertEqual(resultado["parcela_mensal"], 100.0)


class TestResumoGastos(unittest.TestCase):
    def test_identifica_maior_categoria(self):
        gastos = {"moradia": 1380.0, "alimentacao": 570.0, "lazer": 240.0}
        resultado = resumo_gastos(gastos)
        self.assertEqual(resultado["maior_categoria"], "moradia")
        self.assertEqual(resultado["total"], 2190.0)


if __name__ == "__main__":
    unittest.main()
