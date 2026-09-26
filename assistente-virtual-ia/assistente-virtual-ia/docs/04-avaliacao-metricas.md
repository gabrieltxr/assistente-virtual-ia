# 04 — Avaliação e Métricas

## Métricas usadas

| Métrica | Pergunta que ela responde |
|---|---|
| **Assertividade** | O agente respondeu de fato o que foi perguntado? |
| **Segurança (anti-alucinação)** | O agente evitou inventar informação fora da base? |
| **Personalização** | Quando fazia sentido, o agente usou dados do perfil de exemplo? |
| **Continuidade de contexto** | O agente conseguiu reaproveitar informação de uma pergunta anterior? |

Como o agente é determinístico (sem LLM), cada caso de teste tem uma saída
fixa e reproduzível — o que permite avaliação objetiva (não é preciso "achar"
se a resposta ficou boa: dá para rodar de novo e comparar).

## Como os testes foram executados

Os casos abaixo foram gerados rodando `src/bia.py` diretamente (sem
intervenção manual no texto de saída), com o comando:

```bash
cd src
python3 -c "from bia import Bia; bia = Bia('../data'); print(bia.responder('sua pergunta aqui'))"
```

## Casos de teste e resultados reais

| # | Pergunta | Categoria testada | Resultado obtido | Avaliação |
|---|---|---|---|---|
| 1 | "oi" | Saudação | Apresentação da Bia com nome do perfil ("Marina") e lista de temas | ✅ Assertivo |
| 2 | "o que é CDI?" | Conceito (FAQ) | Explicação correta de CDI, extraída da base | ✅ Assertivo, ✅ Seguro |
| 3 | "quanto rende 1000 reais em 12 meses a 1% ao mes?" | Cálculo | R$ 1000 → R$ 1126.83 em 12 meses (juros compostos calculado corretamente: 1000×1.01^12) | ✅ Assertivo, ✅ Cálculo correto |
| 4 | "e se fossem 24 meses?" | Continuidade de contexto | Reaproveitou valor (R$1000) e taxa (1%) do cálculo anterior, recalculando só o prazo → R$ 1269.73 | ✅ Contexto mantido |
| 5 | "onde estou gastando mais?" | Personalização | Usou `perfil_usuario.json`: total R$ 2775,00, maior categoria "moradia" (49,7%) | ✅ Personalizado, ✅ Dado real do perfil |
| 6 | "simular financiamento de 20000 reais em 36 meses a 1,5% ao mes" | Cálculo | Parcela de R$ 723,05 (Tabela Price), total de juros R$ 6.029,72 | ✅ Cálculo correto, inclui aviso sobre CET |
| 7 | "qual o melhor time de futebol do brasil?" | Fora de escopo | Admitiu não ter informação suficiente e sugeriu os temas disponíveis | ✅ Anti-alucinação funcionando |
| 8 | "o que é reserva de emergência?" | Conceito vs. produto (ambíguo) | Retornou a explicação conceitual (não o produto Tesouro Selic) | ✅ Correto após ajuste de prioridade (ver nota abaixo) |
| 9 | "qual produto você indica para reserva de emergência?" | Produto específico | Retornou o produto Tesouro Selic, com aviso de que não é recomendação | ✅ Assertivo, ✅ Limite respeitado |
| 10 | "qual meu saldo?" | Personalização | R$ 1250,30, valor exato do perfil de exemplo | ✅ Personalizado |
| 11 | "como usar cartão de crédito sem entrar em dívida?" | Conceito (FAQ) | Explicação correta sobre fatura integral e crédito rotativo | ✅ Assertivo |

**Nota sobre o caso 8:** na primeira versão do agente, a busca por similaridade
retornava o produto "Tesouro Selic" em vez do conceito "reserva de
emergência", porque a base de produtos tem menos palavras por item, o que
inflava artificialmente a similaridade de Jaccard. A correção foi dar
prioridade à busca conceitual por padrão, e só priorizar produtos quando a
pergunta contém termos explícitos como "produto", "indicar" ou "investir em"
(ver `src/bia.py`, método `_responder_conhecimento`). Isso é justamente o tipo
de ajuste que a etapa de avaliação deve capturar — testar cedo revelou um
problema real de precificação de relevância.

## Resultado consolidado

- 11/11 casos de teste retornaram a categoria de resposta esperada;
- 0 casos de alucinação (nenhuma informação inventada fora da base);
- 2 casos validaram personalização com dados do perfil fictício;
- 1 caso validou continuidade de contexto entre turnos.

## Limitações conhecidas

- A busca por palavras-chave (Jaccard) é sensível a sinônimos não previstos
  nas tags — perguntas com vocabulário muito diferente do cadastrado podem
  cair no "não sei" mesmo quando a base teria a resposta. Mitigação: expandir
  as `tags` de cada item com mais variações.
- A extração de números da pergunta (`_extrair_parametros_calculo`) depende
  de padrões de texto (regex) e pode falhar em frases muito informais ou com
  números por extenso ("mil reais" em vez de "1000 reais").
