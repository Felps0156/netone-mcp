# Sprint 9.5 — Otimização local incremental

Estado: abordagem1 e desenho aprovados pelo mantenedor, com autorização para seguir pelo plano. Fonte de verdade: PRD, seção28, S9.5.01–14 / DEC-032. Evidências de execução e checklist ficam no PRD/runbook, não são presumidas pela aprovação deste desenho.

## Intenção, escopo e alternativas

Encontrar produtos além das primeiras 20 linhas sem confundir inspeção com retorno, melhorar alternativas lexicais na aplicação e reduzir trabalho de serialização sem perda de informação.

1. Escolhida: manter `max_results` como orçamento de linhas recebidas, elevar explicitamente seu default de busca para 100 e acrescentar `max_items=20` como teto independente de retorno. Reutilizar o coletor existente. Custo: uma busca padrão pode inspecionar mais linhas; isso é aumento deliberado de cobertura, não economia HTTP.
2. Não escolhida: preservar default de inspeção 20 e exigir opt-in para ampliá-lo. Conserva custo padrão, mas não atende ao aceite da chamada padrão além de 20 linhas.
3. Descartada pelo PRD: reinterpretar max_results como matches, varredura integral, nova tool ou infraestrutura.

## Contrato de busca literal e compatibilidade

`search_products(client, query, max_results=100, *, max_items=20)`.

Ambos os limites são inteiros estritos 1–1000, sem bool/coerção. `max_results` mantém o significado anterior inclusive posicional: chamada explícita com 20 continua limitada a 20 linhas recebidas. A mudança do default omitido é intencional, documentada na aplicação e no schema MCP. `max_items` limita somente a saída; não altera o orçamento HTTP. Outros consumidores mantêm seus defaults e contratos.

O coletor continua aplicando `min(max_results, configuração)` e o teto configurado de páginas, sem alterar settings ou estado compartilhado. Página fixa `min(50, orçamento efetivo)`; prazo existente de quatro vezes timeout de fase, teto de bytes e cleanup preservados. Nenhum novo argumento controla configuração, HTTP ou prazo. O teto de saída não exige inspeção até preenchê-lo e não provoca parada no primeiro match: filtrar a coleta limitada inteira permite conservar variantes e erros posteriores.

Exemplos sintéticos:

- Chamada padrão com configuração de 100 linhas/5 páginas: até 100 linhas, páginas de 50 e até 20 matches retornados; produto só na segunda página pode aparecer.
- max_results=20: até 20 linhas, até 20 matches; sem ampliação silenciosa do orçamento explícito.
- max_results=100, max_items=1: mesma inspeção limitada, um item retornado; corte de saída explicitado.
- Configuração limitada a 10 linhas ou uma página: os limites configurados prevalecem; ausência sob corte é inconclusiva.
- Nenhum match: não ampliar orçamento, não repetir consulta, preservar parcialidade/erros.

Matching literal permanece substring casefold em description/product_mask/sku, com trim somente da consulta e sem remoção de acentos. Identificadores exatos e valores retornados não são normalizados.

## Busca ampliada somente na aplicação

`search_products_expanded(client, query, *, required_terms=(), suggested_terms=(), max_results=100, max_items=20)` reaproveita a mesma política de inspeção/retorno. O novo teto de saída é mudança explícita também aqui; o default anterior não tinha teto separado. Uma coleta atende todos os termos.

Proposta técnica do implementador, ainda sujeita à aprovação deste desenho:

- Separar automaticamente uma frase somente quando começa por um único tipo revisado inequívoco (manopla ou punho), seguido por restrições textuais. O restante vira restrição obrigatória da descrição, combinado com required_terms explícitos, nunca substituído por eles. Não identificar semanticamente marcas/modelos.
- Se houver mais de um tipo revisado na frase, ou não houver prefixo inequívoco, conservar a frase literal como termo direto e required_terms explícitos; não relaxar critérios para produzir alternativas.
- Manter somente o par revisado manopla/punho; nenhuma nova equivalência comercial. Sugestões explícitas permanecem suggested e não são persistidas.
- Comparação lexical ampliada: casefold e remoção de marcas diacríticas apenas em cópias de comparação; fronteiras Unicode de palavra para produtos e restrições, regex escapada e pontuação literal interna. Hífens externos podem delimitar; LS2 não casa LS20; metacaracteres não são regex do usuário.
- Normalizar descrição uma vez por item e preparar termos/padrões uma vez por busca. Deduplicar termos normalizados, preservando prioridade direct/reviewed/suggested e grafia de apresentação.
- Priorizar itens com match direto antes de alternativas, estavelmente na ordem de coleta dentro de cada classe. items e matches permanecem alinhados após corte. Contar candidatos com restrições sem evidência na descrição, mesmo quando há evidência apenas em outro campo; não afirmar compatibilidade.

## Metadados e completude

