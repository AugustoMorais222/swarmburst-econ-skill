# Relatório de Valoração Econômica: SwarmBurst

> Gerado pela skill `engenharia-economica-software` (scripts/valuation.py) em 24/11/2026. Todos os números abaixo saem de cálculo determinístico sobre `swarmburst-input.json`.

## Sumário executivo

- **Decisão:** projeto economicamente **VIÁVEL** à TMA de 20,58% a.a.
- **VPL (5 anos, sem valor residual):** R$ 346.040,99
- **TIR:** 46,50% a.a. contra TMA de 20,58% a.a.
- **Payback simples:** 3,14 anos (3 a 2 m); **descontado:** 3,73 anos (3 a 9 m)
- **Índice de lucratividade:** 2,45
- **Investimento inicial (CapEx):** R$ 238.800,00
- **GVA na sprint atual:** CPI 0,881, SPI 0,922, EAC R$ 209.661,02 (BAC R$ 184.800,00)
- **Preço de equilíbrio (VPL = 0):** R$ 9.269,43 por cluster/ano, -22,75% em relação ao preço proposto
- **Markup x valor:** ao preço de markup (R$ 7.350,00) o VPL seria -R$ 244.469,19; o preço por valor percebido torna o produto viável
- **Modelo de negócio:** open-core, com plano Community gratuito como funil e licença Pro anual de R$ 12.000 por cluster, precificada por valor percebido

## 1. Contexto e processo de decisão (Aulas 1 e 2)

O SwarmBurst é o nosso TCC: um agente autônomo de cloud bursting para Docker Swarm. Ele monitora CPU, memória e requisições do cluster, provisiona nós em nuvem pública (AWS EC2) quando a carga passa do threshold, faz o ingresso no Swarm via Ansible e SDKs oficiais de nuvem e desprovisiona quando a demanda normaliza. O núcleo é Java 21 + Micronaut, com coletores gRPC, dashboard React com estimativa de custos e controles de segurança (2FA, JWT, RBAC). A pergunta econômica que respondemos aqui é se vale a pena transformar o TCC em produto comercial.

Estruturamos a decisão em alternativas mutuamente exclusivas, avaliadas pela mesma TMA e no mesmo horizonte:

- **A. Não investir:** Aplicar o capital à TMA. É a alternativa nula: qualquer projeto precisa ter VPL maior que zero para superá-la.
- **B. Produto com licença por cluster (escolhida):** Desenvolver e comercializar o SwarmBurst em modelo open-core, com receita recorrente anual por cluster.
- **C. Projeto sob encomenda:** Vender o desenvolvimento uma única vez pelo preço de markup (seção 3.2). Receita única, sem recorrência e sem escala.

Trade-off técnico x orçamento: o SwarmBurst só faz sentido econômico se a economia de nuvem gerada no cliente superar com folga o preço da licença. Por isso a precificação (seção 3) é validada pelo valor percebido e não apenas pelo custo.

## 2. Premissas financeiras e Valor do Dinheiro no Tempo (Aulas 3 e 5)

| Premissa | Valor | Fonte / justificativa |
| --- | --- | --- |
| Taxa livre de risco (Selic) | 13,75% | Copom, 282ª reunião (04/11/2026): Selic mantida em 13,75% a.a. |
| Prêmio de risco de startup | 6,00% | Premissa da equipe para risco de produto novo |
| TMA = (1+Selic)(1+prêmio) - 1 | 20,58% | Calculada |
| TMA mensal equivalente | 1,571% | (1+TMA)^(1/12) - 1 |
| Câmbio USD/BRL | R$ 5,85 | Dólar comercial fechou a R$ 5,87 em 18/11/2026; usamos R$ 5,85 |
| Horizonte | 5 anos | Vida útil do software (amortização 20% a.a.) |
| Reajuste anual de preço e custos | 4,00% | Premissa alinhada à inflação esperada |

