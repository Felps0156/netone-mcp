# Sprint 7 — Detalhes por ID e códigos exatos

> Desenho e critério de aceite originais, preservados como histórico.
> PRD 1.7.0 / DEC-027 registra o encerramento posterior com ressalva
> explícita: codigoSku técnico continua sem validação real; S7.11 foi
> revisada por aceite do mantenedor, não por substituição pela máscara.

## Intenção e decisões do mantenedor

Executar somente S7.01–S7.12 do PRD, preservando tarefas anteriores e
posteriores. O mantenedor escolheu ID remoto + SKU/EAN exatos locais e
limitados. Autorizou até quatro consultas de produtos com limit=1, sem
retries: descoberta em memória e até uma por função implementada. Isso
não autoriza login, rotação, alteração do .env, banco ou registro MCP.
Desenho aprovado pelo mantenedor após builder check independente sem
questões importantes em aberto; execução depende da revisão do plano.

## Evidência e situação atual

PRD 1.3.0; Sprints 5/6 concluídas; registry vazio; baseline executada:
74 testes PASS, pip check PASS, Python 3.14.3. HTTPX/normalização/coleção
já protegem origem, método, body, TLS, bytes, tempo, páginas, linhas,
precisão, erros e cleanup. search_products faz substring casefold local.

O3 relida anonimamente após renderização em 29/10/2026:
https://net1ti.stoplight.io/docs/erp-api-v2/1eefaa8cb7cc6-busca-reduzidos
POST /app-web/api/v2/produto/reduzidos documenta idsProdutos:
array[number] para ID do produto; o retorno define idProduto como integer.
Não documenta filtros codigoSku/ean nessa consulta; ambos são campos do
retorno. mascara não é sinônimo comprovado de codigoSku. Universo ainda
restrito pelo fornecedor a ecommerce ativo/tabelas do vendedor.

## Alternativas consideradas

1. Escolhida: ID remoto com filtro documentado, SKU/EAN por igualdade local
   sobre coleta limitada. Entrega códigos exatos sem prometer busca global.
2. Somente ID remoto, sem implementar SKU/EAN. Mais restritiva; descartada
   pelo mantenedor em favor de comparação local explicitamente limitada.
3. Não elegível no escopo atual: catálogo persistente sincronizado ou
   filtros remotos inventados. Banco/sync proibidos; não antecipar Sprints
   8/9 ou a discussão futura de busca ampla.

## Interfaces e validação propostas pelo coordenador

Funções de aplicação assíncronas em tools.py, sem decoradores/registro:

- get_product_details(client, product_id: int, max_results: int = 20).
- search_product_by_sku(client, sku: str, max_results: int = 20).
- search_product_by_ean(client, ean: str, max_results: int = 20).

client é o NetOneClient confiável do processo, nunca argumento do modelo.
product_id é inteiro estrito (sem bool/subclasse/coerção), 0 até
9223372036854775807. É teto defensivo local de 64 bits, não limite oficial.
Strings, inclusive IDs com zeros à esquerda, são rejeitadas em vez de
normalizadas silenciosamente. IDs retornados mantêm a normalização atual.
Não selecionar idReduzido como se fosse idProduto.

SKU/EAN: strings de 1–256 caracteres, não vazias após strip e sem Unicode
categoria C. Validação não transforma o valor: comparação exata, sensível
à caixa, espaços, hífens e zeros; sem cast numérico, casefold, substring,
regex, remoção de acentos ou validação de checksum/GS1 não documentada.
Os campos de origem permanecem intactos; null/ausente não corresponde.

max_results: inteiro estrito 1–1000, default 20, limitado por Settings;
conta linhas recebidas, inclusive não matches/duplicatas. Invalidar todo
input antes de HTTP com mensagens fixas sem ecoar valores.

## Integração e transporte

Adicionar somente product_id opcional keyword-only ao coletor e _query.
Só products aceita esse parâmetro; rejeitar uso em prices/stock. O body
continua construído internamente: page/limit e, quando presente,
idsProdutos=[product_id]. Nenhum dict de filtros público/genérico, novos
paths, idsReduzidos, mascara, codigoSku ou ean no body. Manter todos os
limites, paginação fixa e guardas; orçamento/filtro isolados por chamada.
Omitir o parâmetro preserva exatamente os requests existentes.

O coletor valida que todos os registros de uma página filtrada possuem
product_id normalizado igual a str(product_id), antes de aceitar a página.
Se a API ignorar o filtro ou devolver outra identidade, invalid_response;
não apresentar produtos alheios ou concluir sucesso vazio. Reduzidos
distintos do mesmo produto sobrevivem; não escolher arbitrariamente um.

SKU/EAN usam _collect('products', max_results=...) sem filtro remoto.
Reutilizar normalização/serialização e um pequeno helper de filtro/estado
se evitar duplicação real; não criar framework, módulo vazio ou alterar
semântica da pesquisa textual existente.

## Retorno e ausência

Mesma projeção JSON de QueryResult, Decimal string e metadados existentes.
Details devolve o conjunto limitado de reduzidos do produto, não o JSON
bruto nem uma promessa de produto completo/preço/estoque atualizado.
SKU/EAN acrescentam respectivamente local_exact_sku_search e
local_exact_ean_search, distinguindo-os de local_text_search da Sprint 6.
Não devolver o código consultado como metadado extra.

Erros/parcialidade do coletor prevalecem mesmo sem matches. Só coleta
válida completa permite found/not_found no universo visível consultado.
Sem match em amostra limitada é partial, nunca ausência global.
Campos ausentes/null preservados; HTTP404 segue erro de endpoint.
Cancelamento propaga; cleanup preserva falha original e tem teto atual.

## Verificação e aceite

TDD via unittest/MockTransport: validação sem envio; body fechado e
restrito a products; filtro constante em páginas/concorrência e sem
mudança de defaults; filtro ignorado rejeitado atomicamente; vários
reduzidos; exatidão SKU/EAN com zeros/case/hífens/espaços e sem campo
alternativo; null/ausência; erro/partial/vazio; JSON/Decimal; regressão
search_products; stdio com registry vazio e sem rede/LLM.

Prova real em scratch, uma execução depois da suíte: até quatro envios
page=1/limit=1 em products, guardas mantidas. Descoberta inicial obtém
ID/SKU/EAN apenas em memória. Uma chamada por função com dado utilizável;
SKU/EAN ausentes/null/inválidos ficam como validação real não demonstrada,
sem outra descoberta ou termo inventado. Não converter ausência de dado
em sucesso operacional. Reter apenas contagens/status/tipos/invariantes,
sem IDs, códigos, descrições, host, segredo, payload ou exceção bruta.
Nenhum orçamento remoto é renovado automaticamente em falha.

Atualizar PRD/decisão para registrar o schema específico novo e separar
suporte offline de evidência real por função. S7.11 só fica [x] se a
validação manual aplicável estiver comprovada; se faltar amostra de código,
registrar precisamente a parcela pendente. S7.12 é verificação de registry
vazio, não autorização para registrar tools. Marcar demais tarefas somente
com evidência; não mudar tarefas de sprints diferentes ou aceite V1.

Revisões independentes e auditoria pública por snapshots/diffs, sem Git,
instalações ou .env. Documentação pública em inglês; PRD/planos pt-BR.
