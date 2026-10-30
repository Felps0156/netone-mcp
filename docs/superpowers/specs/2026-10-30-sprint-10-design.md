# Sprint 10 — Análises determinísticas na aplicação

Estado: desenho aprovado pelo mantenedor em 30/10/2026, com limiar padrão de estoque baixo ajustado para 3. Opção 1 escolhida. A aprovação não é implementação nem aceite da sprint.

## Intenção e escopo

Entregar `tools.analyze_inventory` e `tools.analyze_product_catalog`, sem LLM, novas tools MCP ou alterações comerciais. Reutilizar consultas já admitidas e normalização existente para produzir contagens verificáveis do universo efetivamente coletado. Implementar somente S10.01–15; marcar tarefas apenas após evidência.

O pedido atual autoriza iniciar a Sprint 10 e a escolha confirma a camada de aplicação. Não renova orçamentos de ERP. A validação será offline, com dados sintéticos explicitamente identificados nos testes e na demonstração; nenhum acesso ao `.env` real, login, rotação ou Git. Sprints posteriores, G3 e V1 não são promovidos.

## Abordagens

1. Escolhida pelo mantenedor: funções na aplicação, módulo `analysis.py` para preparação de universo/agregação, sem adaptadores MCP. Menor expansão de superfície e nenhuma dependência nova.
2. Não escolhida: incluir adaptadores MCP. Exigiria revisar o registro de sete tools e definir aceite próprio; fora deste desenho.

Grafo/framework não se justifica: coleta → normalização já existente → preparação de identidades → agregação → serialização são etapas diretas. Não criar adaptadores opcionais sem consumidor.

## Arquitetura e interfaces propostas

- `tools.py`: duas funções assíncronas públicas, validação antes da coleta, chamada única de `_collect()` por análise e composição do retorno.
- `analysis.py`: estado imutável tipado para o universo preparado e funções puras de métricas. Justificado pelas etapas reais compartilhadas e por dois consumidores; não duplica normalização, transporte ou paginação.
- `catalog.py`, `client.py`, `config.py`, `server.py` e `mcp_tools.py`: preservar comportamentos e registry; nenhuma necessidade identificada de editá-los.
- `tests/test_analysis.py`: regressões puras e integração com o cliente/streams sintéticos seguindo os fixtures existentes.

Assinaturas aprovadas (threshold aceita também inteiro estrito conforme abaixo):

- `analyze_inventory(client, *, threshold: Decimal = Decimal('3'), max_results: int = 100, max_pages: int = 1) -> dict[str, object]`
- `analyze_product_catalog(client, *, max_results: int = 100, max_pages: int = 1) -> dict[str, object]`

`threshold` aceita somente Decimal finito não negativo ou inteiro estrito não negativo, sem bool/float/string/coerção; o valor é configuração por chamada, não nova variável de ambiente. Não altera ERP ou configuração do processo. Limite de representação defensivo: até 100 algarismos no coeficiente e expoente entre -100 e 100. Limiar padrão 3 aprovado pelo mantenedor é regra local da análise, não regra comprovada do ERP. Regra: low_stock quando quantidade conhecida <= threshold; zero e negativo são subcontagens explícitas, e não disponibilidade para venda.

`max_results` inteiro estrito 1–1000 conta todas as linhas recebidas, inclusive duplicatas, e continua limitado pela configuração. `max_pages` inteiro estrito 1–100/default1 é limitado pela configuração. Page size fica com o coletor: min(50, orçamento efetivo), fixo. Sem filtro, seleção de depósito, join, segunda coleta, retry ou parada no primeiro resultado. Uma página por padrão evita varredura ampla implícita.

## Universo e identidade

Preservar exatamente IDs, códigos, Decimal, ausência/null/zero e registros fonte. Preparar grupos por reduced_id textual exato: um reduzido é a unidade de contagem, nunca uma linha ou um produto inferido. Não mesclar IDs com zeros, caixa ou espaços diferentes.

O coletor já remove duplicatas brutas idênticas. Na preparação, registros projetados inteiramente iguais para o mesmo reduced_id contam uma vez. Qualquer diferença entre registros normalizados de uma mesma identidade torna esse grupo ambíguo: excluir o grupo inteiro dos indicadores, contar uma identidade conflitante e conservar os registros no retorno de origem. Não escolher primeiro/último registro nem somar variantes conflitantes. Isso também protege reduced_id associado a product_id diferente. Não somar quantidades entre reduzidos, unidades ou depósitos.

`records_analyzed` = número de identidades não conflitantes usadas nas métricas; `source_record_count` = registros normalizados recebidos do coletor; `rows_received` continua contagem de linhas brutas. Informar `distinct_reduced_ids`, `conflicting_identity_count` e `duplicate_records_excluded` (somente duplicatas projetadas observáveis após coleta; não inferir quantas linhas o coletor descartou).

## Métricas

Estoque, exclusivamente de `stock`:

