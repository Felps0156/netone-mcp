# Consultas direcionadas de estoque e preço — plano de execução

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** eliminar a consulta de prefixos não filtrados para identidades numéricas canônicas em check_inventory/get_product_price, com testes exclusivamente simulados.

**Architecture:** reutilizar tools.py → client._collect → client._query e catalog.py sem nova camada/dependência. Acrescentar reduced_id inteiro privado para stock; ampliar product_id privado para prices. Preservar paginação filtrada, validação atômica e todos os limites existentes.

**Tech Stack:** Python >=3.14,<4; unittest, HTTPX/AnyIO/Pydantic nos pins existentes.

**Spec:** solicitação direta do mantenedor nesta execução; PRD.md, extensão DEC-038. O mantenedor delegou escolhas e execução sem checkpoints intermediários. O plano inicial abaixo era exclusivamente offline; a autorização posterior separada e seu consumo real estão no fim do ledger, sem renovar qualquer orçamento antigo.

## Desenho e alternativas

A causa é a coleta page/limit sem identidade antes da igualdade local. Aumentar caps ou percorrer985 páginas não resolve o custo nem é necessário. Cache/join/banco adicionariam arquitetura e estado sem necessidade. Escolha do executor: filtro remoto mínimo na rota já existente, sem novo endpoint, filtro arbitrário ou tentativa de outro formato após erro.

Preços: O5 publica idsProdutos:array[number]. Estoque: O4 e o OpenAPI original mantêm schema number/exemplo array; a coleção Postman oficial também usa array. Escolha provisória do executor: singleton array seguindo os exemplos oficiais, sem alegar resolução pelo fornecedor ou prova operacional. Nunca chamar ERP para resolver a dúvida nesta execução.

IDs textuais atuais são preservados. Strings canônicas ASCII `0|[1-9][0-9]*`, até9223372036854775807, podem ser codificadas sem perda como inteiros. Valores canônicos acima do teto são rejeitados antes do envio. IDs não canônicos, incluindo zeros significativos, continuam no caminho exato local limitado por compatibilidade, explicitado por lookup_strategy e aviso; nunca são normalizados nem usados como fallback após falha remota. As identidades vindas da API continuam inalteradas. Os limites originais de string1–256 e max_results1–1000/default20 permanecem.

Um filtro de stock só aceita reduced_id inteiro; product_id não é admitido em stock. Um filtro de prices só aceita product_id; reduced_id não é admitido em prices. Products mantém ID OU mascara. Validar em _query e _collect antes de HTTP. Uma identidade diferente rejeita toda a página, retendo apenas páginas válidas anteriores. Percorrer somente páginas filtradas dentro dos caps; não parar no primeiro match de preço, pois pode haver variantes/tabelas. Sem depósito/modelo/tenant selecionável.

Zero recebido permanece Decimal/string zero; null/ausente é desconhecido (quantity_missing); vazio terminal válido é not_found no universo visível filtrado, não estoque zero. Corte/metadados insuficientes/conflitos mantêm partial; erro nunca vira ausência. Identidade encontrada não garante campo populado. complete_dataset refere-se ao percurso consultado, não ao catálogo ERP.

## Global Constraints

- Não acessar .env/configuração privada, ERP, login/rotação, Git, instalações, publicação ou cadastro Hermes.
- Preservar oito tools, assinaturas/defaults públicos, limites, allowlist literal, TLS/Host/origem,1MiB, identity, zero retries/redirects/fallback, erros seguros, cancelamento e cleanup.
- Código/docs públicos em inglês; PRD/plano pt-BR. Sem nova dependência, módulo de produção ou persistência.
- Manter checklists de sprints/aceite global byte-equivalentes em tuplas ordenadas; trabalho anterior já presente não pertence a este recorte.
- Os identificadores expressamente fornecidos pelo mantenedor podem aparecer na regressão solicitada; todas as quantidades/preços/descrições nessa fixture são simulados, não observações comerciais.

## Review Focus

- IDs não canônicos não podem perder zeros/espaços nem virar outra identidade numérica.
- Provedor ignorando filtro: página mista/identidade ausente rejeitada atomicamente, nunca seleção silenciosa.
- Metadados totais não filtrados/ausentes não podem promover completude da consulta.
- Erro/redirect do filtro não pode disparar replay, tentativa escalar/array ou consulta sem filtro.
- Concorrência, variantes/tabelas e conflitos devem preservar filtros locais e valores anteriores.

## Task 1 — Regressões e transporte/consumidores

**Files:** client.py, tools.py, tests/test_client.py, tests/test_sprint8.py.
**Interfaces:** _query/_collect(..., *, product_id:int|None, product_mask:str|None, reduced_id:int|None); get_product_price/check_inventory mantêm entradas textuais públicas e retornam lookup_strategy explícita.

- [x] Escrever regressão do cenário informado (código comercial, produto e reduzido) com handler que só devolve o alvo quando o body contém o filtro correto; sem filtro devolve prefixo de985 páginas.
- [x] Executar testes novos antes da produção e observar ausência do filtro/estado errado.
- [x] Cobrir bodies fechados; tipos/bounds/operações/combinações inválidos sem envio; identidades mistas/páginas posteriores; zero/null/ausência/vazio/limites/erros; precisão e variantes; concorrência/cancelamento.
- [x] Implementar validação privada e encaminhamento fixo dos filtros; adaptar strings canônicas sem alterar DTO ou legado textual.
- [x] Executar testes focados e suíte completa; atualizar apenas expectativa antiga que deliberadamente proibia prices/product_id e bodies MCP afetados.

## Task 2 — MCP, documentação e revisão final

