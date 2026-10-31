# Sprint 13 — Desenho da validação final offline e operacional

Data: 2026-10-31.
Estado: desenho aprovado expressamente pelo mantenedor, incluindo o ajuste
de VM11; plano e execução nativa posteriormente aprovados. Revisão independente
do desenho: nenhuma lacuna importante para elaboração do plano.
Fonte de verdade: PRD 1.12.0, seção 28, S13.01–20, matriz VM01–VM20 e
critérios globais das seções 26/30.

## Intenção e autorização atual

Demonstrar o comportamento existente com evidências atuais, distinguindo
regressão sintética, instalação limpa e aceite operacional. Não reconstruir
funcionalidades já aceitas nem converter evidências históricas em novas provas.

O mantenedor solicitou Sprint13 e aprovou a abordagem2: revisão restrita do
escopo, desenho/plano para aprovação, fase offline e permissões específicas
para instalação e consulta real. O mantenedor aprovou posteriormente este
desenho, incluindo o ajuste de VM11, para elaborar o plano. Isso não autoriza
instalação, leitura da configuração privada ou envio ERP. A restrição
anterior de exclusão de13 será supersedida apenas pelo recorte posteriormente
aprovado e documentado. Nenhum orçamento histórico é reaberto.

Até aprovação do desenho/plano: somente inspeção pública, snapshot público,
desenho e revisão. Nenhuma tarefa S13 está concluída por este documento.

## Contexto observado

- Sete módulos de produção na raiz, treze arquivos Python em tests e cinco
  pins diretos no manifesto. Não há src/ ou necessidade de criar outra camada.
- config.py é o único loader. load_config lê o .env raiz mesmo com overrides
  de processo; testes offline precisam substituir o leitor ou usar Settings
  sintéticas. Não iniciar server.py diretamente como verificação offline.
- server.create_server preserva stdio, logging seguro e um cliente por lifespan.
  mcp_tools mantém sete entradas strict/extra-forbid, erros fixos e equivalência
  structuredContent/texto JSON. Análises e busca ampliada não são tools MCP.
- client._query constrói corpos fechados para três POSTs, mantém guarda de
  destino, TLS, zero retries/redirects e limites de bytes/páginas/linhas/prazo.
  _collect retém erros/parcialidade e tamanho fixo de página.
- catalog preserva identidade textual, Decimal exato, ausência/null/zero/false.
  analysis agrega por identidade reduced_id não conflitante; desconhecido não
  vira zero, não há soma entre depósitos/unidades ou conclusão global de amostra.
- README/runbook registram195 testes em checkpoints anteriores. A contagem e
  o resultado desta sprint só serão declarados após execução atual.
- Baseline público criado em managed scratch:61 arquivos; vinte tarefas S13
  abertas. Não contém .env, .git, ambientes ou respostas comerciais.

## Objetivos, exclusões e antiobjetivos

Objetivos: matriz assinável VM01–20 com PASS/FAIL/BLOCKED, evidência por tarefa,
regressão real do código existente, interoperabilidade SDK/stdio, demonstração
sintética das análises, instalação limpa autorizada e uma consulta operacional
mínima autorizada. Cada PASS descreve o universo que realmente foi observado.

Não objetivos: novas tools/filtros/rotas, framework, atualização de dependência,
Git/worktree/commit/publicação, cliente permanente Hermes, login/rotação,
mutação ERP, alteração do .env, stress test ou validação de todas as tools reais.

Antiobjetivos: marcar instalação existente como limpa; transformar mock em ERP;
forçar401/403/429 no fornecedor; repetir chamada consumida para consertar prova;
apagar histórico; declarar V1 por contagem de checkboxes; imprimir dados privados.

## Abordagens consideradas

1. Somente offline no ambiente existente: preserva acesso fechado e prova os
   controles locais, mas não satisfaz S13.02 nem S13.11 operacional.
2. Validação em fases com permissões separadas: escolhida pelo mantenedor.
   Reaproveita testes, registra limites e admite apenas ações operacionais
   específicas após revisão. Custo: instalação/configuração/ERP podem permanecer
   BLOCKED enquanto suas permissões ou condições não forem satisfeitas.
