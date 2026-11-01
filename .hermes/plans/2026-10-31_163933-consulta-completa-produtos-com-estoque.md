# Proposta de ampliação — produtos com estoque via MCP

Estado: proposta para análise e aprovação; não autoriza execução por si só. Nenhum código, configuração ou consulta real foi alterado/executado durante sua elaboração. A única escrita desta etapa é este plano. Aprovação prévia continua obrigatória para mudanças futuras, apesar da autonomia técnica concedida.

## Objetivo

Atender ao pedido de listar os óleos identificáveis no catálogo visível com quantidade conhecida maior que zero no estoque do usuário configurado. Evoluir o MCP de forma reutilizável para outras categorias, sem operação de escrita comercial, novos endpoints ou filtros remotos presumidos.

## Diagnóstico fundamentado

- `client.py:280-427`: `_collect()` começa sempre na página 1; limita até 1000 linhas/100 páginas por chamada; valida totais como travessia desde o início.
- `mcp_tools.py`: sete tools; `list_products` não aceita página inicial; estoque só é exposto como seleção local por um `reduced_id`.
- `config.py`: limites máximos de 1000 linhas e 100 páginas no processo. O cadastro Hermes foi deliberadamente restringido a 20 linhas/1 página na campanha anterior.
- A última busca retornou metadados de 19.699 registros visíveis. Com páginas de 50, esse catálogo demandaria 394 consultas se a contagem permanecer estável. O total atual do endpoint de estoque é desconhecido.
- A pesquisa é local. Aumentar apenas os limites não resolve o reinício na página 1, a coleta de estoque ou a completude entre chamadas.
- PRD atual não admite retomada nem join comercial no normalizador; qualquer revisão deve ser explícita e limitada ao novo fluxo. Não marcar sprints/global/V1 como concluídos por esta entrega.

## Abordagens para aprovação

A. Recomendada: paginação retomável em blocos pequenos, expondo catálogo e estoque por MCP; composição em memória por um consumidor MCP externo. Ampliar `list_products` com `start_page` e adicionar `list_inventory`, totalizando oito tools. Preserva limites por chamada, permite medir progresso e evita estado persistente no servidor. Exige que o consumidor reconcilie blocos, identidades e completude.

B. Uma única tool composta que varre catálogo e estoque por chamada. Interface mais simples, porém a leitura inteira pode ser longa, exceder deadlines e exigir estado de execução/retomada adicional. Adiar até haver necessidade que justifique essa complexidade.

Filtros remotos direcionados só serão considerados após suporte documental inequívoco; não são dependência nem premissa da abordagem A. Não usar banco/cache/sync persistente.

## Contrato proposto para A

- `list_products`: preservar parâmetros e padrões atuais; acrescentar `start_page` inteiro estrito, padrão 1, dentro da faixa já permitida ao HTTP. `page_size` deve ficar constante durante toda a campanha.
- Nova `list_inventory`: paginação tipada equivalente, somente operação interna stock. Não aceitar URL, método, tenant, depósito, credenciais ou body arbitrário.
- Cada resposta informa primeira/última página realmente aceita, próxima página ou fim, linhas recebidas e efetivos limites. Metadados de retomada não implicam snapshot estável.
- Separar conclusão do bloco de conclusão da travessia desde a página 1. Ler apenas um sufixo nunca pode declarar catálogo inteiro completo.
- Ajustar validação de totalElements para blocos com início posterior a 1: a contagem de um bloco não pode ser comparada como se fosse o acumulado global. O consumidor verifica reconciliação global.
- Erro preserva dados anteriores, código seguro e último progresso confirmado; sem retry automático. Retomada manual após falha exige decisão, não reenvio oculto.
- O consumidor acumula páginas em memória, verifica mudanças de totais, páginas repetidas, duplicatas e conflitos entre blocos. Só afirma travessia concluída quando as páginas e contagens permitem isso; estabilidade de totais não prova snapshot.
- Registrar a oitava tool e atualizar a allowlist Hermes somente após testes e aprovação deste escopo.

## Etapas de execução após aprovação

