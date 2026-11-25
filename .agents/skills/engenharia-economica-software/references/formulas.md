# Fórmulas: TVM, Fluxo de Caixa, Viabilidade e Métricas de Produto (Aulas 3 a 8)

Funções correspondentes em `scripts/econ.py` indicadas entre parênteses.

## Valor do Dinheiro no Tempo (Aulas 3 e 5)

| Conceito | Fórmula | Função |
| --- | --- | --- |
| Valor futuro | VF = VP (1 + i)^n | `vf` |
| Valor presente | VP = VF / (1 + i)^n | `vp` |
| Taxa equivalente | i_q = (1 + i_p)^(q/p) - 1 | `taxa_equivalente` |
| TMA composta | TMA = (1 + taxa livre de risco)(1 + prêmio) - 1 | `tma_composta` |
| Série uniforme (PMT) | PMT = VP · i / (1 - (1 + i)^-n) | `pmt` |

TMA: menor retorno aceitável. Em projeto de software no Brasil, partimos da Selic vigente (custo de oportunidade sem risco) e somamos um prêmio pelo risco do produto. Use a forma composta para não subestimar a taxa.

## Fluxo de caixa (Aulas 3 e 5)

- **CapEx (investimento):** gastos que geram ativo. Em software, o desenvolvimento capitalizável e o hardware. Entra em t = 0.
- **OpEx (operação):** equipe de manutenção, infraestrutura recorrente, suporte, CAC. Entra em t = 1..n.
- **Fluxo de caixa livre:** FCL_t = Receita_t - Tributos_t - OpEx_t - CapEx_t.
- Depreciação não é saída de caixa. Só afeta o fluxo através do imposto (ver `tributos-depreciacao.md`).

## Custo, preço e valor (Aula 4)

- **Custo direto:** existe só por causa do projeto (horas da equipe alocada, nuvem de testes, licenças do projeto).
- **Custo indireto:** existe de qualquer forma e é rateado (espaço, administração, energia, internet).
- **Markup:** Preço = Custo · (1 + margem) / (1 - alíquota sobre o preço) (`preco_markup`). O imposto incide sobre o preço, por isso a divisão.
- **Valor percebido:** quanto o cliente economiza ou ganha. Para SaaS de infraestrutura: economia = nós · preço/hora · (horas estáticas - horas sob demanda).
- Regra de decisão: markup é o piso (cobre o custo), valor percebido é o teto. O preço deve ficar entre os dois e ser testado no fluxo de caixa. Se o preço de markup gerar VPL negativo, ele cobre a construção mas não a operação do produto.

## Viabilidade (Aulas 6 e 8)

| Indicador | Fórmula | Critério | Função |
| --- | --- | --- | --- |
| VPL | Σ FC_t / (1 + TMA)^t | VPL > 0 | `vpl` |
| TIR | taxa tal que VPL = 0 | TIR > TMA | `tir` (bisseção) |
| Payback simples | primeiro t com saldo acumulado ≥ 0, interpolado | menor que o horizonte | `payback_simples` |
| Payback descontado | idem sobre fluxos descontados | menor que o horizonte | `payback_descontado` |
| Índice de lucratividade | VP das entradas / investimento | IL > 1 | `indice_lucratividade` |

Cuidados:
- TIR pode não existir ou ser múltipla quando o fluxo troca de sinal mais de uma vez. Nesse caso prevalece o VPL.
- Projetos mutuamente exclusivos são comparados pelo VPL, não pela TIR.
- Preço de equilíbrio: preço que zera o VPL (calculado por bisseção em `valuation.py`).

## Métricas de produto digital (Aulas 6 e 8)

| Métrica | Fórmula | Função |
| --- | --- | --- |
| CAC | (marketing + vendas) / clientes novos | entrada |
| LTV | ARPA · margem bruta / churn | `ltv` |
| LTV/CAC | razão; saudável acima de 3 | - |
| Payback do CAC | CAC / (ARPA mensal · margem bruta) | `payback_cac_meses` |
