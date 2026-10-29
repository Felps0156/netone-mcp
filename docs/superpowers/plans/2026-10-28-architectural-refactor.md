# Refatoração arquitetural incremental

> Execução autorizada pelo mantenedor em 28/10/2026 após aprovação da auditoria e da abordagem incremental. Usar superpowers:executing-plans com testes de caracterização e revisão independente final. Não solicitar nova aprovação para decisões dentro deste escopo.

## Objetivo e desenho aprovado

Simplificar a fundação implementada das Sprints 0–5, sem iniciar a Sprint 6. Manter os módulos atuais e os contratos privados de coleta/normalização. Alternativas avaliadas: limpeza apenas documental (menor risco, deixa o acoplamento HTTPX) e refatoração incremental com testes (escolhida). Não recomeçar o projeto.

Stack: Python >=3.14,<4, SDK MCP, HTTPX, Pydantic, AnyIO e python-dotenv nos pins existentes; unittest da biblioteca padrão. Remover LangChain/LangGraph sem uso; reavaliá-los somente se houver consumidor real futuro.

## Restrições globais

- Não acessar/modificar .env, segredos, dados comerciais ou ERP; somente configuração e respostas sintéticas nos testes.
- Sem login, chamadas reais, ferramentas MCP novas, novos filtros, análise, Docker, DB ou CI/CD.
- Preservar HTTPS verificado, origem fixa, allowlist literal dos três POSTs, zero retries/redirects, limites e erros sanitizados.
- Manter Decimal, IDs/códigos, null/ausência/zero, metadados, duplicatas e parcialidade.
- Não executar commits, pushes, resets, troca de branch nem editar .git. Trabalhar no checkout autorizado sem worktree adicional.
- Código/docs públicos em inglês; PRD/planejamento em pt-BR. Aspas simples e PEP 8.
- Nenhum estado de sprint muda nesta refatoração. Seção 28 e registros históricos permanecem rastreáveis.

## Tarefas e verificação

- [x] 1. Atualizar políticas antes do código: permitir unittest/mocks e inspeção Git, adiar dependências sem consumidor, simplificar obrigação documental. Arquivos: PRD.md, AGENTS.md. Preservar versão anterior integral em docs/history/ e checklist canônico.
- [x] 2. Criar testes de caracterização offline antes das alterações de comportamento. Arquivos: tests/test_client.py, tests/test_catalog.py, tests/test_server.py; configuração em tests/test_config.py. Interfaces existentes: Settings, _validate/load_config, NetOneClient._query/_collect/aclose, CatalogRecord/QueryResult.as_json, create_server/main. Executar `.venv/Scripts/python.exe -B -m unittest discover -s tests -v`; baseline dos contratos corretos deve passar. Novos comportamentos devem falhar antes de implementar.
- [x] 3. Simplificar config.py: parsing de URL por biblioteca, validações essenciais explícitas e erro sem valores; remover restrições lexicais de redes/hosts definidos pelo operador. Preservar carregamento sem interpolação/mutação e compatibilidade de origem legada. NETONE_MAX_RETRIES legado será aceito como ajuste inerte, não habilitará reenvios. Testes: HTTPS, origem, userinfo/path/query, tokens, limites, overrides, falhas de I/O e importação sem .env.
- [x] 4. Simplificar client.py: APIs públicas de streaming, centralizar erro e cleanup protegido, evitar estado HTTPX escrito manualmente e dupla validação do body. Manter guarda de método/origem/rota; filtros internos fechados. Não remover limite identity/bytes sem alternativa igualmente limitada. Testar status, JSON/Decimal, oversize, guarda, paginação, falhas iniciais/tardias, deadline e cancelamento/cleanup.
- [x] 5. Simplificar logging em server.py e client.py: eventos identificáveis seguros; payloads SDK/HTTP continuam não renderizados. Não desativar indiscriminadamente loggers. Testar entrada MCP inválida, root DEBUG, exceções e stdout protocolar. Remover somente os pins LangChain/LangGraph; preservar demais versões. Sem desinstalação em massa do ambiente.
- [x] 6. Consolidar README/configuração/inventário/runbook. Mover evidências históricas em vez de apagá-las; seção 28 mantém IDs/estados/ordem, contratos e pendências reais. Não repetir gates em todas as páginas.
- [x] 7. Revisão independente somente leitura; corrigir defeitos relevantes com regressão RED→GREEN. Executar suíte completa, imports/sintaxe, pip check, stdio real sem LLM/rede/env e auditoria programática de checklist/links/arquivos. Registrar comando e resultado real em runbook, sem relatório por microalteração.

