# Sprints 12 e 14 — Documentação pública e encerramento delimitado

Data: 2026-10-31. Estado: aprovado pelo mantenedor, incluindo execução até
verificação final sem aprovações intermediárias; builder check sem lacunas
importantes. Plano: ../plans/2026-10-31-sprints-12-14.md.

## Intenção e autorização

Executar exclusivamente as tarefas abertas das Sprints 12 e 14 da seção 28
do PRD. O mantenedor confirmou expressamente que a Sprint 13 não faz parte
do pedido. Não repetir tarefas já marcadas nem modificar seus critérios.
O objetivo é permitir que um mantenedor entenda instalação, contratos,
segurança, limites e estado real da entrega sem informações privadas.

## Abordagens

1. **Consolidar os contratos implementados e encerrar com limites explícitos**
   (proposta recomendada): reaproveitar README, inventário, configuração e
   runbook; acrescentar os guias ausentes; auditar os contratos contra código
   e testes. Preservar NOT_READY e a Sprint 13 aberta. Não exige alterar
   comportamento ou gastar orçamento ERP.
2. **Preparar uma V1 operacional/publicada:** não se enquadra no pedido, pois
   exigiria critérios da Sprint 13, autorizações operacionais e autorização
   de publicação. Descartada neste escopo.

A delimitação de executar apenas 12 e 14 foi confirmada pelo mantenedor.
A implementação segue a primeira abordagem aprovada neste desenho;
não se atribui ao mantenedor aceite operacional ou escolha de licença.

## Estado observado e responsabilidades

- config.py é o único loader explícito; settings e credenciais pertencem ao
  processo. A configuração real não será lida.
- server.py mantém stdio e um cliente privado por lifespan. mcp_tools.py
  define exatamente sete entradas estritas, sem configuração ou HTTP livre.
- tools.py implementa os consumidores; client.py admite exclusivamente os
  três POSTs existentes, page/limit e, somente em produtos, um filtro
  mutuamente exclusivo de ID inteiro ou mascara textual.
- catalog.py preserva identidades, Decimal, nulidade e proveniência.
  analysis.py serve duas funções somente de aplicação. SKU técnico e busca
  ampliada também permanecem fora do registro MCP.
- Há evidência operacional histórica delimitada, mas não nova evidência.
  G3/G4 não serão ampliados nem instalação limpa/plataformas certificadas.
- Não foi encontrado arquivo de licença/notice na inspeção direta de arquivos
  da raiz e de tests. A referência SCSI declara ausência de cópia de código.
  Revisar metadados das dependências instaladas e registrar atribuições sem
  inventar direitos de redistribuição ou escolher licença pelo responsável.

## Entregáveis

- README em inglês com estado atual, setup, navegação, sete tools, limites,
  comandos de desenvolvimento e integração MCP genérica por caminhos absolutos.
- docs/architecture.md: camadas, diagrama Mermaid, fluxo/lifecycle e fronteiras.
- docs/security.md: allowlist literal, configuração, segredos, dados não
  confiáveis, TLS, limites, cancelamento e garantias que não são oferecidas.
- docs/local-dev.md: receitas Windows/macOS/Linux, um ambiente raiz,
  interpreter explícito, pins, verificações offline e plataformas não testadas.
- docs/api-capabilities.md: matriz atual de método/rota/schema/consumidor/
  evidência, distinguindo contrato implementado de filtros publicados futuros.
  Preservar observações históricas e rotular seus estados obsoletos.
- docs/runbook.md: instruções atuais, troubleshooting, procedimento de futura
  validação manual com autorização própria, evidências novas offline e ledger
  agrupado das tarefas 12/14. Não criar nova matriz de aceite da Sprint 13.
- PRD.md: versão 1.12.0, DEC-035, data e resumo das duas sprints, escopo e
  pendências atuais. Preservar todos os textos/IDs/ordem das tarefas e estados
  alheios, inclusive critérios globais e Sprint 13. Marcar somente tarefas com
  evidência. A classificação de entrega será NOT_READY, sem publicação.
- AGENTS.md: atualização restrita do estado atual/autorização e navegação,
  pelo mecanismo normal protegido. Recusa/timeout implica parar essa edição
  e reportar a divergência, sem caminho alternativo.

## Limites e não objetivos

Sem leitura/escrita/movimento do .env real, ERP, login, renovação, Git,
instalações, substituição de ambiente, dependências novas, filtros/tools,
infraestrutura, alterações de produção ou testes sem necessidade demonstrada.
Não declarar ausência de segredos em Git/histórico ou em arquivos privados que
não forem examinados. A auditoria cobre somente o conjunto público explícito;
.gitignore não prova ausência de segredos já rastreados. Arquivos históricos
não serão reescritos, exceto a emenda de privacidade abaixo. Publicação será
um handoff opcional, não ação.

### Emenda de privacidade explicitamente aprovada

A auditoria encontrou12 linhas com identificadores pessoais/empresariais ou
caminhos locais em cinco documentos preexistentes. O mantenedor autorizou
expressamente sanitização pontual em docs/history/PRD-1.1.6.md,
docs/history/runbook-through-1.1.6.md e nos planos históricos de Sprint5/9/11.
Substituir somente essas referências por placeholders neutros, preservando
decisões, resultados, textos/IDs/ordem/estados de checklist. Atualizar o índice
histórico para não alegar mais cópia byte-idêntica. Esta exceção supersede
somente a imutabilidade dessas referências identificáveis; não autoriza
reescrever evidências, ler .env, executar Git ou publicar.

## Verificação e critério de conclusão

1. Capturar baseline público allowlisted em scratch gerenciado, excluindo
   .git, .venv, caches e configuração privada antes da travessia.
2. Conferir inputs/defaults, consumidores e admissão literal contra os sete
   módulos e testes existentes; revisar imports/pins e metadados de licença.
3. Executar a suíte unittest offline existente e pip check usando a .venv
   raiz, com fixtures sintéticas e nenhuma carga de configuração real.
   Os testes SDK/stdio existentes exercitam integração genérica e cleanup.
4. Auditar exemplos públicos, links locais e anchors novos; comparar tuples
   de checklist e arquivos contra baseline por código, sem Git. Confirmar
   código/testes/manifesto inalterados e históricos preservados exceto as
   substituições de privacidade explicitamente aprovadas.
5. Obter revisão independente do conjunto e corrigir divergências no escopo.
6. Registrar resultados reais e limites no runbook antes de marcar as tarefas.
   S14.14 aceita apenas a evidência realmente disponível: não transforma os
   resultados sintéticos ou histórico em nova prova do ERP.

G5 pode ser aceito no recorte documental público verificado, com limites de
licenciamento/publicação e cobertura explicitados. G6 e V1 não serão
promovidos; a Sprint 13 e os critérios globais permanecem pendentes.

## Decisões deixadas ao implementador

Organização dos tópicos, tabelas e navegação; comandos equivalentes por
plataforma como receitas não executadas; seleção de exemplos sintéticos;
metadados estruturais de auditoria e nomenclatura dos artefatos temporários.
Licença do projeto, novo orçamento operacional e publicação são decisões do
mantenedor e não serão preenchidas por suposição.