3. Recriar o ambiente ou executar a matriz inteira contra ERP: rejeitada por
   risco desnecessário, perda do ambiente existente e testes remotos agressivos.

## Fases e fronteiras de aprovação

### A — Offline no ambiente existente

Após aprovação do plano: usar explicitamente .venv/Scripts/python.exe,
inspecionar versão e pins, rodar unittest discover e pip check sem instalação.
Fresh imports com leitura .env/construção HTTP/rede proibidas; stdio com loader
sintético e envio HTTP externo bloqueado. Preservar socketpair interno Windows.

Executar os cenários reais da aplicação com transporte em memória, não mocks
das funções comerciais. Reutilizar testes existentes e demonstrações limitadas
para vazio/permissão,429/timeout, fidelidade/paginação e análises. Observar
cleanup concluído inclusive cancelamento, não apenas is_closed. stdout sempre
protocolar, stderr saneado inclusive DEBUG/protocolo inválido.

Probes e logs sintéticos ficam em managed scratch. Não instalar ferramentas de
lint ou atualizar pins. Não refatorar dívida preexistente de linhas longas.
Se surgir falha, diagnosticar; correção mínima passa por regressão que falha e
escopo explícito antes de mudança de comportamento. Mudança arquitetural ou
sensível não está implicitamente autorizada por esta validação.

### B — Instalação limpa, somente com autorização específica

Escolha técnica proposta pelo autor, ainda não aprovada: um ambiente temporário
limpo em managed scratch, com intérprete compatível explicitamente inspecionado,
instalação somente do requirements.txt atual, pip check, imports e regressão
completa offline nesse intérprete. Não copiar .env nem configurações privadas.

Isso requer exceção expressa à regra de ambiente único exclusivamente para o
probe temporário, fora do projeto. A única .venv do projeto permanece intacta;
sem instalação global, alteração de pins ou substituição do ambiente existente.
Registrar intérprete/plataforma, versões diretas e resultados, sem alegar lock
transitivo, validação macOS/Linux ou vulnerabilidades ausentes.

Não criar esse ambiente ao aprovar apenas o desenho/plano. Se a exceção não for
aprovada, S13.02 permanece aberta/BLOCKED; pip check no ambiente existente não a
substitui. A remoção do ambiente temporário deve limitar-se ao diretório criado
pela execução, após registrar evidência sanitizada; nunca remover .venv raiz.

### C — Configuração e prova real, permissões independentes

Proposta mínima para aprovação posterior:

- Leitura privada: uma invocação de load_config pelo processo do servidor para
  a prova, somente em memória; sem exibir/serializar Settings, hosts, token,
  ambiente, conteúdo ou checksum do .env. Sem escrita/movimentação. Se falhar,
  registrar diagnóstico fixo e pedir nova autorização antes de nova leitura.
- ERP: uma única tentativa POST /app-web/api/v2/produto/reduzidos, corpo exato
  page=1/limit=1, via list_products MCP com max_results=1/page_size=1/max_pages=1.
  Sem chamada de descoberta ao ERP. initialize/tools-list não fazem HTTP.
- Cliente SDK genérico por stdio, servidor existente e guardas originais.
  Instrumentação em memória acrescenta restrição de rota/body/uma tentativa;
  não remove guardas, não substitui transporte real nem altera arquivos produto.
- Retenção: somente horário do teste, status/códigos fixos, contagens e booleanos
  de fidelidade, equivalência JSON e cleanup. Registros, valores comerciais,
  origem, credenciais e chaves desconhecidas ficam somente em memória.
- Um marcador exclusivo antes da tentativa impede replay; registrar consumo
  duravelmente no runbook, inclusive falha/interrupção. Não renovar orçamento
  por timeout/401/403/429/5xx ou coleta vazia. Não redistribuir uma tentativa.
- Validar o probe offline antes: sucesso, corrupção Decimal/null detectada e
  falha após recebimento com métricas preservadas. Comparar projeção com a
  própria resposta do consumidor em memória, não com outra consulta anterior.
