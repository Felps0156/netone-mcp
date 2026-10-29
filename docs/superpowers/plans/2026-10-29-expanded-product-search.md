# Pesquisa ampliada de produtos — plano de implementação

> Execução futura: usar superpowers:subagent-driven-development ou superpowers:executing-plans após autorização específica de escopo. Este plano não autoriza ERP, Sprint 8+ ou registro MCP.

**Objetivo:** permitir pesquisa textual com termos relacionados e percurso paginado limitado, sem apresentar uma amostra ou uma hipótese como resultado global garantido.

**Arquitetura:** o cliente MCP pode sugerir termos adicionais; o servidor permanece utilizável sem LLM e combina termos explícitos com uma lista revisada. Uma passagem limitada sobre o endpoint de produtos aplica os termos localmente, preserva restrições expressas e informa o universo percorrido, as evidências de cada correspondência e qualquer interrupção.

**Stack:** Python >=3.14,<4, unittest, HTTPX e SDK MCP já fixados em requirements.txt.

**Especificação:** PRD.md, DEC-028 e seções 10, 16, 18 e 23. A aprovação do conceito não altera as restrições operacionais existentes.

## Restrições globais

- Sem requisições reais ERP, login, rotação de token, leitura ou alteração de .env; validação somente sintética e offline.
- Nenhuma tool MCP registrada e nenhuma tarefa Sprint 8+ executada até autorização própria; não modificar checkboxes existentes.
- Manter allowlist, origem, TLS, corpo fechado, zero retries/redirects, teto de 1 MiB por resposta e cleanup limitado.
- Limites de páginas, linhas, tempo e memória permanecem explícitos e finitos; não alegar quota do fornecedor.
- Não inferir marca, modelo, estoque, compatibilidade, snapshot ou cobertura global. CatalogRecord não tem campo de marca estruturado validado.
- Não persistir respostas, dados comerciais reais ou sugestões automáticas; sinônimos entram no repositório apenas após revisão do mantenedor.
- Sem Git mutável, dependências novas ou integração LLM obrigatória.

## Decisões de desenho e portões

1. Alternativas: elevar somente max_results foi rejeitado porque ainda limita o universo e não amplia sinônimos. Fazer várias varreduras, uma por sinônimo, multiplica carga e pode produzir universos inconsistentes. Recomenda-se uma única passagem com todos os termos e limites compartilhados.
2. O modelo do cliente pode sugerir termos como entrada explícita; a aplicação não chama um serviço LLM nem confia que sugestões sejam sinônimos verdadeiros. A busca básica funciona sem sugestões. Termos, restrições e correspondências permanecem distinguíveis.
3. Marca/modelo são restrições textuais explícitas, não campos estruturados inventados. Se não puderem ser comprovados no texto disponível, não apresentar confirmação de marca/modelo; definir o comportamento exato antes da implementação.
4. Completude só se refere ao percurso visível do endpoint sob sua paginação. Mesmo uma passagem terminal coerente não garante snapshot, visibilidade de todo o ERP, nem cobertura de sinônimos ou identificação semântica.
5. Antes de implementar, aprovar contrato exato de entrada/saída, orçamentos finitos, tratamento de restrições textuais e política de sinônimos ambíguos; antes de tool MCP ou exploração real, obter autorização específica e definir orçamento remoto separado.

## Foco da revisão

- Um termo ambíguo como 'luva' pode retornar item de outra categoria: identificar como possibilidade, sem afirmar equivalência.
- Marca ou modelo ausente no texto não pode ser afirmado nem descartado silenciosamente como fato estruturado.
- Corte por páginas, linhas, prazo, falha ou metadados incoerentes não pode virar resultado completo ou ausência global.
- Duplicatas, conflitos e produto alterado durante paginação não provam snapshot consistente.
- Sugestões inválidas, excessivas ou maliciosas não podem alterar filtros remotos, limites ou instruções do servidor.

## Etapas propostas — dependem dos portões acima

### 1. Contrato e termos relacionados

Arquivos candidatos: `tools.py`, nova fonte versionada de sinônimos e `tests/test_tools.py`. Definir junto ao mantenedor o contrato tipado, limites de termos e normalização, separando consulta original, termos revisados, sugestões e restrições. Criar testes sintéticos para termos diretos, sinônimos ambíguos, sugestões inválidas e falta de marca/modelo; executar primeiro para observar falha e depois implementar o mínimo para passar. Não promover automaticamente sugestões à fonte revisada.

### 2. Percurso paginado e proveniência

Arquivos candidatos: `client.py`, `catalog.py`, `tools.py`, `tests/test_client.py` e `tests/test_tools.py`. Após aprovar orçamentos finitos e contrato, criar testes sintéticos para correspondência além de 20 linhas, passagem única com múltiplos termos, limite, timeout, erro, metadados ausentes/contraditórios e duplicatas/conflitos. Preservar o comportamento das consultas existentes; registrar termos de correspondência e razões de parcialidade. Executar testes de falha, implementar e repetir.

### 3. Integração e liberação separadas

O registry segue vazio enquanto o registro MCP não for autorizado. Após autorização própria e revisão de contrato/segurança, adicionar apenas a tool aprovada e testes stdio sintéticos para descoberta, schema e ausência de escrita. Nenhum teste sintético demonstra operação real; qualquer validação ERP exige autorização e orçamento próprio.

### 4. Verificação e documentação

Executar `.venv/Scripts/python.exe -B -m unittest discover -s tests -v` com transporte sintético e proibição de env/HTTP reais; registrar resultados reais e atualizar apenas documentação afetada. Revisar contrato, segurança, limites, dados parciais e ausência de informações privadas. Não marcar sprints concluídas sem evidência e autorização.