## Foco da revisão

Cancelamento durante o auto-close HTTPX; limite de resposta sob encoding; logs de protocolo inválido e dados privados; origem equivalente IPv6/porta padrão; página terminal repetida/contraditória e precisão Decimal.

## Registro de decisões e execução

Baseline público salvo em scratch gerenciado, sem .env. Baseline executado: Python 3.14.3, pins instalados e pip check válidos; sintaxe dos cinco módulos válida; initialize/tools-list por subprocesso com loader sintético e transporte bloqueado: duas respostas, zero tools, saída 0.

Decisão: o pedido explícito de execução autônoma substitui checkpoints adicionais de aprovação de plano. Não criar infraestrutura de worktree/commits/ledger baseada em Git; este plano contém o registro mínimo de execução.

Execução: PRD 1.2.0 consolidado antes de fechar a implementação; instruções propostas em docs/agent-instructions-proposed.md. A edição protegida de AGENTS.md expirou sem aprovação da ferramenta; não houve retry nem bypass. Após o retorno do mantenedor e renovação explícita da autorização, a ferramenta normal aplicou as instruções aprovadas em AGENTS.md; a tarefa 1 está concluída e o timeout anterior é histórico.

Testes: 23 contratos cliente/catálogo passaram na base original. Três novos critérios (sem escrita de estado HTTPX, sem desligar loggers no construtor e fechamento do cliente limitado) falharam antes e passaram depois da alteração. Logging estruturado seguro também falhou antes e passou depois; configuração teve 11 caracterizações e novos comportamentos RED→GREEN. Última suíte integrada: 49 PASS, incluindo stdio com DEBUG, import de LangChain/LangGraph bloqueado e HTTP/env proibidos. Sintaxe/compilação de nove arquivos, linhas <=79, cinco pins instalados e pip check passaram. Não é instalação limpa nem validação remota.

Decisão: manter iteração explícita do protocolo público response.stream, sem escrever estados HTTPX, em vez de aiter_raw com fechamento automático. O código HTTPX instalado comprova que o auto-close pode começar antes do shield; testes observam cleanup concluído sob cancelamento. Isso preserva o limite raw sem nova classe/adaptador. Custo: uma pequena rotina de leitura/cleanup explícita permanece.

Decisão: a guarda final continua validando método/origem/Host/rota, enquanto _query valida filtros e constrói o body fechado. O objeto HTTP privado não é sandbox contra código Python confiável que deliberadamente acessa seus privados. Custo: futuros consumidores devem usar _query, nunca repassar body arbitrário.

Auditoria própria anterior à aplicação final de AGENTS.md: os 212 IDs/estados/ordem de sprint, catalog.py, tools.py e AGENTS.md eram idênticos ao baseline; PRD/runbook históricos integrais conferem; nenhum link local dos documentos atuais está quebrado. Nenhum comando Git, ERP, instalação, segunda .venv ou acesso ao .env. A revisão independente foi concluída: um achado Important, nenhum Critical/Minor. O timeout no fechamento do cliente podia substituir o erro/cancelamento original em __aexit__. Dois testes reproduziram a falha antes da correção; após preservar a exceção de entrada, a suíte completa passou com 51 testes. Falha isolada de cleanup continua erro; não há falsa garantia de recurso liberado. Verificação pelo coordenador, sem segunda revisão. Nenhum achado menor adiado. O runbook contém resultados e limites finais; a tarefa 1 foi posteriormente concluída com a aplicação protegida de AGENTS.md após renovação da autorização.
