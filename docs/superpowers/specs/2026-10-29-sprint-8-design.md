# Sprint 8 — preço, estoque e listagem limitada

Estado: desenho/plano aprovados e executados. Sprint 8 concluída conforme PRD1.8.0/DEC-029 e evidências no runbook. BRL confirmado pelo mantenedor para esta instalação, não por campo observado na API. O orçamento descrito abaixo é histórico e está consumido/encerrado: cinco consultas HTTP200 page1/limit1, sem autorização de repetição. Nenhuma Sprint9 ou tool MCP liberada.

## Intenção e limites

Executar exclusivamente as tarefas abertas S8.01–S8.15 da seção 28 do PRD, preservando os estados de todas as outras sprints. Acrescentar consumidores de aplicação, não tools MCP. V1 permanece NOT_READY e o registry permanece vazio. Nenhuma alteração comercial no ERP é permitida.

O mantenedor escolheu a opção 1: manter os filtros HTTP atuais, selecionar preço/estoque por identidade exata localmente e listar uma página por padrão. Também autorizou consultas reais mínimas e limitadas, sem alterar o sistema. O orçamento operacional proposto abaixo integra esta aprovação, não renova probes anteriores.

## Abordagens

1. Escolhida: coleta page/limit existente e seleção local exata por identidade. Preserva o schema fechado e evita resolver por suposição o conflito de idsReduzidos do estoque. Custo: misses parciais não provam ausência global e o orçamento pode não alcançar um identificador conhecido.
2. Não escolhida: filtro remoto de ID somente para preços. Mais eficiente, mas ampliaria a superfície de filtros e exigiria sua própria evidência operacional. Não implementar nesta sprint.

Sem novos endpoints, filtros de preço/estoque, depósitos selecionáveis, joins, somas entre filiais, persistência, dependências, LLM, instalação ou comandos Git. Não ler, imprimir ou modificar .env nesta fase de desenho. Na validação real aprovada, leitura exclusivamente em memória pelo loader existente, sem modificar o arquivo. Não imprimir settings, origem, token, IDs ou registros reais.

## Evidência documental e segurança

O3/O4/O5 foram relidas anonimamente no navegador após hidratação em 29/10/2026:

- O3: https://net1ti.stoplight.io/docs/erp-api-v2/1eefaa8cb7cc6-busca-reduzidos
- O4: https://net1ti.stoplight.io/docs/erp-api-v2/47f2f0f5255d2-busca-estoque
- O5: https://net1ti.stoplight.io/docs/erp-api-v2/79683209728d7-busca-precos

O5 publica preço varejo/atacado, descrições das tabelas e identidades. Não publica moeda ou preço final com descontos. O4 descreve retorno de saldo físico menos reservas, usando o depósito parametrizado do usuário quando omitido; não identifica esse depósito na resposta publicada. O conflito de idsReduzidos (number no schema, array no exemplo) permanece, portanto nenhum formato será enviado. O3/O4/O5 publicam page/limit e metadados de paginação; quotas e snapshot não são comprovados.

DEC-017 já aceita a finalidade documental de consulta com risco residual de efeitos internos não documentados. A implementação só executará esses POSTs de consulta existentes, sem payload ou chamada de reserva/movimentação. S8.06 deve registrar essa evidência e seus limites, nunca alegar prova absoluta dos efeitos internos. Evidência de mutação ou necessidade de operação não admitida interrompe o caminho; não contornar.

## Contratos de aplicação propostos

Todas as funções retornam dict JSON compatível com QueryResult, preservando normalização, Decimal como string, missing_fields, status, error, warnings, retrieved_at, métricas e complete_dataset. Não registrar em server.py.

### Preço

`get_product_price(client: NetOneClient, product_id: str, max_results: int = 20, *, currency: Literal['BRL'] | None = None) -> dict[str, object]` (async).

