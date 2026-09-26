# 02 — Base de Conhecimento

## Arquivos

| Arquivo | Conteúdo | Usado para |
|---|---|---|
| `data/base_conhecimento.json` | 10 conceitos financeiros em formato pergunta/resposta, com tags | Responder "o que é X?" |
| `data/produtos_financeiros.json` | 6 produtos financeiros com descrição, risco e indicação | Responder "qual produto..." |
| `data/perfil_usuario.json` | Perfil fictício de uma usuária (Marina): renda, gastos por categoria, saldo | Personalizar respostas sobre gastos/saldo |

## Estrutura de cada item da base de conceitos

```json
{
  "id": "cdi",
  "categoria": "conceito",
  "tags": ["cdi", "taxa", "renda fixa", "cdb"],
  "pergunta": "O que é CDI?",
  "resposta": "..."
}
```

- **id**: identificador único, usado internamente para lembrar do "último tópico" na conversa;
- **tags**: palavras-chave usadas na busca (além da própria pergunta);
- **resposta**: texto final devolvido à pessoa usuária, sem necessidade de reescrita por IA generativa.

## Estratégia de busca (retrieval)

Implementada em `src/retrieval.py`, sem embeddings nem API externa:

1. A pergunta da pessoa e os itens da base são **tokenizados** (minúsculas, sem
   acento, sem palavras irrelevantes como "o", "a", "que");
2. Calcula-se a **similaridade de Jaccard** (intersecção / união dos conjuntos
   de palavras) entre a pergunta e cada item;
3. O item com maior similaridade é escolhido, **desde que** ultrapasse um
   limiar mínimo (`LIMIAR_CONFIANCA = 0.20`);
4. Se nenhum item ultrapassar o limiar, a Bia assume que não tem informação
   suficiente — este é o principal mecanismo **anti-alucinação** do projeto:
   a resposta só é dada se vier de um item real da base.

## Por que essa abordagem para o desafio

- É totalmente **auditável**: dá para explicar exatamente por que a Bia
  respondeu X e não Y (mostrando o score de similaridade);
- Não depende de chave de API nem de conexão com a internet;
- É fácil de testar de forma determinística (mesma pergunta → mesma resposta),
  o que facilita a etapa de avaliação (`docs/04-avaliacao-metricas.md`).

## Como crescer a base

Basta adicionar novos objetos aos arquivos JSON em `data/`, seguindo a mesma
estrutura. Não é necessário alterar o código em `src/` — a busca já
considera qualquer item novo automaticamente. Boas adições futuras: Pix,
consórcio, previdência privada, seguros.
