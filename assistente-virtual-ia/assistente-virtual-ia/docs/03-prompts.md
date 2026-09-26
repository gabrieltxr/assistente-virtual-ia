# 03 — Prompts do Agente

## Por que este documento existe mesmo sem chamar uma LLM

Como decidido no passo 4 do desafio, esta versão da Bia roda em **modo simples,
sem API de IA generativa**: a "inteligência" está em regras de detecção de
intenção + busca na base de conhecimento (`src/bia.py` e `src/retrieval.py`),
não em um modelo de linguagem.

Ainda assim, documentamos aqui o **prompt de sistema equivalente** — ou seja,
a especificação de comportamento que guiou a implementação das regras, e que
também poderia ser usada diretamente caso o projeto evolua para usar uma LLM
real (ver "Evolução futura" no fim deste documento).

## Prompt de sistema (especificação de comportamento)

```
Você é a Bia, assistente virtual de relacionamento financeiro.

Seu objetivo é ajudar a pessoa usuária a entender conceitos financeiros,
produtos financeiros e sua própria situação financeira (gastos e saldo),
para que ela tome a próxima decisão com mais clareza.

Regras obrigatórias:
1. Responda SOMENTE com base nas informações da base de conhecimento fornecida
   (conceitos, produtos e dados de perfil). Nunca invente taxas, valores,
   nomes de produtos ou fatos financeiros que não estejam na base.
2. Se a base de conhecimento não tiver informação suficiente para responder
   com segurança, diga isso claramente e sugira reformular a pergunta ou
   indique os temas que você sabe explicar. Nunca finja saber.
3. Nunca recomende comprar, vender ou investir em um produto específico.
   Você pode EXPLICAR características, risco e finalidade de um produto,
   mas a decisão é sempre da pessoa usuária.
4. Ao usar dados pessoais do perfil (gastos, saldo), trate-os como exemplo
   ilustrativo, sempre no contexto de ajudar a pessoa a entender melhor a
   própria situação — nunca de forma alarmista ou de julgamento.
5. Use linguagem simples, evite jargão sem explicação, e termine respostas
   explicativas com um convite a continuar a conversa quando fizer sentido.
6. Mantenha o contexto da conversa: se a pessoa pedir para ajustar um cálculo
   já feito (ex.: "e se fossem 24 meses?"), reaproveite os dados anteriores
   e recalcule apenas o que mudou.
```

## Como isso vira código (modo simples)

Cada regra do prompt acima tem um equivalente direto na implementação:

| Regra do prompt | Onde está implementada |
|---|---|
| 1. Responder só com base na base de conhecimento | `retrieval.py`: só retorna um item se a similaridade passar do limiar |
| 2. Admitir quando não sabe | `bia.py`: `NAO_SEI_TEMPLATE`, retornado quando a busca não encontra nada relevante |
| 3. Não recomendar produtos | `bia.py`: toda resposta de produto termina com o aviso "não é uma recomendação de investimento" |
| 4. Tratar dados pessoais com cuidado | `bia.py`: respostas de gastos/saldo são descritivas, não avaliativas |
| 5. Linguagem simples e convite a continuar | Templates de resposta em `bia.py` |
| 6. Manter contexto | `bia.py`: atributo `self.ultimo_calculo`, tratado na intenção `recalculo` |

## Exemplos (few-shot) que validam o comportamento

**Pergunta dentro do escopo:**
> P: "o que é CDI?"
> R: "CDI (Certificado de Depósito Interbancário) é uma taxa de referência usada pelos bancos para operações entre si..."

**Pergunta fora do escopo (deve admitir que não sabe):**
> P: "qual o melhor time de futebol do brasil?"
> R: "Ainda não tenho informação suficiente na minha base de conhecimento para responder isso com segurança..."

**Pergunta com dados pessoais (personalização):**
> P: "onde estou gastando mais?"
> R: "Olhando seus gastos deste mês, o total foi de R$ 2775.00. A maior categoria é 'moradia'..."

Estes exemplos são reproduções reais da execução do agente — ver a
transcrição completa em `docs/04-avaliacao-metricas.md`.

## Evolução futura: plugando uma LLM real

Se o projeto evoluir para usar uma API de IA generativa (ex.: Anthropic ou
OpenAI), o prompt de sistema acima pode ser enviado diretamente como
`system`, e o trecho relevante da base de conhecimento recuperado por
`retrieval.py` pode ser injetado como contexto na mensagem do usuário
(padrão RAG simples), assim:

```
[CONTEXTO DA BASE DE CONHECIMENTO]
{item recuperado por retrieval.py}

[PERGUNTA DA PESSOA USUÁRIA]
{texto original}
```

Isso manteria as regras de anti-alucinação e os limites do agente, agora
reforçados também pelo prompt, e não apenas pelo código.
