# Tributos e Depreciação em Projetos de Software (Aulas 6 e 8)

## Depreciação e amortização

- Método linear: quota = (valor - residual) / vida útil (`depreciacao_linear`).
- Hardware de TI (computadores, servidores): 20% a.a., vida útil de 5 anos (IN RFB 1.700/2017, Anexo III).
- Software desenvolvido e capitalizado (intangível): amortização usual de 20% a.a. (5 anos).
- Depreciação não sai do caixa. O efeito no fluxo é o **escudo fiscal**: redução do IRPJ/CSLL quando o regime permite deduzi-la.

## Lucro Presumido (serviços de software)

Função `tributos_lucro_presumido`.

| Tributo | Base | Alíquota |
| --- | --- | --- |
| ISS | Receita | 2% a 5% (municipal; padrão 5%) |
| PIS (cumulativo) | Receita | 0,65% |
| COFINS (cumulativo) | Receita | 3% |
| IRPJ | 32% da receita | 15% + 10% sobre a base que exceder R$ 240 mil/ano |
| CSLL | 32% da receita | 9% |

Carga sobre a receita: 8,65% (ISS + PIS/COFINS) + 7,68% (IRPJ/CSLL presumidos) = 16,33%, antes do adicional. Depreciação **não** altera o tributo.

## Lucro Real

Função `tributos_lucro_real`.

- PIS 1,65% e COFINS 7,6% não cumulativos (o modelo não considera créditos, o que é conservador) + ISS.
- LAIR = Receita - deduções - OpEx - depreciação.
- IRPJ 15% (+10% adicional) e CSLL 9% sobre o LAIR positivo.
- Prejuízo fiscal é acumulado e compensado em anos seguintes, limitado a 30% do lucro do período.

## Como decidir o regime

Rode o valuation nos dois regimes (o `valuation.py` já faz) e escolha o de maior VPL. Em startups de software com margem alta e pouco crédito de PIS/COFINS, o Presumido tende a vencer. O Simples Nacional (Anexos III ou V, fator R) deve ser avaliado com contador no primeiro ano.
