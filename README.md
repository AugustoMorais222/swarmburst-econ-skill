# Engenharia Econômica Agêntica: skill de valoração de software aplicada ao SwarmBurst

Skill de IA no padrão aberto **Agent Skills** que calcula, projeta e defende a viabilidade financeira de projetos de software. Ela empacota os métodos das Aulas 1 a 12 de Engenharia Econômica (SENAI FATESG) em instruções procedurais e scripts Python determinísticos, e foi validada com os dados do nosso TCC, o **SwarmBurst** (agente autônomo de cloud bursting para Docker Swarm).

**Equipe:** Augusto de Morais, Marcos Antônio e Kaique Bahmad
**Docente:** Msc. Ujeverson Tavares Sampaio

## 1. Descrição e propósito

Líderes técnicos, POs e desenvolvedores tomam decisões econômicas o tempo todo (nuvem x on-premises, manter x refatorar, o que entra na próxima sprint) sem uma ferramenta padronizada. Esta skill ensina o agente a:

| Módulo | O que a skill faz | Aulas |
| --- | --- | --- |
| Processo de decisão | Estrutura alternativas mutuamente exclusivas, incluindo a alternativa nula | 1 e 2 |
| TVM e fluxo de caixa | VP, VF, taxa equivalente, TMA composta, projeção de CapEx e OpEx | 3 e 5 |
| Custo, preço e valor | Custos diretos x indiretos, preço por markup, valor percebido, preço de equilíbrio | 4 |
| Viabilidade | VPL, TIR, payback simples e descontado, IL, CAC, LTV, depreciação, Lucro Presumido x Real | 6 e 8 |
| Proposta econômica | Sumário executivo, ROI do investidor e do cliente, riscos e hipóteses | 7 |
| GVA / EVM | PV, EV, AC, CPI, SPI, EAC, ETC, VAC, TCPI por sprint e impacto do EAC no VPL | 9 |
| Estratégia | Substituição de legado por CAUE, Bom o Suficiente por análise marginal, priorização Valor x Esforço | 10, 11 e 12 |

Princípio de projeto: **o LLM não faz conta**. Todo número sai de `scripts/econ.py` e `scripts/valuation.py`; o modelo coleta premissas, executa e interpreta.

## 2. Plataforma suportada

**Genérica (padrão Agent Skills em `.agents/skills/`)**, testada no **Claude Code**. Por ser só Markdown + Python sem dependências, funciona em qualquer harness compatível com Agent Skills e, como fallback, em qualquer LLM com execução de código.

## 3. Estrutura do repositório

```
.
├── .agents/skills/engenharia-economica-software/
│   ├── SKILL.md                     # frontmatter YAML + instruções procedurais
│   ├── scripts/
│   │   ├── econ.py                  # biblioteca de fórmulas + CLI de cálculos pontuais
│   │   └── valuation.py             # valoração completa a partir de um JSON de premissas
│   ├── references/                  # carregadas sob demanda (camada 3)
│   │   ├── formulas.md
│   │   ├── tributos-depreciacao.md
│   │   ├── gva-evm.md
│   │   ├── estrategia-priorizacao.md
│   │   └── proposta-economica.md
│   └── assets/
│       └── input-template.json      # modelo de premissas
├── examples/
│   ├── swarmburst-input.json        # premissas do TCC
│   ├── tcc-valuation-report.md      # relatório gerado pela skill
│   └── tcc-valuation-result.json    # resultados numéricos
└── tests/test_econ.py               # 16 testes unitários e de integração
```

### Divulgação progressiva

| Camada | Conteúdo | Quando entra no contexto |
| --- | --- | --- |
| 1. Catálogo | `name` + `description` (~100 tokens) | Início da sessão |
| 2. Instruções | Corpo do `SKILL.md` (~900 palavras, bem abaixo de 5.000 tokens) | Quando o pedido casa com a descrição |
| 3. Recursos | Um arquivo de `references/` por etapa; scripts executados, não lidos | Só quando o fluxo exige |

O `SKILL.md` tem uma tabela que mapeia cada tipo de pedido para a única referência necessária, evitando carregar tudo.

## 4. Instalação, carregamento e permissões

Pré-requisito: Python 3.9 ou superior (`python3 --version`). Não há dependências externas.

### Claude Code (testado)

```bash
git clone https://github.com/<usuario>/swarmburst-econ-skill.git
cd swarmburst-econ-skill

# skill do projeto
mkdir -p .claude/skills
cp -r .agents/skills/engenharia-economica-software .claude/skills/

# ou skill pessoal, disponível em qualquer projeto
mkdir -p ~/.claude/skills
cp -r .agents/skills/engenharia-economica-software ~/.claude/skills/
```