Reutilizar QueryResult e seus campos existentes. Acrescentar metadados mínimos para limites efetivos da coleta (linhas, páginas, tamanho de página e prazo), sem expor origem, credencial ou settings. A busca informa limites solicitados, quantidade de matches anteriores ao corte e se houve truncamento de saída. rows_received/pages_fetched/returned_count continuam sendo contagens executadas, não limites.

Distinguir a coleta completa da saída completa: expor collection_complete antes do corte; se a saída foi truncada, retornar partial=true/status=partial/complete_dataset=false e aviso fixo de corte de saída. Nunca apagar erro posterior, avisos de conflito/duplicata ou dados úteis. Sem corte, manter os estados atuais; not_found exige coleta completa válida e nenhum match. Duplicatas não conferem certeza nova; busca ampliada conserva sua política conservadora existente.

Serialização: substituir cópia recursiva de registros dentro de QueryResult.as_json por projeção rasa explícita dos metadados mais serialização única dos itens, se comparação comprovar equivalência. Avaliar a mesma otimização em CatalogRecord sem mudar sua ordem de apresentação. JSON textual MCP compacto com separators, preservando ensure_ascii/allow_nan e equivalência semântica com structuredContent. Medir bytes sintéticos antes/depois no mesmo payload, separadamente do tamanho adicional dos metadados.

## Investigação de filtros comerciais

Reexaminar anonimamente as páginas oficiais O5 e O4 referenciadas no inventário, sem acionar Send ou ERP. Registrar contrato efetivamente recuperado, divergências e limites da leitura; se só houver shell/navegação, não declarar contrato revisado.

O5: distinguir idsProdutos/idsReduzidos, tipos de arrays/elementos, combinações publicadas, page/limit e identidades/tabelas de resposta. Planejar apenas body fechado com filtro único de identidade, validação pré-envio e rejeição atômica de resposta incompatível. IDs textuais com zeros, espaços ou formato incompatível não são convertidos destrutivamente. Ausência de regra publicada deve permanecer lacuna, não contrato presumido.

O4: confrontar number versus array de idsReduzidos. Se não houver resolução inequívoca, conservar bloqueio e seleção local limitada. Não copiar formato de produtos/preços nem escolher pelo legado. Evidência necessária: contrato oficial coerente/clarificação do fornecedor, revisão de admissão e autorização própria de implementação/validação.

Consolidar casos futuros para identidade inválida sem envio, identidade divergente, vazio/erro, paginação filtrada, concorrência e múltiplos reduzidos/tabelas. Comparação de custo dirigido versus prefixo é estimativa estrutural, não ganho remoto medido. Sem fallback automático depois de erro. Nenhum filtro comercial novo será implementado nesta sprint.

## Arquivos e fronteiras

Alterações previstas: tools.py, catalog.py, mcp_tools.py; client.py apenas para metadados mínimos de orçamento no QueryResult, sem reconstruir coleta/transporte. Estender testes existentes de tools/client/expanded/catalog/product_fields/MCP/stdio/sprint8 conforme responsabilidade. Manter config.py, server.py, dependências e modelos de campos comerciais sem mudanças.

README, inventário, runbook e PRD serão reconciliados com os contratos e evidências reais; desenho/plano são um par por sprint, não dossiês por tarefa. Preservar textos/ordem/estados de tarefas alheias e marcar S9.5 somente após sua verificação. Instruções protegidas só serão reconciliadas pelo mecanismo normal, sem bypass de recusa/timeout.

Exatamente sete tools atuais; search_products continua literal. DEC-030 não será ampliada para expor busca lexical ampliada ou SKU técnico. Sem novos módulos, camadas, cache, banco, LLM, dependências, paralelismo HTTP ou infraestrutura.

## Verificação e limites de aceite

TDD nos comportamentos alterados. Baseline público allowlisted em scratch gerenciado, excluindo .env/.git/.venv e arquivos privados antes de qualquer travessia; nenhum comando Git. Regressão principal: `.venv/Scripts/python.exe -B -m unittest discover -s tests -v`; pip check e inspeções offline relevantes sem instalar nada.

Fixtures precisam demonstrar segunda página além de 20 linhas na chamada literal padrão e via MCP/stdio; limites explícitos/restritivos, zero matches, cortes de saída, erros anteriores/posteriores, metadados ausentes/contraditórios, página vazia/repetida, duplicatas/conflitos, sugestões inválidas, isolamento concorrente e cancelamento com cleanup concluído. Valores/Decimal/null/zero/false/missing_fields, origem/tabelas/escopo e JSON estruturado/texto são preservados. Sinônimos não multiplicam requests; medidas contam requests/páginas/linhas/matches/bytes no mesmo universo, sem depender apenas de tempo de parede.

Revisão independente do conjunto e auditoria de checklist antes do fechamento. Nenhuma tarefa será marcada agora. G3 permanece no recorte DEC-031, V1 NOT_READY, DEC-027 e orçamentos encerrados preservados. Nenhum .env real, ERP, login, rotação, mutação, Git ou Sprint 10. Resultado é evidência offline, não nova prova operacional.
