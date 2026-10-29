# Sprint 6 — pesquisa textual local limitada

## Objetivo e autorização

Executar somente S6.01–S6.14 ainda abertas no PRD, sem antecipar Sprints 7–9.
O mantenedor escolheu busca textual local em páginas limitadas e autorizou
até duas consultas reais de produtos, cada uma com limit=1, pelo loader e
token existentes, sem retries, alteração do `.env` ou dados privados retidos.

## Alternativas consideradas

- Escolhida: consulta paginada existente e substring local, preservando o
  body fechado page/limit, a origem e todos os controles de transporte.
- Não escolhida: filtro remoto mascara; documentado, mas não equivale a
  descrição textual e ampliaria o schema fechado do cliente.
- Rejeitada: enviar query/descricao ou busca semântica ao ERP sem contrato.

## Contrato proposto

`search_products(client, query, max_results=20)` será uma função assíncrona
utilizável em `tools.py`, recebendo exclusivamente o cliente confiável já
criado pelo processo. Não será registrada no MCP nesta sprint; o registro
pertence à Sprint 9. A função não receberá settings, URL, token ou filtros
remotos arbitrários.

- query: string de 1–200 caracteres, não vazia após strip, sem caracteres
  Unicode de controle/formatação/surrogate; rejeição segura antes de HTTP.
- Busca por substring case-insensitive (casefold) em description,
  product_mask e sku. Sem regex, stemming, remoção de acentos, inferência
  semântica ou alteração dos valores retornados. Não promete match exato.
- max_results: inteiro estrito entre 1 e 1000, limitado também pelo teto
  configurado. Default local 20, não quota do fornecedor. Será orçamento
  de linhas recebidas/inspecionadas, não apenas de correspondências;
  duplicatas e linhas não correspondentes também consomem o orçamento.
- Reutilizar `_collect('products')`, acrescentando orçamento opcional por
  chamada sem modificar Settings ou estado compartilhado. Page size fixo
  min(50, orçamento efetivo), respeitando max_pages e deadline existentes.
- Aplicar o filtro ao resultado normalizado. JSON contém os campos atuais
  de QueryResult e contagens de coleta, com aviso fixo de busca local.
  returned_count conta matches; rows_received conta todas as linhas lidas.
- found/not_found somente se a coleta terminou de modo completo, salvo
  conflitos já tratados; coleta limitada/interrompida permanece partial,
  inclusive sem matches. Erro inicial mantém error, mesmo sem matches;
  erro posterior mantém partial e seu código, sem ocultar falhas.
- complete_dataset preserva o significado restrito de percurso do endpoint,
  não snapshot nem catálogo inteiro; filtro local é explicitamente descrito.
- IDs, Decimal, nulidade e proveniência seguem catalog.py; sem join preço/
  estoque, persistência, cache, LLM ou nova dependência.

## Gates e verificação

S6.01 revisará os critérios escritos de G0/G1 por operação, usando a
finalidade de consulta aceita em DEC-017 e a evidência real S5.01. Não
exigirá novo gate genérico de reaceite, permissões amplas ou instalação
limpa como pré-requisito inventado para pesquisa de produtos. A liberação
não se estende a preços/estoque/filtros adicionais ou tools MCP.

TDD offline no caminho real guardado: validações sem envio, filtro local,
limites por chamada, paginação, precisão/null, resultados vazios completos
versus sem matches parciais, erros iniciais/posteriores e serialização.
Manter stdio vazio e sem rede/LLM, imports sem configuração e pip check.

Validação autorizada: até duas consultas, page=1 e opcional page=2,
limit=1. Usar um termo derivado em memória da primeira amostra se disponível
para exercitar a função pública; nunca reter esse termo ou valores reais.
Não ultrapassar duas requisições somadas. Evidência apenas de estrutura,
contagens limitadas, resultado de invariantes e cleanup. Se o cenário não
permitir validar a função com esse orçamento, registrar o limite honestamente.

Atualizar somente documentação afetada e marcar cada tarefa com evidência;
comparar IDs, ordem e estados de outras sprints contra baseline público.
Não executar Git, instalar dependências nem alterar `.env`.
