# Decisão, Legado, Bom o Suficiente e Priorização (Aulas 1, 2, 10, 11 e 12)

## Processo de decisão (Aulas 1 e 2)

1. Definir o problema em termos econômicos (custo evitado, receita gerada, risco reduzido).
2. Listar alternativas mutuamente exclusivas, incluindo a alternativa nula (não fazer e aplicar à TMA).
3. Estimar fluxos de cada alternativa no mesmo horizonte e com a mesma TMA.
4. Escolher pelo VPL (ou menor VP de custos / CAUE quando só há custos).
5. Registrar premissas e riscos.

Decisões de engenharia típicas: on-premises x nuvem, manter x refatorar, construir x terceirizar, lançar agora x na próxima sprint.

## Substituição e aposentadoria de legado (Aula 10)

Função `substituicao(defensor, desafiante, taxa)`.

- **Defensor:** o que já existe (código legado, servidor atual). Custo de investimento passado é custo afundado e não entra.
- **Desafiante:** a alternativa nova (refatoração, reescrita, novo serviço).
- Compare pelo **CAUE** (Custo Anual Uniforme Equivalente): VP de todos os custos convertido em série uniforme (`caue`). Menor CAUE vence.

## Princípio "Bom o Suficiente" (Aula 11)

Função `bom_o_suficiente(niveis)`.

Qualidade tem custo de oportunidade. Para cada nível de qualidade (cobertura de testes, provedores validados, SLA alvo), compare benefício marginal e custo marginal. Avance enquanto benefício marginal > custo marginal; pare no primeiro passo que não se paga.

## Priorização econômica do backlog (Aula 12)

Função `priorizar_backlog(itens)`.

- Cada item recebe valor (1 a 10, ou R$) e esforço (story points ou R$).
- Ordenação por razão valor / esforço.
- Quadrantes: Quick win (alto valor, baixo esforço), Projeto estratégico (alto valor, alto esforço), Preenchimento (baixo valor, baixo esforço), Evitar (baixo valor, alto esforço).
- Limiares padrão: valor ≥ 5 e esforço > 8 pontos. Ajuste ao contexto do time.