Custo de oportunidade: os R$ 238.800,00 investidos, se aplicados à TMA, virariam R$ 608.584,20 em 5 anos (VF = VP(1+i)^n). O projeto precisa superar isso, e é exatamente o que o VPL mede.

## 3. Custo, preço e valor (Aula 4)

### 3.1 Custos do ciclo de desenvolvimento

| Item | Classificação | Valor |
| --- | --- | --- |
| 2 devs back-end Java/Micronaut (R$ 8.000 x 2 x 6 meses) | Direto | R$ 96.000,00 |
| 1 dev front-end React (R$ 6.500 x 6 meses) | Direto | R$ 39.000,00 |
| 1 eng. DevOps, Ansible e SDKs de nuvem (R$ 5.000 x 6 meses) | Direto | R$ 30.000,00 |
| Designer UI/UX (R$ 4.500 x 2 meses) | Direto | R$ 9.000,00 |
| Nuvem para testes de estresse k6 (R$ 1.200 x 6 meses) | Direto | R$ 7.200,00 |
| Licenças e ferramentas IDE e CI/CD (R$ 600 x 6 meses) | Direto | R$ 3.600,00 |
| Coworking / espaço físico | Indireto (rateio) | R$ 12.000,00 |
| Administração e contabilidade | Indireto (rateio) | R$ 9.000,00 |
| Marketing institucional | Indireto (rateio) | R$ 7.200,00 |
| Reserva de suporte e pós-venda | Indireto (rateio) | R$ 6.000,00 |
| Energia elétrica | Indireto (rateio) | R$ 2.700,00 |
| Internet corporativa | Indireto (rateio) | R$ 2.100,00 |
| **Total diretos** |  | **R$ 184.800,00** |
| **Total indiretos** |  | **R$ 39.000,00** |
| **Custo total do desenvolvimento** |  | **R$ 223.800,00** |

### 3.2 Precificação por markup

| Etapa | Valor |
| --- | --- |
| Custo total | R$ 223.800,00 |
| (+) Lucro 20% sobre o custo | R$ 44.760,00 |
| (=) Base antes dos tributos | R$ 268.560,00 |
| (+) Tributos 8,65% sobre o preço (base / (1 - t)) | R$ 25.430,15 |
| (=) Preço do projeto | R$ 293.990,15 |
| Multiplicador de markup | 1,3136 |

Dividindo o preço de projeto pela meta de 40 licenças chegamos ao preço por markup de **R$ 7.350,00** por cluster/ano. Esse preço cobre o custo de construir, mas não o custo de operar um produto recorrente (equipe, CAC, suporte): com ele o VPL fica em -R$ 244.469,19. Por isso o preço recomendado vem do valor percebido (3.3): **R$ 12.000,00** por cluster/ano (R$ 1.000,00/mês).

### 3.3 Valor percebido pelo cliente

| Perfil | Pico 24/7 (USD/mês) | Burst sob demanda (USD/mês) | Economia (R$/mês) | Licença / economia |
| --- | --- | --- | --- | --- |
| Laboratório do TCC: 2 x t3.medium, pico 40 h/mês | 59,90 | 3,33 | R$ 330,97 | 302% |
| Cliente de referência: 8 x t3.xlarge, pico 60 h/mês | 958,46 | 79,87 | R$ 5.139,76 | 19,5% |

Leitura: no cenário de laboratório do TCC (2 nós t3.medium) a economia não paga a licença Pro, então esse perfil fica no plano gratuito (Community). No perfil de referência a licença consome só 19,5% da economia gerada: o cliente obtém 4,1x de retorno sobre o que paga. Markup define o piso; valor percebido define o teto, e o preço proposto está entre os dois.

## 4. Fluxo de caixa projetado (Aulas 3 e 5)

