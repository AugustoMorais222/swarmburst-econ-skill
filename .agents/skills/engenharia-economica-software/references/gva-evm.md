# Gerenciamento de Valor Agregado em Sprints (Aula 9)

Função `evm(bac, sprints)` em `scripts/econ.py`.

## Entradas por sprint

| Campo | Significado |
| --- | --- |
| `pv_pct` | fração do BAC planejada para a sprint (a soma de todas deve ser 1,0) |
| `ev_pct` | fração do BAC efetivamente entregue (story points aceitos / total do release) |
| `ac` | custo real da sprint em R$ (horas x custo/hora da equipe + nuvem + licenças) |

Sprints futuras: `ev_pct` e `ac` como `null`.

## Indicadores

| Sigla (PT / EN) | Fórmula | Leitura |
| --- | --- | --- |
| VP / PV | Σ planejado até a data | quanto deveria estar pronto |
| VA / EV | Σ entregue · BAC | quanto vale o que está pronto |
| CR / AC | Σ custo real | quanto já gastamos |
| VC / CV | EV - AC | negativo = acima do custo |
| VPr / SV | EV - PV | negativo = atrasado |
| IDC / CPI | EV / AC | < 1 = cada R$ gasto entrega menos de R$ 1 |
| IDP / SPI | EV / PV | < 1 = ritmo abaixo do planejado |
| EAC | BAC / CPI | custo final se o desempenho de custo se mantiver |
| EAC (custo e prazo) | AC + (BAC - EV) / (CPI · SPI) | cenário mais pessimista |
| ETC | EAC - AC | quanto ainda vamos gastar |
| VAC | BAC - EAC | estouro previsto |
| TCPI | (BAC - EV) / (BAC - AC) | eficiência necessária para fechar no BAC |

## Integração com o valuation

O EAC é a melhor estimativa do investimento real. Recalcule o VPL substituindo o custo direto pelo EAC (`valuation.py` faz isso no cenário "Investimento pelo EAC do GVA"). Assim a eficiência ágil vira impacto financeiro mensurável.

## Leituras típicas

- CPI e SPI baixos só na primeira sprint: sprint de descoberta ou decisão. Recupera se as seguintes ficarem acima de 1.
- TCPI acima de 1,1: fechar no orçamento é improvável. Renegocie escopo usando a priorização Valor x Esforço.
