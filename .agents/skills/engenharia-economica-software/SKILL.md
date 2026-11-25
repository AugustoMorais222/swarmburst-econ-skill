---
name: engenharia-economica-software
description: Valoração e viabilidade econômica de projetos de software. Calcula VP/VF, TMA, fluxo de caixa (CapEx e OpEx), custos diretos e indiretos, preço por markup e por valor percebido, VPL, TIR, payback simples e descontado, CAC/LTV, depreciação e regime tributário (Lucro Presumido x Real), GVA/EVM por sprint (CPI, SPI, EAC), substituição de legado por CAUE, princípio Bom o Suficiente e priorização Valor x Esforço, e gera sumário executivo com riscos. Use quando o usuário pedir viabilidade, ROI, valuation, precificação, VPL/TIR, payback, EVM de sprints, análise on-premises x nuvem, refatorar x manter legado ou priorização econômica de backlog.
license: MIT
compatibility: Python 3.9+ sem dependências externas. Requer permissão para executar python3 nos scripts da skill.
metadata:
  author: Augusto de Morais, Marcos Antônio, Kaique Bahmad
  version: "1.0.0"
  disciplina: Engenharia Econômica - SENAI FATESG
allowed-tools: Bash(python3:*) Read Write
---

# Engenharia Econômica para Projetos de Software

Esta skill transforma dados de um projeto de software em uma valoração econômica auditável. A regra central: **nenhum número financeiro é calculado de cabeça**. Todo cálculo passa pelos scripts em `scripts/`, e o texto final só interpreta o que os scripts retornaram.

## Quando usar

- Pedido de viabilidade, valuation, ROI, VPL, TIR ou payback de software.
- Precificação de software (markup, licença, SaaS) e comparação com valor percebido.
- Acompanhamento de sprints com GVA/EVM (PV, EV, AC, CPI, SPI, EAC).
- Decisões de engenharia como decisões econômicas: on-premises x nuvem, manter x refatorar legado, terceirizar x construir, o que priorizar no backlog.

## Fluxo de trabalho

### 1. Classificar o pedido e carregar só a referência necessária

| Pedido | Leia | Aulas |
| --- | --- | --- |
| Estruturar alternativas, trade-offs | `references/estrategia-priorizacao.md` (seção Processo de decisão) | 1 e 2 |
| VP, VF, TMA, fluxo de caixa, VPL, TIR, payback, CAC/LTV | `references/formulas.md` | 3, 5, 6, 8 |
| Custos diretos/indiretos, markup, valor percebido | `references/formulas.md` (seção Custo, preço e valor) | 4 |
| Depreciação, Lucro Presumido x Real | `references/tributos-depreciacao.md` | 6 e 8 |
| Proposta econômica e sumário executivo | `references/proposta-economica.md` | 7 |
| GVA/EVM por sprint | `references/gva-evm.md` | 9 |
| Legado, Bom o Suficiente, priorização de backlog | `references/estrategia-priorizacao.md` | 10, 11 e 12 |

Valoração completa de um projeto (ex.: TCC) usa todas, mas leia cada uma apenas quando chegar na etapa correspondente.

### 2. Coletar premissas

1. Copie `assets/input-template.json` para o diretório de trabalho e preencha com os dados do usuário.
2. Campos críticos que você deve perguntar se faltarem: custos de desenvolvimento (diretos e indiretos), preço ou modelo de receita, projeção de clientes, OpEx anual e dados de sprint (BAC, % planejado, % entregue, custo real).
3. Campos com padrão aceitável se o usuário não souber, sempre declarados como premissa no relatório:
   - Selic vigente (pesquise a taxa atual antes de usar) e prêmio de risco de 6% para startup.
   - Churn de 12% a.a., reajuste de 4% a.a., horizonte de 5 anos, Lucro Presumido com ISS 5% + PIS 0,65% + COFINS 3%.
   - Software amortizado em 5 anos e hardware de TI depreciado em 5 anos.
4. Nunca invente dados reais (salários, sprints, clientes). Se precisar estimar, marque a linha como estimativa no JSON e avise o usuário.

### 3. Executar os scripts

Valoração completa:

```bash
python3 scripts/valuation.py premissas.json --out relatorio.md --json resultado.json
```

Cálculos pontuais (saída JSON):

```bash
python3 scripts/econ.py vpl --fluxos "[-238800,-78396,34566,218402,452067,732980]" --taxa 0.2058
python3 scripts/econ.py preco --custo 223800 --margem 0.20 --aliquota 0.0865
python3 scripts/econ.py equivalencia --valor 10000 --taxa 0.2058 --n 3
python3 scripts/econ.py evm --json '{"bac":184800,"sprints":[{"nome":"S1","pv_pct":0.12,"ev_pct":0.05,"ac":30000}]}'
```

Os caminhos são relativos à pasta desta skill. Se o harness executar a partir da raiz do repositório, prefixe com o caminho da skill.

### 4. Validar antes de responder

- Confira se a soma dos `pv_pct` das sprints é 1,0 e se `novos_clusters` e `equipe_fixa` têm o tamanho do horizonte.
- Se a TIR vier `null`, os fluxos não trocam de sinal: diga isso em vez de inventar uma taxa.
- Tributo sobre o preço é sempre por divisão: preço = base / (1 - alíquota).
- Se o VPL der negativo, não ajuste premissas para "fazer fechar". Mostre o resultado, o preço de equilíbrio e os cenários de sensibilidade.

### 5. Entregar

Estrutura da resposta (detalhada em `references/proposta-economica.md`):

1. Sumário executivo com decisão (viável ou inviável), VPL, TIR, paybacks e preço de equilíbrio.
2. Fluxo de caixa e indicadores.
3. GVA e impacto do EAC no valuation.
4. Decisões estratégicas (legado, Bom o Suficiente, priorização).
5. Modelo de negócio com ROI do cliente.
6. Riscos e hipóteses, deixando explícito o que é estimativa.

Formate valores em reais no padrão brasileiro (R$ 1.234,56) e percentuais com vírgula.

## Exemplo de gatilhos

- "Calcula a viabilidade do meu TCC com essas premissas."
- "Qual o VPL e a TIR desse fluxo a uma TMA de 18%?"
- "Minha sprint 4 tem PV 118 mil, EV 109 mil e AC 123 mil. Como estou?"
- "Vale mais manter o código legado ou refatorar?"
- "Como precificar meu SaaS por cluster?"

## Limitações

- Modelo anual, sem valor terminal (conservador).
- Lucro Real modelado sem créditos de PIS/COFINS; Simples Nacional não modelado.
- A qualidade do resultado depende das premissas; o relatório sempre lista quais são estimativas.