| Linha | Ano 0 | Ano 1 | Ano 2 | Ano 3 | Ano 4 | Ano 5 |
| --- | --- | --- | --- | --- | --- | --- |
| Clusters novos | - | 10 | 20 | 28 | 34 | 38 |
| Clusters ativos (churn aplicado) | - | 10,0 | 28,8 | 53,3 | 80,9 | 109,2 |
| Licença anual | - | R$ 12.000,00 | R$ 12.480,00 | R$ 12.979,20 | R$ 13.498,37 | R$ 14.038,30 |
| Receita bruta | - | R$ 120.000,00 | R$ 359.424,00 | R$ 692.362,44 | R$ 1.092.594,62 | R$ 1.533.398,10 |
| (-) ISS + PIS/COFINS | - | -R$ 10.380,00 | -R$ 31.090,18 | -R$ 59.889,35 | -R$ 94.509,43 | -R$ 132.638,94 |
| (-) IRPJ + CSLL | - | -R$ 9.216,00 | -R$ 27.603,76 | -R$ 53.173,44 | -R$ 94.874,29 | -R$ 142.833,71 |
| (-) OpEx fixo (equipe + infra SaaS) | - | -R$ 129.600,00 | -R$ 159.984,00 | -R$ 200.383,36 | -R$ 240.798,69 | -R$ 271.230,64 |
| (-) OpEx variável (suporte/infra por cluster) | - | -R$ 4.200,00 | -R$ 12.579,84 | -R$ 24.232,69 | -R$ 38.240,81 | -R$ 53.668,93 |
| (-) CAC (marketing e vendas) | - | -R$ 45.000,00 | -R$ 93.600,00 | -R$ 136.281,60 | -R$ 172.104,19 | -R$ 200.045,81 |
| (-) CapEx (desenvolvimento + hardware) | -R$ 238.800,00 | - | - | - | - | - |
| **Fluxo de caixa livre** | **-R$ 238.800,00** | **-R$ 78.396,00** | **R$ 34.566,22** | **R$ 218.402,01** | **R$ 452.067,19** | **R$ 732.980,06** |
| Fluxo descontado à TMA | -R$ 238.800,00 | -R$ 65.018,45 | R$ 23.775,92 | R$ 124.590,47 | R$ 213.881,84 | R$ 287.611,21 |
| Saldo acumulado | -R$ 238.800,00 | -R$ 317.196,00 | -R$ 282.629,78 | -R$ 64.227,77 | R$ 387.839,43 | R$ 1.120.819,49 |

Regime tributário do cenário base: **Lucro Presumido**. CapEx = desenvolvimento capitalizado (R$ 223.800,00) + hardware do cluster local (R$ 15.000,00). Valores nominais com reajuste de 4% a.a. Não consideramos valor terminal, o que torna o VPL conservador.

## 5. Viabilidade: VPL, TIR e Payback (Aulas 6 e 8)

| Indicador | Resultado | Critério | Leitura |
| --- | --- | --- | --- |
| VPL | R$ 346.040,99 | VPL > 0 | Cria valor acima da TMA |
| TIR | 46,50% | TIR > TMA (20,58%) | Atende |
| Payback simples | 3,14 anos (3 a 2 m) | < 5 anos | Ignora o valor do dinheiro no tempo |
| Payback descontado | 3,73 anos (3 a 9 m) | < 5 anos | Critério de risco/liquidez |
| Índice de lucratividade | 2,45 | IL > 1 | Retorno por real investido |

### 5.1 Sensibilidade

| Cenário | VPL | TIR | Payback descontado |
| --- | --- | --- | --- |
| Base | R$ 346.040,99 | 46,50% | 3,73 anos (3 a 9 m) |
| Preço da licença -20% | R$ 41.892,81 | 24,15% | 4,78 anos (4 a 9 m) |
| Adoção -30% | R$ 11.162,41 | 21,57% | 4,94 anos (4 a 11 m) |
| Churn 20% a.a. | R$ 240.587,46 | 39,95% | 3,98 anos (4 a 0 m) |
| Prêmio de risco +5 p.p. | R$ 235.577,25 | 46,50% | 3,96 anos (4 a 0 m) |
| Investimento pelo EAC do GVA (R$ 209.661,02 em diretos) | R$ 321.179,97 | 43,44% | 3,84 anos (3 a 10 m) |
| Preço por markup (R$ 7.350,00) | -R$ 244.469,19 | -4,86% | não recupera no horizonte |