1. Atualizar o recorte de requisitos/decisão no PRD e documentação atual pertinente; preservar checklists históricos e critérios globais. Capturar baseline público sem acessar segredos nem Git.
2. Escrever regressões falhando em `tests/test_client.py` para início após página 1, limites fixos, metadados de sufixo, terminal vazio/contraditório, interrupção e isolamento concorrente. Implementar extensão mínima em `client.py` e metadados tipados em `catalog.py`.
3. Testar e ampliar `tools.py` com listagem de estoque e paginação de catálogo; preservar todas as funções existentes e o significado de max_results como linhas recebidas.
4. Testar e atualizar `mcp_tools.py`, `tests/test_mcp_tools.py`, `tests/test_mcp_stdio.py` e fixture sintética pertinente. Exigir exatamente oito tools, argumentos fechados e erros sem eco de entrada.
5. Criar um consumidor temporário em scratch usando ClientSession/stdio real, não funções privadas como atalho. Executar inicialmente com respostas sintéticas. O consumidor mantém o conjunto completo em memória e só escreve evidências estruturais por padrão.
6. Selecionar candidatos de óleo em uma única passagem no catálogo: comparação local sem diferença de acento/caixa para óleo/oleo e plural. Examinar descrições para separar óleo de filtro de óleo, bomba e acessórios; listar ambíguos à parte. Não inventar equivalência de marcas, unidades ou categoria estruturada.
7. Percorrer estoque uma vez, reconciliar por reduced_id exato, sem alterar zeros ou converter códigos comerciais. Conflitos de quantidade/identidade ficam pendentes, sem escolher valor arbitrário nem somar depósitos. Ausente/null é desconhecido; zero/negativo não entra em estoque positivo.
8. Produzir código comercial, descrição e quantidade positiva observada; não buscar preços nesta entrega. Informar quantidade de resultados, escopo do depósito, registros desconhecidos/conflitantes, período de observação e cobertura. Só usar a expressão 'todos' para os matches do universo visível percorrido, nunca para todo ERP ou óleos semanticamente não identificáveis.
9. Executar regressão completa, pip check e revisão independente de correção/segurança. Corrigir achados dentro do escopo aprovado e repetir testes relevantes.
10. Ajustar apenas o cadastro netone no Hermes para permitir a oitava tool e blocos de até 50 linhas/1 página, mantendo sampling desativado. Ler de volta configuração e verificar descoberta/protocolo.
11. Executar validação real e pedido comercial dentro do orçamento abaixo. Entregar produtos observados e relatório de limites; se interrompido, entregar resultado parcial explícito, não um total inventado.

## Validação e critérios de aceite

Comandos, após implementação:

- `.venv/Scripts/python.exe -B -m unittest discover -s tests -v`
- `.venv/Scripts/python.exe -B -m pip check`
- `hermes mcp test netone`

Testes sintéticos obrigatórios: defaults legados, validação antes de HTTP, origem/rotas/body fechados, acentos e plural, falsos positivos como filtro de óleo, IDs com zeros, quantidade Decimal positiva/zero/negativa/null/ausente, conflitos, totais mutáveis, repetição entre blocos, cortes de orçamento, cancelamento e fechamento concluído. Teste do consumidor deve provar que progresso e contagens vêm dos dados recebidos, não de índices presumidos. MCP deve executar catálogo e estoque por stdio real com respostas sintéticas antes do ERP.

Aceite real: consulta de página posterior a 1 por ambas as tools, união por identidade observada e relatório verificável de cobertura. Validação de bloco não substitui travessia completa. Nenhum sucesso antecipado se faltar estoque ou houver erro de coleta.

## Orçamento real proposto, sujeito à aprovação

- Loader privado somente na memória do servidor, com token existente e TLS verificado. Sem ler/exibir `.env` por ferramentas nem alterá-lo.
- Até 1.200 tentativas HTTP de leitura no total, incluindo validação inicial e campanha comercial; até 50 linhas por tentativa; somente os endpoints products e stock já admitidos.
- Um request por chamada de bloco, sem concorrência HTTP adicional, sem retry/redirect ou fallback. Manter 1 MiB por resposta e deadlines/cleanup existentes.
- Prazo global máximo proposto de 45 minutos. Limites de requests e prazo são tetos, não estimativas garantidas nem promessa de conclusão.
- Parar ao completar o trabalho, atingir teto, receber erro ou detectar inconsistência impeditiva. Se estoque for maior que o orçamento, informar a lacuna e propor complemento; não ampliar silenciosamente.
- Não consultar preços, login, refresh, rotas auxiliares ou outros sistemas.
- Produtos e quantidades são retornados ao operador; não entram em testes, docs públicas, logs ou memória persistente. Um arquivo comercial só será gerado mediante pedido do operador.

## Arquivos previstos

Modificar: `client.py`, `catalog.py`, `tools.py`, `mcp_tools.py`; testes existentes acima e testes de listagem de estoque em `tests/test_sprint8.py` ou novo arquivo específico após inspeção; `PRD.md`, `README.md`, `docs/api-capabilities.md`, `docs/security.md`, `docs/configuration.md`, `docs/runbook.md` e instruções atuais estritamente afetadas. Criar documentação de desenho/plano definitivo após seleção da abordagem. Nenhuma mudança de dependência é prevista.

Configuração externa: apenas chave mcp_servers.netone via CLI suportada; não editar configuração de outros MCPs/perfis. Sem commit, push, branch, instalação, alteração de .env, mutação ERP ou liberação V1.

## Decisão pendente

Aprovar abordagem A, registro de oito tools, atualização documental necessária, ajuste restrito do cadastro e orçamento real indicado; ou solicitar alterações. O detalhamento definitivo segue a abordagem escolhida. Nenhuma implementação foi iniciada.