- product_id é identidade normalizada textual exata, 1–256 caracteres, não whitespace-only e sem categorias Unicode C; não converter, strip ou remover zeros. Diferente do inteiro exigido pelo filtro remoto de get_product_details: aqui não há filtro remoto.
- max_results inteiro estrito 1–1000/default20, limitado pela configuração e contando todas as linhas recebidas.
- Coletar prices somente com page/limit e selecionar record.product_id == product_id. Preservar todos os reduzidos e conflitos; nenhum fallback por mascara/SKU.
- Discriminar `local_exact_product_id_price_search` e `nominal_prices_not_final_quote` em warnings; acrescentar `currency: 'BRL'`, `currency_source: 'operator_confirmation'` e `price_kind: 'source_retail_and_wholesale'` no envelope, não em cada DTO. BRL é contexto confirmado pelo mantenedor para esta instalação, não moeda retornada pela API nem garantia para instalações de terceiros; não alterar Settings ou .env. Como o repositório é reutilizável, a função recebe `currency: Literal['BRL'] | None = None` keyword-only, de integração confiável, não de argumento MCP. None retorna currency null, currency_source null e warning currency_unknown. A validação real nesta instalação fornece explicitamente BRL; outros valores são rejeitados antes de HTTP. Nenhuma conversão monetária é realizada.
- price/price_table e wholesale_price/wholesale_price_table são campos de origem, não escolha de tabela nem cálculo. Null/ausente não viram zero. `found` indica identidade encontrada, não garante preço preenchido; avisar `price_missing` se um match não tiver nenhum dos dois valores.

### Estoque

`check_inventory(client: NetOneClient, reduced_id: str, max_results: int = 20) -> dict[str, object]` (async).

- Mesma validação de string e orçamento; comparação exata exclusivamente com record.reduced_id. Não coagir identificador inteiro/textual nem inferir idProduto ausente.
- Coletar stock somente com page/limit. Warning `local_exact_reduced_id_stock_search`.
- Envelope adicional `inventory_scope: {'selection': 'configured_user_deposit', 'deposit_id': null, 'branch_id': null, 'quantity_basis': 'physical_minus_reservations'}`. Contexto publicado, não identidade do depósito observada.
- `last_changed_raw` permanece por item sem conversão, e retrieved_at é instante local de coleta, não frescor do estoque. Avisar `inventory_scope_unverified` e `inventory_freshness_unverified`.
- Quantity zero, negativo, null e ausente continuam distintos; nenhum saldo agregado ou promessa de venda/reserva/entrega. Se um match tiver quantity null, avisar `quantity_missing`; found não significa disponibilidade.
- Não adicionar campos brutos/desconhecidos ou nova projeção de depósito/timestamp por especulação.

### Listagem

`list_products(client: NetOneClient, max_results: int = 20, *, page_size: int | None = None, max_pages: int = 1) -> dict[str, object]` (async).

- Começa sempre em page1. Não aceita cursor, página inicial, filtro arbitrário ou consulta automática de todas as páginas.
- max_results estrito 1–1000; max_pages estrito 1–100; page_size quando fornecido estrito 1–1000 e deve caber no orçamento efetivo de linhas, como no coletor existente. None usa min(50, orçamento efetivo).
- Acrescentar apenas max_pages opcional keyword-only ao coletor privado: None mantém comportamento anterior; valor informado limita min(max_pages, configuração). Validação antes de HTTP, nenhum estado compartilhado alterado. _query e filtros permanecem inalterados.
- Default20/max_pages1 limita a uma requisição; mais páginas exigem escolha explícita do chamador e continuam sob os tetos configurados. Não mudar limit entre páginas.
- Retornar o resultado de products sem reclassificar ausência/erro e avisar `provider_visible_catalog_only`; percurso completo não é catálogo ERP global nem snapshot.

## Implementação e padrões