Preço de equilíbrio (VPL = 0): **R$ 9.269,43** por cluster/ano. Abaixo disso o projeto não remunera a TMA.

## 6. Depreciação e impacto tributário (Aulas 6 e 8)

| Período | Depreciação + amortização |
| --- | --- |
| Ano 1 | R$ 47.760,00 |
| Ano 2 | R$ 47.760,00 |
| Ano 3 | R$ 47.760,00 |
| Ano 4 | R$ 47.760,00 |
| Ano 5 | R$ 47.760,00 |

Software capitalizado amortizado em 5 anos (20% a.a.) e hardware de TI depreciado em 5 anos (20% a.a., IN RFB 1.700/2017). Depreciação não é saída de caixa: ela só afeta o fluxo via imposto. No Lucro Presumido ela não reduz tributo; no Lucro Real ela reduz a base do IRPJ/CSLL.

| Regime | Tributos totais (5 anos) | VPL | TIR |
| --- | --- | --- | --- |
| Lucro Presumido (base) | R$ 656.209,11 | R$ 346.040,99 | 46,50% |
| Lucro Real | R$ 900.417,83 | R$ 245.207,18 | 40,86% |

Resultado: no Lucro Real o escudo fiscal da amortização e a compensação de prejuízos (trava de 30%) existem, mas PIS/COFINS não cumulativos (9,25%, sem créditos no modelo) pesam mais que o ganho no IRPJ/CSLL. Recomendação: **Lucro Presumido**, a validar com contador (o Simples Nacional, com fator R, também deve ser avaliado no primeiro ano).

## 7. Métricas de produto digital: CAC e LTV (Aulas 6 e 8)

| Métrica | Valor | Fórmula |
| --- | --- | --- |
| ARPA (receita média por cluster/ano) | R$ 12.000,00 | Licença anual |
| Margem bruta por cluster | 80,17% | 1 - (tributos + custo variável) / receita |
| Churn anual | 12% | Premissa |
| Vida média do cliente | 8,3 anos | 1 / churn |
| LTV | R$ 80.170,00 | ARPA x margem / churn |
| CAC | R$ 4.500,00 | Marketing + vendas / clusters novos |
| LTV / CAC | 17,8x | Saudável acima de 3x |
| Payback do CAC | 5,6 meses | CAC / margem bruta mensal |

## 8. Eficiência ágil: Gerenciamento de Valor Agregado (Aula 9)

BAC = R$ 184.800,00 (custos diretos do ciclo), distribuído em sprints mensais. Data de status: fim da Sprint 4 (novembro/2026).

| Sprint | VP (PV) acum. | VA (EV) acum. | CR (AC) acum. | VC (CV) | VPr (SV) | IDC (CPI) | IDP (SPI) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Sprint 1 (ago) | R$ 22.176,00 | R$ 9.240,00 | R$ 30.000,00 | -R$ 20.760,00 | -R$ 12.936,00 | 0,308 | 0,417 |
| Sprint 2 (set) | R$ 51.744,00 | R$ 36.960,00 | R$ 61.000,00 | -R$ 24.040,00 | -R$ 14.784,00 | 0,606 | 0,714 |
| Sprint 3 (out) | R$ 85.008,00 | R$ 73.920,00 | R$ 92.500,00 | -R$ 18.580,00 | -R$ 11.088,00 | 0,799 | 0,870 |
| Sprint 4 (nov) | R$ 118.272,00 | R$ 109.032,00 | R$ 123.700,00 | -R$ 14.668,00 | -R$ 9.240,00 | 0,881 | 0,922 |
| Sprint 5 (dez) | R$ 155.232,00 | - | - | - | - | - | - |
| Sprint 6 (jan) | R$ 184.800,00 | - | - | - | - | - | - |

