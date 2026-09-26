# 05 — Pitch: Bia, Assistente de Relacionamento Financeiro

## O problema

Grande parte das pessoas evita se aprofundar nas próprias finanças porque os
termos são confusos (CDI, CET, Tesouro IPCA+...) e as respostas costumam vir
fragmentadas — um pouco no app do banco, um pouco em vídeos, um pouco em
posts genéricos que não consideram a realidade de quem pergunta.

## A solução

A **Bia** é uma assistente virtual que centraliza três coisas em uma única
conversa: explicação de conceitos, simulações práticas (juros compostos,
financiamento) e leitura organizada dos próprios gastos — sempre deixando
claro quando não tem certeza, em vez de arriscar uma resposta errada.

## Por que "modo simples" (sem LLM) para este protótipo

Para o primeiro protótipo, priorizamos um agente **100% determinístico**:
busca em base de conhecimento + templates + cálculos reais. Isso trouxe três
vantagens diretas para a validação da ideia:

1. **Zero custo de API** para testar o conceito;
2. **Comportamento auditável** — cada resposta pode ser rastreada até um item
   real da base (ver `docs/02-base-conhecimento.md`);
3. **Testes objetivos e reproduzíveis** (ver `docs/04-avaliacao-metricas.md`),
   sem a variabilidade natural de um modelo generativo.

## Demonstração rápida

```
Você: o que é CDI?
Bia: CDI (Certificado de Depósito Interbancário) é uma taxa de referência
usada pelos bancos para operações entre si...

Você: onde estou gastando mais?
Bia: Olhando seus gastos deste mês, o total foi de R$ 2775.00. A maior
categoria é 'moradia', com R$ 1380.00 (49.7% do total)...

Você: quanto rende 1000 reais em 12 meses a 1% ao mes?
Bia: Simulando R$ 1000.00 com 1.00% ao mês por 12 meses: o valor final
seria de aproximadamente R$ 1126.83...

Você: e se fossem 24 meses?
Bia: Refazendo com os novos números: ... por 24 meses resultaria em
R$ 1269.73 (R$ 269.73 de rendimento).
```

## O que aprendi construindo este projeto

- Um agente não precisa de um LLM para ser útil e "conversacional" — para um
  escopo bem definido, regras + uma boa base de conhecimento já resolvem boa
  parte do problema, e com previsibilidade total;
- Métricas de similaridade simples (como Jaccard) podem ter vieses sutis
  (bases menores "parecem" mais relevantes) — isso só apareceu ao rodar
  casos de teste reais, reforçando a importância da etapa de avaliação;
- Separar claramente "busca de conhecimento" (`retrieval.py`) de "lógica de
  conversa" (`bia.py`) facilita a evolução futura do projeto sem reescrever
  tudo.

## Próximos passos

- Plugar uma LLM real (usando o prompt documentado em `docs/03-prompts.md`)
  para lidar com perguntas fora do vocabulário previsto na base;
- Adicionar uma interface web simples (ex.: Streamlit) sobre a mesma lógica
  de `src/bia.py`, sem precisar reescrever o núcleo do agente;
- Ampliar a base de conhecimento com mais conceitos e produtos, e testar com
  perfis de usuário diferentes (não só o perfil "Marina" usado como exemplo).