- quantidade conhecida, desconhecida, explicitamente null e ausente (missing_fields contém quantidade);
- low_stock_count para valores conhecidos <= threshold;
- zero_quantity_count e negative_quantity_count;
- above_threshold_count para valores conhecidos > threshold.

Categorias zero/negativo são subconjuntos de low_stock, não parcelas adicionais. Sem soma monetária, valor de estoque, média de quantidades, reposição recomendada, venda garantida ou interpretação de unidade. Escopo usa o mesmo contrato de check_inventory: depósito configurado do usuário, identidade de depósito/filial e frescor desconhecidos.

Catálogo, exclusivamente de `products`:

- número de product_id distintos entre identidades analisadas, sem apresentar isso como todos os produtos do ERP;
- contagens de campo preenchido, ausente, null e texto branco para commercial code/product_mask, description, technical sku e ean;
- blocked true, false e desconhecido, distinguindo ausente de null;
- contagens por group, subgroup e line textuais exatas; null/ausente/branco em categorias separadas, sem rótulo sentinela que possa colidir com texto real.

Sem validação de barcode, preço final, compatibilidade, sellability ou confirmação de unicidade comercial do SKU/EAN. Não usar quantidade projetada em products como estoque.

## Retorno e conclusões

Reutilizar `QueryResult.as_json()` como envelope e fonte dos registros, proveniência, erros, limites e metadados. Adicionar `analysis_type`, `records_analyzed`, contagens do universo, `threshold` como string/null, `criteria` com regras explícitas, `metrics` e `analysis_scope`.

Preservar `items`, `missing_fields`, todos os valores e avisos; `returned_count` continua significando registros devolvidos, não identidades analisadas. Sem corte adicional de saída. `retrieved_at` não significa frescor do estoque.

Separar `collection_complete` (completude original do coletor) de `complete_dataset` analítico: este último só é true se coleta completa, sem erro, sem duplicatas observadas ou identidades conflitantes. Duplicatas removidas pelo coletor e conflitos impedem conclusão global mesmo que a paginação termine. Se análise invalida completude, promover status para partial e acrescentar aviso fixo, preservando erro inicial/posterior. Erro sem dados permanece error; vazio válido completo permanece not_found. Grupo totalmente conflitante não vira not_found.

`analysis_scope` = `sample` quando incompleto; `visible_endpoint` somente quando completo. Mesmo nesse último caso, declarar que não prova snapshot ou cobertura global do ERP. Métricas sempre têm denominador explícito; dados ausentes restringem a métrica correspondente, não são convertidos em zero. Acrescentar `metrics_complete` separado para estoque (todas as identidades têm quantidade conhecida) e catálogo (todos os estados de presença podem ser classificados); completude de percurso não prova campos preenchidos. Ausência de quantidades permite contagens de desconhecidos, mas não classificar esses itens no limiar.

Não marcar dados de produção como sintéticos no contrato da função; a procedência sintética pertence ao harness/demonstração, enquanto source continua o envelope existente `netone_api` para o cliente mockado.

## Segurança e padrões preservados

Python >=3.14,<4, uma `.venv`, requirements.txt inalterado; código/docs públicos em inglês, planejamento/PRD pt-BR, aspas simples e unittest. Somente o cliente guardado, origem/TLS/allowlist/schema existentes, sem novas rotas/filtros/HTTP paralelo. Cancelamento propaga e cleanup concluído deve ser observado. Imports sem configuração/rede, stdout MCP-only, sem logs de dados ou exceções cruas.

## Verificação e aceite

1. Baseline offline e snapshot público allowlisted sem Git/.env.
2. TDD das funções: validações sem envio, threshold exato/zero/negativo/null/ausente, IDs com zeros, reduzidos distintos do mesmo produto, duplicatas e conflitos entre produtos, campos de classificação com texto semelhante a sentinelas.
3. Paginação fixa limitada, orçamento restritivo, ausência de metadados, vazio válido, erro inicial/posterior, sample sem conclusões globais, concorrência sem estado compartilhado e cancelamento com cleanup observado.
4. Registry permanece exatamente sete tools; imports/demonstração sintética sem chave de LLM/configuração real e nenhuma dependência nova.
5. Executar `.venv/Scripts/python.exe -B -m unittest discover -s tests -v` e pip check; revisão independente do conjunto, corrigir achados e revalidar.
6. Reconciliar PRD/README/inventário/runbook e instruções atuais somente no escopo da autorização de Sprint 10. Registrar decisão, resultados reais, limites e G4 somente offline; preservar orçamentos encerrados, ressalvas DEC-027/030/031, sprints alheias e V1 NOT_READY. Atualização protegida de AGENTS.md pelo mecanismo normal, sem bypass se negada.

## Decisões deixadas ao implementador

Nomes dos helpers/estado interno, organização exata dos testes e chaves detalhadas das métricas podem seguir os padrões existentes, desde que consistentes e documentados. Algoritmo de agrupamento O(n) com dict é suficiente. Não instalar bibliotecas, construir framework ou alterar HTTP para simplificar o código.