| Previsão | Valor | Fórmula |
| --- | --- | --- |
| % concluído | 59,0% | EV / BAC |
| EAC (desempenho de custo mantido) | R$ 209.661,02 | BAC / CPI |
| EAC (custo e prazo) | R$ 216.945,85 | AC + (BAC - EV) / (CPI x SPI) |
| ETC | R$ 85.961,02 | EAC - AC |
| VAC | -R$ 24.861,02 | BAC - EAC |
| TCPI | 1,240 | (BAC - EV) / (BAC - AC) |

Leitura: A Sprint 1 foi dedicada a decisões internas (funcionamento do agente via cloud-init e estratégia da base de código) e entregou pouco valor com custo cheio, o que derrubou o CPI acumulado. Nas Sprints 3 e 4 o desempenho por sprint ficou acima de 1, mas o acumulado ainda carrega o efeito da Sprint 1. Para fechar no BAC precisaríamos de TCPI acima de 1 até o fim, o que é improvável sem cortar escopo. Integrando ao valuation, se o estouro previsto pelo EAC se confirmar, o VPL cai para R$ 321.179,97 (cenário na seção 5.1).

## 9. Estratégia, legado e "Bom o Suficiente" (Aulas 10, 11 e 12)

### 9.1 Substituição de legado (decisão real da Sprint 1)

Na Sprint 1 tínhamos duas bases de código: X, funcional porém sem padrão e com integrações acopladas, e Y, estável e limpa porém sem integrações. A decisão foi refazer a partir de Y usando X como referência. Avaliamos as duas opções pelo Custo Anual Uniforme Equivalente em 5 anos, com custos de manutenção estimados (retrabalho e correção de defeitos).

| Alternativa | Investimento | Custos anuais | CAUE |
| --- | --- | --- | --- |
| Manter a base X (legado funcional) | R$ 0,00 | R$ 52.000,00, R$ 52.000,00, R$ 52.000,00, R$ 52.000,00, R$ 52.000,00 | R$ 52.000,00 |
| Refazer a partir de Y usando X como referência | R$ 38.000,00 | R$ 20.000,00, R$ 20.000,00, R$ 20.000,00, R$ 20.000,00, R$ 20.000,00 | R$ 32.867,55 |

Decisão pelo menor Custo Anual Uniforme Equivalente: **Refazer a partir de Y usando X como referência**, economia de R$ 19.132,45 por ano equivalente. Isso confirma, em números, a decisão que tomamos na Sprint 1.

### 9.2 Princípio "Bom o Suficiente": cobertura de validação multi-cloud

| Passo | Benefício marginal | Custo marginal | Vale a pena? |
| --- | --- | --- | --- |
| AWS apenas (estado atual) para AWS + GCP | R$ 38.000,00 | R$ 14.000,00 | Sim |
| AWS + GCP para AWS + GCP + Azure | R$ 9.000,00 | R$ 14.000,00 | Não |

Paramos em **AWS + GCP**: a partir daí cada real investido em qualidade retorna menos de um real. Isso é coerente com a limitação do TCC (validação experimental só na AWS): o próximo passo que se paga é validar a GCP. Azure e testes de caos ficam para quando houver demanda de cliente que pague por eles.

### 9.3 Priorização econômica do backlog (Valor x Esforço)

| # | Item | Valor (1-10) | Esforço (pts) | Valor/Esforço | Quadrante |
| --- | --- | --- | --- | --- | --- |
| 1 | 2FA no primeiro login e registro | 6 | 3 | 2,00 | Quick win |
| 2 | Otimização multi-cloud com instâncias spot | 9 | 8 | 1,12 | Quick win |
| 3 | Dashboard de energia e carbono | 5 | 5 | 1,00 | Quick win |
| 4 | Zero Trust (mTLS e rotação de certificados) | 8 | 13 | 0,62 | Projeto estratégico |
| 5 | Escalonamento preditivo por séries temporais | 8 | 13 | 0,62 | Projeto estratégico |
| 6 | Integração com service mesh (canary burst) | 4 | 13 | 0,31 | Evitar |
| 7 | Suporte a serviços stateful | 6 | 21 | 0,29 | Projeto estratégico |
| 8 | Suporte ao Nomad | 3 | 21 | 0,14 | Evitar |