- Observar conclusão de fechamento de resposta, transporte e cliente após
  encerrar sessão/processo. Falha de cleanup não é aprovação operacional.

Uma resposta vazia válida é observação legítima; não prova consulta comercial
útil com dados nem fidelidade monetária. Nesse caso S13.11 deve registrar o
alcance e permanecer sem aceite completo se não cumprir o critério; não repetir.
Preço/estoque permanecem sintéticos nesta sprint mínima, sem alegar nova prova
real desses endpoints. Qualquer expansão exige orçamento separado.

### D — Revisão e reconciliação

Revisão independente da evidência, diffs públicos e matriz. Corrigir achados
relevantes dentro do escopo, repetir só verificações offline, nunca o probe real
consumido. Atualizar PRD/README/runbook/instruções atuais pela ferramenta normal,
preservando histórico e limites. Atualização protegida recusada/expirada exige
parada, sem bypass. Planos históricos não ganham autorização retroativa.

## Mapeamento de aceite por tarefa

| Tarefa | Evidência requerida e limite |
|---|---|
| S13.01 | Versão exata do intérprete raiz realmente executado; não Python de PATH. |
| S13.02 | FaseB limpa autorizada e verificada; ambiente existente não basta. |
| S13.03 | Imports dos sete módulos sem configuração/rede/output/efeito colateral. |
| S13.04 | Loader sintético +, para aceite operacional, leitura privada autorizada e resultado saneado; não mostrar valores. |
| S13.05 | Entrypoint sem configuração obrigatória sintética: exit1, stdout vazio e diagnóstico fixo. |
| S13.06 | initialize e resposta MCP por stdio em processo real com configuração sintética. |
| S13.07 | Parsing de todas as linhas stdout como protocolo e sentinelas ausentes de stderr/replies; logs DEBUG e protocolo malformado. |
| S13.08 | Descoberta exatamente igual ao registry aprovado de sete entradas. |
| S13.09 | Schemas fechados/strict sem escrita, URL/método/token/tenant e nenhuma candidata indevida. |
| S13.10 | Entradas inválidas, extras e limites combinados recusados com zero sends. |
| S13.11 | FaseC autorizada e observada, sem alegar cobertura de outras tools/rotas. |
| S13.12 | Cenários sintéticos separados de vazio terminal válido e403, incluindo404 como erro de endpoint; não provocar falha real. |
| S13.13 | Demonstração manual sintética429/timeout pelo consumidor existente; tentativa única, erro/parcialidade e cleanup. Sem stress remoto. |
| S13.14 | IDs/Decimal/null/ausência/zero no pipeline sintético; produtos reais comparados com sua própria resposta se autorizados. Preço/estoque reais novos não inferidos. |
| S13.15 | Paginação sintética multi-page, limites e erros após dados; página real única nunca prova paginação remota completa. |
| S13.16 | Chamar ambas as análises reais da aplicação com transporte sintético; confirmar universo, duplicatas/conflitos e suficiência. Não registrar tools. |
| S13.17 | Cliente SDK genérico/stdin-stdout, sem chaves LLM/frameworks; sem instalar integração permanente. |
| S13.18 | Auditoria do conjunto público explícito e logs de prova saneados; não ler .env/índice/histórico ou alegar detecção universal. |
| S13.19 | Vinte linhas VM01–20, cada uma com estado, comando/cenário, prova e limitação/ação pendente. |
| S13.20 | Achados corrigidos ou bloqueios explicitados; não anunciar aceite final enquanto requisitos faltarem. |

## Matriz VM e ajuste pontual proposto

### Cobertura existente a reutilizar, ainda sem execução nesta sprint

- tests/test_mcp_stdio.py:test_generic_stdio_client_discovers_executes_and_closes
  e test_generic_stdio_default_search_reaches_second_page: SDK genérico/stdin-
  stdout, payload e cleanup, primeira página e busca posterior sintéticos.
- tests/test_mcp_tools.py:test_all_registered_consumers_use_guarded_closed_queries,
  test_invalid_inputs_are_safe_and_never_send e
  test_empty_partial_and_upstream_errors_remain_distinct: consumidores reais,
  rejeição pré-envio e distinção entre vazio, parcialidade e erro.
