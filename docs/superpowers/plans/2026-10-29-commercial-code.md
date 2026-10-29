# Código comercial prioritário — desenho e plano

Aprovação: mantenedor autorizou implementar e validar diretamente, sem
aprovações intermediárias. Até duas requisições reais filtradas pelo
código informado, cada uma limitada a 20 registros; zero retries/login,
.env somente pelo loader em memória e sem alteração/disclosure. Nenhuma
permissão para scan adicional, preço/estoque, MCP ou próximas sprints.

## Desenho

Usar o filtro documentado mascara:string de POST produto/reduzidos.
O3 foi relida após renderização; não publica filtro codigoSku nessa rota.
Alternativa descartada: repetir varredura local das primeiras páginas,
que já deixou o código fora da amostra. Não chamar máscara de codigoSku
nem mudar silenciosamente search_product_by_sku. Para o vocabulário do
operador (código/SKU comercial), priorizar a nova search_product_by_code.
Não existe camada conversacional/registro MCP ainda; a prioridade será
contrato documentado da função, não roteamento por LLM fictício.

client.py: adicionar product_mask: str | None = None keyword-only em
_query/_collect, somente products. Quando presente, enviar exatamente
mascara: product_mask além de page/limit. Strings1–256, não whitespace-only,
sem categorias C; preservar zeros, caixa, espaços e pontuação. Sem dict
arbitrário; bloquear combinação product_id+product_mask até contrato
próprio, preservar comportamento de todos os defaults anteriores.

O fornecedor não documenta igualdade exata do filtro. Não rejeitar uma
página só por retornar máscaras parciais; receber pelo coletor limitado e
filtrar igualdade exata no aplicativo. Nunca equiparar mascara a idProduto,
idReduzido ou codigoSku. Preservar metadados/errors/partial após filtragem.
Só percurso válido completo permite found/not_found no universo consultado.

Interface: async search_product_by_code(client: NetOneClient, code: str,
max_results: int = 20) -> dict[str, object]. Código1–256 e budget inteiro
estrito1–1000/cap configurado, linhas recebidas inclusive não matches.
Retorno mantém product_mask e sku técnicos separados, precisão/null,
reduzidos distintos e aviso remote_product_code_exact_match. Pequenos
helpers reutilizam validação e projeção final de filtros locais existentes,
sem trocar a semântica de texto/SKU/EAN ou alterar normalizador/servidor.

## Plano de execução nativa

- [ ] Snapshot público antes de código, sem Git/.git/.env/venv traversal.
- [ ] TDD RED: contrato product_mask fechado somente products, invalidez/
  combinação sem envio, defaults, paginação/concurrency isolada; nova
  função exata/máscara versus outro campo, zeros/case/espaços, erros/
  partial/missing/null/JSON. Usar códigos sintéticos, nunca o valor real.
- [ ] Implementar somente client.py/tools.py e testes correspondentes.
- [ ] GREEN focado e suíte completa, pip check, imports/compilação/linhas.
- [ ] Prova real uma vez: chamada pública por código, teto2 requests
  products com mascara, page<=2, limit<=20, orçamento20/caps existentes.
  Guardas permanecem; não repetir após falha. Confirmar mascara/codigoSku/
  descrição apenas em memória; resposta útil ao operador pode ser mostrada
  no chat. Projeto/scratch retêm somente invariantes/contagens/status.
- [ ] Atualizar PRD1.5.0/DEC025 e docs afetadas com prioridade comercial e
  evidência real, preservando estados/textos das tarefas de sprint. S7.11
  não fecha por troca implícita de codigoSku por mascara.
- [ ] Revisão independente final, uma correção se necessária, auditoria
  final e resultado concreto ao usuário. Sem commit/install/outro sprint.