No Windows (PowerShell): `Copy-Item -Recurse .agents\skills\engenharia-economica-software .claude\skills\`.

Carregamento: abra o `claude` na pasta e pergunte "quais skills você tem?". A skill aparece pelo nome e é acionada automaticamente quando o pedido casa com a descrição.

Permissões: na primeira execução o Claude Code pede autorização para rodar `python3`. Para liberar só os scripts da skill, adicione em `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": ["Bash(python3 .claude/skills/engenharia-economica-software/scripts/*)"]
  }
}
```

### Harnesses compatíveis com Agent Skills

Mantenha a pasta em `.agents/skills/` (local padrão da especificação) ou copie `engenharia-economica-software/` para o diretório de skills que o harness usa. Libere a execução de `python3` quando o harness pedir.

### Fallback para qualquer LLM

1. Cole o conteúdo de `SKILL.md` como instrução de sistema.
2. Rode os scripts localmente e cole a saída JSON ou o relatório na conversa.

### Verificação

```bash
python3 -m unittest discover -s tests -v
```

## 5. Exemplos de prompts de acionamento

- "Calcula a viabilidade econômica do nosso TCC com as premissas de `examples/swarmburst-input.json`."
- "Qual o VPL, a TIR e o payback descontado desse fluxo: -238800, -78396, 34566, 218402, 452067, 732980, com TMA de 20,58%?"
- "Na sprint 4 temos PV de R$ 118 mil, EV de R$ 109 mil e AC de R$ 123,7 mil, com BAC de R$ 184,8 mil. Como está o projeto e qual o EAC?"
- "Vale mais manter o código legado ou reescrever a partir da versão estável?"
- "Precifica meu SaaS por cluster e compara markup com valor percebido."
- "Prioriza esse backlog por valor e esforço."

Execução direta, sem agente:

```bash
python3 .agents/skills/engenharia-economica-software/scripts/valuation.py examples/swarmburst-input.json --out examples/tcc-valuation-report.md --json examples/tcc-valuation-result.json
python3 .agents/skills/engenharia-economica-software/scripts/econ.py vpl --fluxos "[-1000,500,500,500]" --taxa 0.10
```

## 6. Demonstração: valoração do SwarmBurst

Relatório completo em [`examples/tcc-valuation-report.md`](examples/tcc-valuation-report.md). Resumo do que a skill gerou:

| Indicador | Resultado |
| --- | --- |
| TMA (Selic 13,75% composta com prêmio de 6%) | 20,58% a.a. |
| Investimento (desenvolvimento + hardware) | R$ 238.800,00 |
| VPL (5 anos, sem valor terminal) | **R$ 346.040,99** |
| TIR | **46,50% a.a.** |
| Payback simples / descontado | 3,14 anos / 3,73 anos |
| Índice de lucratividade | 2,45 |
| Preço de equilíbrio da licença | R$ 9.269,43 por cluster/ano |
| LTV / CAC | 17,8x |
| GVA na Sprint 4 | CPI 0,881, SPI 0,922, EAC R$ 209.661,02 |
| VPL com investimento pelo EAC | R$ 321.179,97 |
| Regime tributário recomendado | Lucro Presumido |

Principais achados:

1. **Markup x valor (Aula 4):** o preço por markup (R$ 7.350/cluster/ano) cobre a construção mas não a operação do produto e dá VPL de -R$ 244.469,19. Precificando por valor percebido (R$ 12.000/ano, 19,5% da economia de nuvem do cliente de referência) o projeto fica viável.
2. **GVA (Aula 9):** a Sprint 1, usada para decisões de arquitetura, derrubou o CPI acumulado. O EAC indica estouro de R$ 24.861,02, e a skill leva esse estouro para o VPL.
3. **Legado (Aula 10):** a decisão da Sprint 1 de refazer o código a partir da versão estável tem CAUE de R$ 32.867,55 contra R$ 52.000,00 de manter o legado.
4. **Bom o Suficiente (Aula 11):** validar GCP além da AWS se paga; Azure e testes de caos não.
5. **Modelo de negócio (Aula 7):** open-core com Community gratuito, Pro a R$ 12.000/cluster/ano e Enterprise sob consulta. Para o cliente de referência o SwarmBurst é a alternativa de menor custo presente em 36 meses entre nuvem estática, on-premises e migração para Kubernetes.

As premissas estimadas (projeção de clientes, OpEx pós-lançamento, dados de sprint e custos de manutenção do legado) estão identificadas no relatório e podem ser trocadas no JSON; basta rodar o script de novo.

## 7. Licença

MIT.
