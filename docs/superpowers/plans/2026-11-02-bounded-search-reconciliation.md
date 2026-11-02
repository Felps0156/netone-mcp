# Busca limitada e reconciliação MCP

Autorização atual: execução offline delegada sem gates intermediários; sem Git,
ERP, .env, instalação ou cadastro Hermes. Preservar oito tools e limites atuais.

## Decisões do executor

- Unificar parcialidade com os invariantes de bloco seguro no coletor, em vez
  de corrigir cada consumidor isoladamente.
- Estender search_products com start_page/page_size/max_pages opcionais e
  mode literal (padrão compatível) ou related. Reusar a busca lexical existente,
  com termos required/suggested explícitos e uma só coleta. Não parar no primeiro
  match nem repetir por sinônimo; terminal/metadados/tetos limitam o trabalho.
- Implementar consumidor externo em memória sobre session.call_tool existente;
  não adicionar tool, join no normalizador, dependência ou persistência.
  Uma página por chamada, tamanho fixo, teto global de chamadas/páginas/linhas
  e tempo. Validar progresso e totais entre blocos, parar sem retry em erro.
  Reconciliação por reduced_id exato; preservar conflitos, zero e desconhecidos.

## Sequência TDD

1. Regressões de duplicatas terminais em products/stock: RED, correção mínima.
2. Busca tipada na aplicação/MCP, defaults/caps/validação/uma passagem: RED/GREEN.
3. Consumidor MCP reutilizável e reconciliação, com sessão sintética e casos
   adversariais de paginação/identidade/orçamentos: RED/GREEN.
4. Documentar contrato/uso no README e decisão atual no PRD, sem reescrever
   histórico/checklists. Rodar suíte offline completa e pip check; revisão final
   independente pelo coordenador. Sem afirmar snapshot ou cobertura ERP global.