**Files:** mcp_tools.py, tests/test_mcp_tools.py, tests/test_mcp_stdio.py, tests/mcp_stdio_fixture.py; PRD.md, AGENTS.md, README.md, docs/api-capabilities.md, docs/architecture.md, docs/security.md, docs/runbook.md.
**Interfaces:** consumidor canônico envia filtro; MCP continua strict/extra-forbid e JSON estruturado/texto equivalentes; nenhuma nova tool.

- [x] Estender regressões MCP/stdio para execução das duas funções com filtro, validação inválida sem envio, cleanup e estados preservados.
- [x] Atualizar descrições e documentos atuais; manter evidências históricas identificadas como históricas, sem reescrevê-las como nova prova operacional.
- [x] Executar `.venv/Scripts/python.exe -B -m unittest discover -s tests -v` e `.venv/Scripts/python.exe -B -m pip check`; Expected: OK / no broken requirements.
- [x] Revisão independente final somente leitura/testes offline; corrigir achados importantes com RED→GREEN e suíte completa.
- [x] Comparar snapshot público sem Git e tuplas de checklists; registrar comandos/resultados/decisões e pendências de validação real no runbook. Nenhum commit.

## Ledger

- Baseline público em managed scratch:26 arquivos explícitos, sem .env/Git. Python da .venv3.14.3. Suíte214 PASS/9.139s.
- Ruling: executar no workspace atual sem helpers Git/worktree/commits — proibição expressa do projeto; snapshot público substitui diff Git e não altera trabalho anterior.
- Ruling: compatibilidade textual não canônica mantém consulta local explicitamente identificada — não introduzir coerção destrutiva nem quebrar contratos existentes; custo: esses IDs continuam sujeitos aos caps, sem promessa de consulta direcionada.
- Ruling: implementar stock como singleton array seguindo os dois exemplos oficiais — schema number permanece divergente no OpenAPI; custo se errado: falha remota segura sem replay/fallback, ainda exigindo confirmação própria autorizada. Não afirmar contrato resolvido.
- Task1: complete. RED observado nos sete testes de consumidores/três testes privados;71 testes focados PASS/3.774s, suíte228 PASS/9.777s, pip check PASS após integração MCP/stdio.
- Task2: descrições, README/PRD/inventário/arquitetura/segurança/runbook atualizados. AGENTS.md NÃO alterado: aprovação protegida expirou; sem retry/bypass. A etapa documental fica aberta apenas para essa reconciliação humana.
- Auditoria:256 linhas de checklists PRD exatamente iguais; AGENTS.md/requirements.txt/catalog.py iguais ao snapshot público;18 arquivos Python aceitos pelo parser; nenhum novo excesso de79 caracteres no código alterado;87 links/âncoras locais válidos nos sete documentos verificados.
- Revisão independente:228 PASS/10.105s, pip check PASS; nenhum Critical, I1 Important de conflito stock preexistente e M1 Minor documental preexistente. I1 reproduzido em9 subcasos RED; chave stock corrigida para reduced_id, GREEN/0.032s e suíte229 PASS/10.116s. Sem nova revisão da alteração; prova da correção é a regressão executada.
- Final: minor (deferred): M1 — cabeçalho legado PRD:4 ainda cita sete tools, enquanto seção atual/registry/testes comprovam oito. Não muda execução.
- Final: Ruling: itens operacionais não julgados pelo revisor (aceitação do servidor, resolução definitiva number/array e comportamento real) continuam pendentes de autorização/evidência — custo se presumidos: afirmar estoque/preço sem prova. Não houve chamada para supri-los.
- Task2: implementação/regressão/auditoria/revisão concluídas offline, documentação restante bloqueada apenas para AGENTS.md. Validação real não solicitada nem executada.
- Verificação final do coordenador: suíte completa verbose229 PASS/10.279s,229 linhas OK, exit0; pip check PASS; auditoria final de snapshot/checklists/parser/novas linhas longas PASS. Checkout preservado sem Git/merge/publicação, conforme proibição expressa. Nenhum scratch do usuário ou trabalho anterior foi removido.
- Autorização posterior: mantenedor pediu reenviar alteração protegida de AGENTS.md e então executar os dois testes reais propostos. Edição aprovada/aplicada pelo mecanismo normal e conferida; timeout anterior resolvido sem bypass. Um loader privado em memória e no máximo duas tentativas page1/limit20, stock e prices, sem descoberta/páginas extras/replay, autorizados separadamente do plano inicial.
- Probe temporário: seis verificações sintéticas PASS e regressão229 PASS/10.074s antes da consulta. Cliente MCP em sessão em memória sobre factory/consumidores reais, sem alegar stdio operacional novo. Em21:39:53Z–21:39:54Z, duas tentativas HTTP200, uma linha correspondente por operação, found/nonpartial/complete apenas na consulta filtrada; fidelidade à própria resposta/Decimal/null/ausência/JSON e dois closes de resposta/um de transporte/um de cliente aceitos. Valores somente ao operador; evidência estrutural no runbook.
- Orçamento real novo CONSUMIDO/ENCERRADO: um loader e duas tentativas, sem rerun ou acesso contínuo. AGENTS.md e documentação atual reconciliados; Task2 documental concluída. Conflito publicado number/array persiste, embora o array tenha sido observado com sucesso nessa instalação. Sem alteração de sprints/globais/G6/V1.
- Verificação final pós-reconciliação:229 testes PASS/10.833s, pip check PASS; releitura do relatório estrutural confirma contagens/fidelidade/JSON/cleanup.256 linhas de checklists PRD e pins preservados. Nenhuma nova consulta realizada na verificação final.