### 9.4 Decisão do cliente: on-premises, nuvem estática, Kubernetes ou SwarmBurst

| Alternativa do cliente | Investimento inicial | Custo mensal | VP dos custos (36 meses) |
| --- | --- | --- | --- |
| Nuvem estática: 8 x t3.xlarge 24/7 | R$ 0,00 | R$ 5.606,99 | R$ 153.264,90 |
| On-premises: comprar 8 servidores para o pico | R$ 96.000,00 | R$ 1.440,00 | R$ 135.361,84 |
| Migrar para Kubernetes (EKS + Cluster Autoscaler) | R$ 60.000,00 | R$ 4.644,29 | R$ 186.949,83 |
| SwarmBurst Pro: burst 60 h/mês + licença | R$ 0,00 | R$ 1.467,24 | R$ 40.106,42 |

Com TMA mensal de 1,571%, a alternativa de menor custo presente para o perfil de referência é **SwarmBurst Pro: burst 60 h/mês + licença**.

## 10. Proposta de modelo de negócio (Aula 7)

Propomos um modelo open-core. O núcleo do agente fica aberto e gratuito para clusters pequenos, o que reduz o CAC e cria comunidade em torno do Swarm. A receita vem da licença Pro por cluster, que libera multi-cloud, o dashboard de FinOps e suporte. O plano Enterprise atende empresas com requisitos de segurança e SLA de suporte. O fluxo de caixa da seção 4 considera apenas a receita Pro, então o Enterprise é potencial de alta não modelado.

| Plano | Preço | Para quem | Limite |
| --- | --- | --- | --- |
| Community | Grátis | Times pequenos e laboratórios | Até 2 nós de burst, só AWS |
| Pro | R$ 12.000/cluster/ano (R$ 1.000/mês) | Empresas com picos sazonais | Até 10 nós de burst, AWS + GCP, dashboard FinOps |
| Enterprise | Sob consulta (a partir de R$ 24.000/cluster/ano) | Ambientes regulados | Nós ilimitados, SSO, mTLS, suporte 24x7 |

**Justificativa de ROI para o cliente:** no perfil de referência o cliente economiza R$ 5.139,76 por mês em nuvem e paga R$ 1.000,00 por mês de licença, um retorno de 4,1x sobre o valor pago, além da redução projetada de 85% a 90% nas violações de SLA durante picos.

## 11. Riscos e hipóteses financeiras

| Risco / hipótese | Impacto | Mitigação |
| --- | --- | --- |
| Adoção abaixo do previsto | VPL cai (cenário Adoção -30%) | Plano Community como funil e parceria com consultorias DevOps |
| Churn maior que 12% a.a. | LTV e VPL menores (cenário Churn 20%) | Onboarding assistido e relatório mensal de economia gerada |
| Estouro de custo do desenvolvimento (CPI < 1) | EAC acima do BAC e investimento maior | Controle de escopo por Valor x Esforço e replanejamento por sprint |
| Resultados experimentais ainda projetados | Economia de ~94% e redução de SLA são estimativas | Substituir pelos dados reais dos testes k6 e reprocessar a skill |
| Câmbio e preços de nuvem em USD | Valor percebido varia com o dólar | Preço em BRL e economia demonstrada no dashboard do cliente |
| Concorrência de Kubernetes gerenciado | Pressão sobre o preço | Posicionamento de zero migração (seção 9.4) |
| Premissas tributárias (ISS municipal entre 2% e 5%) | Carga diferente da modelada | Validar enquadramento com contador |

## 12. Reprodutibilidade

```bash
python3 .agents/skills/engenharia-economica-software/scripts/valuation.py examples/swarmburst-input.json --out examples/tcc-valuation-report.md --json examples/tcc-valuation-result.json
```
