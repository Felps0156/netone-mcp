# Product Field Priority Implementation Plan

> For agentic workers: use superpowers:executing-plans for inline execution. User opted out of further interactive design/implementation confirmations while away.

Goal: priorizar dados de produto úteis e comprovadamente preenchidos sem apagar null/vazio/ausente/zero/false, inferir estoque ou substituir SKU técnico.

Architecture: manter DTO imutável e normalização explícita em catalog.py; enriquecer a projeção consumida pelas funções existentes e ordenar apresentação JSON, sem alteração de consulta/transporte/registro MCP. A tabela agregada de campos tem amostra limitada, não contrato universal do fornecedor.

Tech stack: Python >=3.14,<4; unittest/MockTransport; dependências atuais.
Spec: desenho abaixo e PRD DEC-026. Mantenedor pediu alterar código/PRD conforme necessário; não autorizou concluir aceite real com mocks.

## Desenho e escopo

Duas consultas products page1/2, limit50, HTTP200, inspecionaram100 linhas. Registrar apenas contagens/tipos de39 campos conhecidos:36 presentes e6 nomes extras descartados por privacidade. Inspeção dos seis extras aguarda autorização pontual; a pergunta adicional não foi respondida. Nenhuma nova consulta agora.

P0: mascara/descricao. P1: bloqueado, grupo/subgrupo/linha, EAN e identificação estável. P2: preço/tabela varejo e atacado já presentes em products; não cotação, não consulta ao endpoint prices, não estoque. P3: observação quando preenchida e timestamp bruto. Código SKU técnico vazio e campos logísticos zerados não guiam busca/identidade. Cor/tamanho textuais estão presentes, mas presença não comprova significado útil; inventariar sem criar novos filtros ou aliases automáticos.

Adicionar subgroup<-subgrupoDescricao e notes<-observacao como texto exato; wholesale_price_table<-tabelaPrecoAtacado como texto exato; wholesale_price<-valorAtacado como Decimal exato; blocked<-bloqueado como bool estrito ou None. Não expandir todo JSON bruto. Novos campos opcionais, sem coerção, fonte ausente reportada em missing_fields. blocked=false é dado preenchido e não prova estoque/liberação comercial. Null/vazio permanecem no retorno.

CatalogRecord.as_json mantém todas as chaves antigas e valores, adiciona cinco campos opcionais e ordena campos preenchidos antes dos null/blank; código/descrição primeiro entre os preenchidos, missing_fields por último. Zero/false não são vazios. Só ordem de apresentação JSON, sem roteador conversacional ou dependência da ordem por consumidores.

## Global constraints

Sem Git/.git/instalação/.env leitura fora do probe autorizado/novas requests/login/token/SDK/servidor/rotas/preço-estoque joins/Sprints8+. Snapshot público em scratch substitui Git; manter artefatos para recuperação. Não alterar tarefa/checkbox de sprint. S7.11 continua aberta sem codigoSku real.

## Review focus

- false/zero não viram ausentes ou indisponibilidade.
- Decimal/zeros à esquerda/espaços permanecem exatos.
- Campos adicionais inválidos falham de modo sanitizado; fechamento e parcialidade preservados.
- Ordem é apresentação, não promessa de estoque, preço final ou cobertura global.
- Seis extras desconhecidos e amostra enviesada são limites explícitos, não evidência inventada.

## Task 1 — projeção e prioridade consumidas pelas funções atuais

Files: catalog.py, tests/test_product_fields.py, docs/product-field-priority.md, PRD.md, README.md, AGENTS.md, docs/api-capabilities.md, docs/runbook.md. Consumes normalize_record/QueryResult; produces mesmos tipos com cinco campos opcionais e as_json ordenado. Nenhuma interface HTTP muda.

- [x] Escrever testes de mapeamento/ordem, null-vazio-ausente, bool estrito, Decimal, imutabilidade, campos não projetados e integração MockTransport da função comercial.
- [x] Executar foco e verificar RED por projeção/ordem ausente.
- [x] Implementar somente os novos campos tipados e ordenação de apresentação.
- [x] Executar foco GREEN e suíte completa `.venv/Scripts/python.exe -B -m unittest discover -s tests -v`; pip check e auditoria pública, sem .env/rede.
- [x] Publicar inventário agregado integral dos39 campos conhecidos e limites dos seis extras; atualizar PRD1.6.0/DEC026 e política. Resolver inconsistência documental M1 da revisão anterior no resumo de filtros. AGENTS.md não alterado após timeout de aprovação da proteção; sem retry ou caminho alternativo.
- [x] Revisão final independente única: aprovada sem achados Critical/Important/Minor; limites preservados para seis extras, S7.11, prontidão V1 e aprovação protegida. Sem commits/push.
