"""
Aplicação funcional (CLI) para testar a conversa com a Bia.

Uso:
    cd src
    python app.py
"""

from bia import Bia


BANNER = """
==================================================
  Bia - Assistente de Relacionamento Financeiro
==================================================
Digite sua pergunta (ou 'sair' para encerrar).
Exemplos:
  - o que é CDI?
  - quanto rende 1000 reais em 12 meses a 1% ao mes?
  - onde estou gastando mais?
  - simular financiamento de 20000 reais em 36 meses a 1,5% ao mes
==================================================
"""


def main():
    bia = Bia(pasta_data="../data")
    print(BANNER)
    while True:
        try:
            pergunta = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBia: Até logo!")
            break

        if not pergunta:
            continue
        if pergunta.lower() in {"sair", "exit", "quit"}:
            print("Bia: Até logo! Foi um prazer conversar com você.")
            break

        resposta = bia.responder(pergunta)
        print(f"Bia: {resposta}\n")


if __name__ == "__main__":
    main()