- tools.py: funções públicas e reutilização de _validate_code_input/_filtered_result, mantendo mensagens fixas e precedência de partial/error mesmo quando a seleção remove todos os itens.
- client.py: somente extensão do teto de páginas por chamada em _collect, com validação e isolamento. Nenhuma mudança de allowlist, autenticação, TLS, redirects, retries, streaming, limites de bytes ou cleanup.
- catalog.py/config.py/server.py/requirements.txt: sem mudanças previstas.
- tests/test_sprint8.py: testes sintéticos pelos consumidores reais e MockTransport, seguindo helpers existentes; testes adicionais focados em client.py quando necessário.
- PRD.md, README.md, docs/api-capabilities.md, docs/runbook.md e AGENTS.md: reconciliar o estado e os contratos efetivamente aprovados/verificados. Edição protegida somente pelo mecanismo normal; recusa/timeout não autoriza outro caminho.
- Código/docs públicos em inglês; desenho/plano/PRD em pt-BR. Python >=3.14,<4, uma .venv, sem novas dependências, aspas simples e type hints.

## Evidência offline exigida

Testes RED antes de implementação e GREEN após cada unidade. Exercitar tipo/bounds/Unicode C/zeros/significant spaces sem HTTP; routes/bodies page/limit exatos; Decimal longo sem float, null/ausente/zero/negativo; todos os reduzidos de produto; correspondência de campo exato; erro antes/depois de linhas inclusive sem match; metadata ausente/contraditória; duplicatas/conflitos; budgets de páginas/linhas, tamanho fixo e concorrência sem mutação; fechamento completo dos streams; JSON e ausência de dados sintéticos sentinela em erros. Stock não deve inferir disponibilidade; currency BRL exige confirmação explícita do operador, sem conversão; default permanece desconhecido para reuso genérico.

Executar `.venv/Scripts/python.exe -B -m unittest discover -s tests -v`, `.venv/Scripts/python.exe -m pip check`, revisão independente do conjunto e auditoria programática dos IDs/estados de checklist contra baseline público, sem Git. Stdio deve continuar com registry vazio e sem rede ou leitura real de .env.

## Validação real delimitada proposta

A executar uma única vez, apenas após aprovação deste desenho/plano, testes e revisão sem achados importantes:

1. Uma consulta prices page1/limit1 para obter identidade válida em memória.
2. Uma chamada real get_product_price com essa identidade, max_results1 e currency='BRL': no máximo uma consulta prices page1/limit1.
3. Uma consulta stock page1/limit1 para obter identidade válida em memória.
4. Uma chamada real check_inventory com essa identidade e max_results1: no máximo uma consulta stock page1/limit1.
5. Uma chamada real list_products(max_results=1, max_pages=1): no máximo uma consulta products page1/limit1.

Teto global: cinco tentativas de envio e cinco linhas recebidas; no máximo duas prices, duas stock e uma products. Uma tentativa que falha consome sua alocação; nenhuma repetição, descoberta adicional ou chamada condicional reaproveitada. Amostra vazia/identidade inutilizável impede a chamada dependente e mantém sua aceitação pendente. Falha de autenticação/TLS/guarda/segurança encerra o probe sem login ou correção automática. Manter guards existentes, TLS verificado, zero retries/redirects e cleanup shielded.

Dados comerciais, origens e segredos somente em memória. Persistir exclusivamente nomes previamente aprovados de campos, categorias de presença/tipo, contagens de envios/status/linhas/matches, estados partial/error e invariantes de identidade/Decimal/JSON/cleanup. Não reter payload ou identificadores mesmo em scratch. Registrar consumo e encerramento do orçamento; a evidência comprova apenas essas amostras, não paginação real ampla ou semântica interna do ERP.

## Aceite e pendências

Marcar apenas S8.xx comprovadas. S8.14 depende dos consumidores reais e seus invariantes, não de mocks. Se qualquer critério exigir evidência indisponível, deixar aberto com bloqueio específico; não alterar seu texto para fingir sucesso. Não alterar checkboxes globais ou tarefas de outras sprints. S8.15 registra moeda BRL confirmada pelo operador para esta instalação (não pela API), depósito/filial desconhecidos, conflito do filtro recusado e ausência de suporte a estimativas/preço final. Sprint 9, registro MCP, análises e release permanecem fora do escopo.

Escolhas menores acima (assinaturas, warnings/envelopes, IDs textuais locais, max_pages por chamada) são propostas técnicas do agente, não decisões previamente expressas pelo mantenedor. Aprovação deste documento as torna o contrato de implementação; o plano detalhará a sequência sem ampliar a autorização.