- tests/test_client.py:test_http_errors_never_retry_or_follow_redirects e
  test_total_deadline_is_distinct_from_phase_timeouts: tentativas limitadas e
  erros sintéticos, nunca prova de rate limit/timeout remoto.
- tests/test_config.py:test_import_does_not_read_environment_file e
  tests/test_analysis.py:test_analyses_need_no_configuration_read_or_llm_key:
  pontos de partida para isolamento; não substituem fresh imports de todos
  os sete módulos nem a demonstração das duas análises.
- tests/test_server.py contém stdio real com loader substituído e HTTP proibido.
  Seu teste de erro de configuração injeta ConfigurationError: complementar
  S13.05 chamando o entrypoint com o loader real e leitor/ambiente sintéticos
  sem valores obrigatórios, não apenas repetindo a exceção injetada.

A revisão estática não executou testes. Instalação limpa, versão do intérprete,
auditoria pública/.gitignore e a matriz final requerem verificações próprias.
Em partial com erro posterior, isError pode ser false: conferir também status,
error, partial e complete_dataset do conteúdo estruturado.

VM01–08: runtime, imports, configuração/erro, stdio/discovery, ausência de escrita
e rejeição pré-HTTP. VM09: exclusivamente prova real da faseC, BLOCKED sem ela.
VM10/12–16: HTTP401/403/429/timeout/5xx/JSON/paginação/campos exercitados em
transporte sintético; registrar explicitamente essa origem. VM17: ambas as
análises sintéticas. VM18: sem LLM. VM19: leitura de padrões .gitignore, não
inspeção Git. VM20: documentos públicos e stderr, não arquivos privados.

Há contradição preexistente em VM11: PRD exige not_found para a linha conjunta
HTTP404/resultado vazio, enquanto seção17 e client tratam404 como erro de
endpoint. Proposta para aprovação deste desenho: revisar somente VM11 para
separar vazio válido terminal → not_found de HTTP404 → error com código seguro
not_found, sem confundir erro de endpoint com produto ausente. Preservar a regra
correta do código; não alterar produção para satisfazer uma descrição ambígua.
Registrar a redação anterior na nova decisão. Nenhum outro critério é dispensado.

## Evidência, estado e conclusão

O runbook será o ledger central em inglês, com matriz VM e referências por
S13; desenho/plano e PRD permanecem pt-BR. Cada resultado guarda origem
synthetic/existing-environment/clean-install/real, comando e limites. Falha de
harness não é falha ERP nem PASS; registrar e corrigir offline.

Somente marcar [x] na tarefa após seu próprio aceite. Comparar os tuples
ordenados (id,texto,estado) ao baseline por código; preservar todas as sprints
alheias, tarefas já concluídas e texto/ordem, salvo ajuste VM11 explicitamente
aprovado. Critérios globais/DoD não serão marcados em massa. Uma eventual
aprovação individual deles requer evidência correspondente e registro separado.

G6 depende de critérios globais atendidos; registrar bloqueios não os torna
verdadeiros. Preservação do .env nesta execução não comprova igualdade com
original histórico, que não foi retido para comparação. Não fabricar essa
prova. S13.19/20 podem ter evidência de matriz/bloqueios sem concluir a sprint.
V1 continua NOT_READY até aceite efetivo; publicação/licença e ações Git
continuam separadas, sem adicionar exigências inventadas a cada teste local.

## Decisões delegadas ao implementador e pendências do mantenedor

Implementador: composição de probes temporários, reutilização de fixtures,
nomes internos e agrupamento de verificações; comandos limitados ao escopo
aprovado. Sem dependências novas ou alteração especulativa de produto.

Mantenedor: aprovar este desenho (incluindo ajuste VM11), depois o plano;
autorizar separadamente exceção de ambiente temporário/instalação, leitura
privada e tentativa ERP/retencão propostas. Recusa mantém o item BLOCKED, não
concede permissão alternativa. A aprovação desta abordagem não aceita exceção
à instalação limpa, prova real ou critérios globais.
