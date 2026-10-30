# Sprint 9 — Registro MCP delimitado

Estado: desenho offline executado e revisado. As restrições de prova real
abaixo registram o checkpoint original; autorização posterior única e
resultado em DEC-031/PRD1.9.1: S9.12 concluída por listagem MCP real
page1/limit1 HTTP200, G3 PASS nesse recorte. Orçamento consumido/encerrado,
sem repetição, nova consulta ou Sprint10. V1 NOT_READY.

## Aprovação e intenção

O mantenedor aprovou a abordagem incremental apresentada na conversa e sua
execução offline no workspace atual, incluindo revisão das restrições
contraditórias do PRD/AGENTS. Este documento registra essa aprovação; não
renova orçamento ERP. A Sprint 10 e V1 continuam fora deste aceite.

Entregar descoberta e execução por cliente MCP genérico, preservando o
cliente guardado e os contratos comerciais já implementados.

## Abordagens

1. Adaptadores explícitos sobre o servidor stdio atual (recomendada e
   aprovada): menor mudança, um cliente por lifespan e nenhuma nova rota.
2. Reescrever o servidor/transporte: sem benefício proporcional; descartada.
3. Registrar todas as funções existentes: descartada por promover SKU técnico
   e busca ampliada sem evidência operacional própria.

## Contrato e fronteiras

Registrar somente search_products, search_product_by_code,
get_product_details, search_product_by_ean, get_product_price,
check_inventory e list_products. Cada uma usa a função de aplicação atual;
o cliente vem do lifespan, nunca dos argumentos MCP. SKU técnico e busca
ampliada continuam disponíveis apenas na aplicação, fora do registry.

Schemas fechados, tipos estritos e limites iguais aos das funções:
query 1–200; códigos/identidades textuais 1–256; product_id inteiro
0–9223372036854775807; max_results 1–1000/default20; page_size opcional
1–1000; max_pages 1–100/default1. A aplicação continua rejeitando branco e
categorias Unicode C, sem alterar códigos. Page size também deve caber no
orçamento efetivo. Nenhum URL/token/tenant/método/body arbitrário ou moeda
fornecida pelo modelo. Preço MCP mantém moeda desconhecida; confirmação BRL
não é universalizada para outras instalações.

A implementação pode especializar os métodos públicos list_tools/call_tool
sob FastMCP para validar os argumentos brutos sem coerção/pré-parse implícito
e retornar mensagens fixas. Inspeção de mcp==1.30.0 mostrou que o caminho
padrão inclui detalhes de validação/exceção no erro de tool; não delegar a
ele a fronteira de sigilo. Não editar SDK nem remover suas guardas.

Sucesso comercial, vazio e parcial preservam o payload JSON e metadata;
status error usa CallToolResult.isError=true e mantém structuredContent.
Erro de entrada/tool desconhecida/falha inesperada: isError=true com código
e texto fixos, sem argumentos, nome desconhecido ou exceção original.
Cancelamento externo propaga. Dados da API são dados, nunca instruções.
Anotações readOnlyHint=true, destructiveHint=false, idempotentHint=false
(nenhuma garantia/replay), openWorldHint=true.

## Verificação e limites de aceite

TDD com transporte sintético no caminho real aplicação/coletor/guard.
Cliente MCP SDK genérico via stdio deve inicializar, descobrir exatamente
as sete tools, executar consulta sintética, rejeitar entradas extras e
malformadas sem envio e encerrar com cleanup concluído. Exercitar erros,
parcialidade, Decimal/zeros/null e logs seguros. Startup nunca consulta ERP.
Sem LLM, novas dependências, instalação, banco ou infraestrutura.

S9.12 exige evidência operacional pelo cliente autorizado; a execução
sintética será registrada como integração offline, não consulta ERP. Sem
nova autorização real, manter S9.12 aberta e G3 operacional pendente;
não revisar silenciosamente seu critério nem declarar Sprint 9 concluída.

Sem .env real, ERP, login, rotação, Git, alteração de outra sprint ou
critérios globais. Manter baseline público/diffs/ledger em scratch gerenciado
porque helpers de worktree/commit violariam a proibição Git. Atualizar apenas
documentação afetada e marcar tarefas somente com evidência própria.
