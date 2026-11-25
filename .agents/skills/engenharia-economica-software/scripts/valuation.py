"""Gera a valoração econômica completa de um projeto de software a partir de um JSON de premissas."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import econ  # noqa: E402


def brl(x: float | None) -> str:
    """Formata valor em reais no padrão brasileiro."""
    if x is None:
        return "n/d"
    s = f"{abs(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"-R$ {s}" if x < 0 else f"R$ {s}"


def pct(x: float | None, casas: int = 2) -> str:
    """Formata percentual no padrão brasileiro."""
    return "n/d" if x is None else f"{x * 100:.{casas}f}%".replace(".", ",")


def num(x: float | None, casas: int = 2) -> str:
    """Formata número decimal no padrão brasileiro."""
    return "n/d" if x is None else f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def anos(x: float | None) -> str:
    """Formata prazo em anos e meses."""
    if x is None:
        return "não recupera no horizonte"
    a = int(x)
    m = round((x - a) * 12)
    if m == 12:
        a, m = a + 1, 0
    return f"{num(x)} anos ({a} a {m} m)"


def tma(cfg: dict) -> float:
    """TMA composta a partir da taxa livre de risco e do prêmio de risco do projeto."""
    m = cfg["macro"]
    return econ.tma_composta(m["selic"], m["premio_risco"])


def custo_desenvolvimento(cfg: dict) -> dict:
    """Separa custos diretos e indiretos do ciclo de desenvolvimento."""
    d = sum(i["valor"] for i in cfg["custos_desenvolvimento"]["diretos"])
    ind = sum(i["valor"] for i in cfg["custos_desenvolvimento"]["indiretos"])
    return {"diretos": d, "indiretos": ind, "total": d + ind}


def projetar(cfg: dict, regime: str | None = None) -> dict:
    """Projeta o fluxo de caixa anual (t = 0 investimento; t = 1..H operação) e calcula os indicadores."""
    h = cfg["projeto"]["horizonte_anos"]
    pr, mk, op = cfg["precificacao"], cfg["mercado"], cfg["opex"]
    reaj = pr.get("reajuste_anual", 0.0)
    regime = regime or cfg["tributacao"]["regime"]
    dev = custo_desenvolvimento(cfg)
    hw = cfg["capex_hardware"]
    capex = dev["total"] + hw["valor"]
    dep_sw = econ.depreciacao_linear(dev["total"], cfg["vida_util_software"], horizonte=h)
    dep_hw = econ.depreciacao_linear(hw["valor"], hw["vida_util"], horizonte=h)
    linhas, ativos = [], 0.0
    for t in range(1, h + 1):
        f = (1 + reaj) ** (t - 1)
        novos = mk["novos_clusters"][t - 1]
        ativos = ativos * (1 - mk["churn_anual"]) + novos
        preco = pr["licenca_anual_cluster"] * f
        receita = ativos * preco
        cac = novos * mk["cac"] * f
        var = ativos * op["custo_variavel_cluster"] * f
        fixo = op["equipe_fixa"][t - 1] + op["infra_saas_anual"] * f
        linhas.append({"ano": t, "novos": novos, "ativos": ativos, "preco": preco, "receita": receita,
                       "cac": cac, "variavel": var, "fixo": fixo, "opex": cac + var + fixo,
                       "depreciacao": dep_sw[t - 1] + dep_hw[t - 1]})
    if regime == "real":
        trib = econ.tributos_lucro_real([l["receita"] for l in linhas], [l["opex"] for l in linhas],
                                        [l["depreciacao"] for l in linhas])
    else:
        trib = [econ.tributos_lucro_presumido(l["receita"]) for l in linhas]
    for l, tr in zip(linhas, trib):
        l["deducoes"] = tr["deducoes"]
        l["irpj_csll"] = tr["irpj_csll"]
        l["tributos"] = tr["total"]
        l["fcl"] = l["receita"] - l["tributos"] - l["opex"]
    fluxos = [-capex] + [l["fcl"] for l in linhas]
    i = tma(cfg)
    return {"regime": regime, "capex": capex, "dev": dev, "linhas": linhas, "fluxos": fluxos,
            "acumulado": econ.acumulado(fluxos),
            "descontados": [fc / (1 + i) ** t for t, fc in enumerate(fluxos)],
            "vpl": econ.vpl(fluxos, i), "tir": econ.tir(fluxos),
            "payback_simples": econ.payback_simples(fluxos), "payback_descontado": econ.payback_descontado(fluxos, i),
            "il": econ.indice_lucratividade(fluxos, i), "tma": i}


def com(cfg: dict, **mudancas) -> dict:
    """Cópia das premissas com alterações pontuais para análise de sensibilidade."""
    c = copy.deepcopy(cfg)
    if "preco_mult" in mudancas:
        c["precificacao"]["licenca_anual_cluster"] *= mudancas["preco_mult"]
    if "adocao_mult" in mudancas:
        c["mercado"]["novos_clusters"] = [n * mudancas["adocao_mult"] for n in c["mercado"]["novos_clusters"]]
    if "diretos_mult" in mudancas:
        for item in c["custos_desenvolvimento"]["diretos"]:
            item["valor"] *= mudancas["diretos_mult"]
    if "premio_extra" in mudancas:
        c["macro"]["premio_risco"] += mudancas["premio_extra"]
    if "churn" in mudancas:
        c["mercado"]["churn_anual"] = mudancas["churn"]
    return c


def preco_equilibrio(cfg: dict) -> float:
    """Licença anual mínima que zera o VPL (bisseção sobre o multiplicador de preço)."""
    lo, hi = 0.01, 5.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if projetar(com(cfg, preco_mult=mid))["vpl"] > 0:
            hi = mid
        else:
            lo = mid
    return cfg["precificacao"]["licenca_anual_cluster"] * hi


def economia_cliente(perfil: dict, cambio: float) -> dict:
    """Economia mensal do cliente ao trocar capacidade de pico 24/7 por burst sob demanda."""
    estatico = perfil["nos"] * perfil["preco_hora_usd"] * perfil["horas_mes_estatico"]
    burst = perfil["nos"] * perfil["preco_hora_usd"] * perfil["horas_mes_burst"]
    return {"estatico_usd": estatico, "burst_usd": burst, "economia_usd": estatico - burst,
            "economia_brl": (estatico - burst) * cambio, "reducao": 1 - burst / estatico}


def tabela(cabecalho: list[str], linhas: list[list[str]]) -> str:
    """Monta tabela Markdown."""
    out = ["| " + " | ".join(cabecalho) + " |", "|" + "|".join([" --- "] * len(cabecalho)) + "|"]
    out += ["| " + " | ".join(l) + " |" for l in linhas]
    return "\n".join(out)


def relatorio(cfg: dict) -> tuple[str, dict]:
    """Gera o relatório Markdown e o dicionário de resultados."""
    p, m, pr = cfg["projeto"], cfg["macro"], cfg["precificacao"]
    base = projetar(cfg)
    alt = projetar(cfg, "real" if base["regime"] == "presumido" else "presumido")
    i = base["tma"]
    i_mes = econ.taxa_equivalente(i, 1, 1 / 12)
    dev = base["dev"]
    mk = econ.preco_markup(dev["total"], pr["margem"], pr["aliquota_preco"])
    ev = econ.evm(cfg["evm"]["bac"], cfg["evm"]["sprints"])
    proj_eac = projetar(com(cfg, diretos_mult=ev["eac"] / cfg["evm"]["bac"]))
    pe = preco_equilibrio(cfg)
    proj_markup = projetar(com(cfg, preco_mult=pr["licenca_markup"] / pr["licenca_anual_cluster"])) if "licenca_markup" in pr else None
    cambio = m["cambio_usd_brl"]
    lab = economia_cliente(cfg["valor_cliente"]["perfil_lab"], cambio)
    ref = economia_cliente(cfg["valor_cliente"]["perfil_referencia"], cambio)
    licenca_mes = pr["licenca_anual_cluster"] / 12
    l1 = base["linhas"][0]
    margem_bruta = 1 - (l1["deducoes"] + l1["irpj_csll"] + l1["variavel"]) / l1["receita"]
    ltv = econ.ltv(pr["licenca_anual_cluster"], margem_bruta, cfg["mercado"]["churn_anual"])
    cac = cfg["mercado"]["cac"]
    leg = cfg["legado"]
    sub = econ.substituicao(leg["defensor"], leg["desafiante"], i)
    back = econ.priorizar_backlog(cfg["backlog"])
    bos = econ.bom_o_suficiente(cfg["bom_o_suficiente"]["niveis"])
    cen = [
        ("Base", base),
        ("Preço da licença -20%", projetar(com(cfg, preco_mult=0.8))),
        ("Adoção -30%", projetar(com(cfg, adocao_mult=0.7))),
        ("Churn 20% a.a.", projetar(com(cfg, churn=0.20))),
        ("Prêmio de risco +5 p.p.", projetar(com(cfg, premio_extra=0.05))),
        (f"Investimento pelo EAC do GVA ({brl(ev['eac'])} em diretos)", proj_eac),
    ]
    if proj_markup:
        cen.append((f"Preço por markup ({brl(pr['licenca_markup'])})", proj_markup))
    alt_cli = cfg["alternativas_cliente"]
    i_cli_mes = econ.taxa_equivalente(i, 1, 1 / 12)
    meses = alt_cli["meses"]
    vp_alt = []
    for a in alt_cli["opcoes"]:
        mensal = a.get("mensal_usd", 0.0) * cambio + a.get("mensal_brl", 0.0)
        vp_c = a.get("inicial_brl", 0.0) + sum(mensal / (1 + i_cli_mes) ** k for k in range(1, meses + 1))
        vp_alt.append((a["nome"], a.get("inicial_brl", 0.0), mensal, vp_c))
    melhor_alt = min(vp_alt, key=lambda x: x[3])

    r = []
    r.append(f"# Relatório de Valoração Econômica: {p['nome']}\n")
    r.append(f"> Gerado pela skill `engenharia-economica-software` (scripts/valuation.py) em {p['data_base']}. "
             f"Todos os números abaixo saem de cálculo determinístico sobre `{p.get('arquivo_premissas', 'premissas.json')}`.\n")
    r.append("## Sumário executivo\n")
    decisao = "VIÁVEL" if base["vpl"] > 0 else "INVIÁVEL"
    r.append(f"- **Decisão:** projeto economicamente **{decisao}** à TMA de {pct(i)} a.a.")
    r.append(f"- **VPL (5 anos, sem valor residual):** {brl(base['vpl'])}")
    r.append(f"- **TIR:** {pct(base['tir'])} a.a. contra TMA de {pct(i)} a.a.")
    r.append(f"- **Payback simples:** {anos(base['payback_simples'])}; **descontado:** {anos(base['payback_descontado'])}")
    r.append(f"- **Índice de lucratividade:** {num(base['il'])}")
    r.append(f"- **Investimento inicial (CapEx):** {brl(base['capex'])}")
    r.append(f"- **GVA na sprint atual:** CPI {num(ev['status']['cpi'], 3)}, SPI {num(ev['status']['spi'], 3)}, EAC {brl(ev['eac'])} (BAC {brl(ev['bac'])})")
    r.append(f"- **Preço de equilíbrio (VPL = 0):** {brl(pe)} por cluster/ano, {pct(pe / pr['licenca_anual_cluster'] - 1)} em relação ao preço proposto")
    if proj_markup:
        r.append(f"- **Markup x valor:** ao preço de markup ({brl(pr['licenca_markup'])}) o VPL seria {brl(proj_markup['vpl'])}; o preço por valor percebido torna o produto viável")
    r.append(f"- **Modelo de negócio:** {cfg['modelo_negocio']['resumo']}\n")

    r.append("## 1. Contexto e processo de decisão (Aulas 1 e 2)\n")
    r.append(p["descricao"] + "\n")
    r.append("Estruturamos a decisão em alternativas mutuamente exclusivas, avaliadas pela mesma TMA e no mesmo horizonte:\n")
    for a in cfg["alternativas_decisao"]:
        r.append(f"- **{a['nome']}:** {a['descricao']}")
    r.append("\nTrade-off técnico x orçamento: o SwarmBurst só faz sentido econômico se a economia de nuvem gerada no cliente "
             "superar com folga o preço da licença. Por isso a precificação (seção 3) é validada pelo valor percebido e não apenas pelo custo.\n")

    r.append("## 2. Premissas financeiras e Valor do Dinheiro no Tempo (Aulas 3 e 5)\n")
    r.append(tabela(["Premissa", "Valor", "Fonte / justificativa"], [
        ["Taxa livre de risco (Selic)", pct(m["selic"]), m["fontes"]["selic"]],
        ["Prêmio de risco de startup", pct(m["premio_risco"]), "Premissa da equipe para risco de produto novo"],
        ["TMA = (1+Selic)(1+prêmio) - 1", pct(i), "Calculada"],
        ["TMA mensal equivalente", pct(i_mes, 3), "(1+TMA)^(1/12) - 1"],
        ["Câmbio USD/BRL", f"R$ {num(cambio)}", m["fontes"]["cambio"]],
        ["Horizonte", f"{p['horizonte_anos']} anos", "Vida útil do software (amortização 20% a.a.)"],
        ["Reajuste anual de preço e custos", pct(pr.get("reajuste_anual", 0)), "Premissa alinhada à inflação esperada"],
    ]))
    vf_cap = econ.vf(base["capex"], i, p["horizonte_anos"])
    r.append(f"\nCusto de oportunidade: os {brl(base['capex'])} investidos, se aplicados à TMA, virariam "
             f"{brl(vf_cap)} em {p['horizonte_anos']} anos (VF = VP(1+i)^n). O projeto precisa superar isso, e é exatamente o que o VPL mede.\n")

    r.append("## 3. Custo, preço e valor (Aula 4)\n")
    r.append("### 3.1 Custos do ciclo de desenvolvimento\n")
    linhas_c = [[c["item"], "Direto", brl(c["valor"])] for c in cfg["custos_desenvolvimento"]["diretos"]]
    linhas_c += [[c["item"], "Indireto (rateio)", brl(c["valor"])] for c in cfg["custos_desenvolvimento"]["indiretos"]]
    linhas_c += [["**Total diretos**", "", f"**{brl(dev['diretos'])}**"], ["**Total indiretos**", "", f"**{brl(dev['indiretos'])}**"],
                 ["**Custo total do desenvolvimento**", "", f"**{brl(dev['total'])}**"]]
    r.append(tabela(["Item", "Classificação", "Valor"], linhas_c))
    r.append("\n### 3.2 Precificação por markup\n")
    r.append(tabela(["Etapa", "Valor"], [
        ["Custo total", brl(mk["custo_total"])],
        [f"(+) Lucro {pct(pr['margem'], 0)} sobre o custo", brl(mk["lucro"])],
        ["(=) Base antes dos tributos", brl(mk["base_antes_tributos"])],
        [f"(+) Tributos {pct(pr['aliquota_preco'])} sobre o preço (base / (1 - t))", brl(mk["tributos"])],
        ["(=) Preço do projeto", brl(mk["preco"])],
        ["Multiplicador de markup", num(mk["markup_multiplicador"], 4)],
    ]))
    if "licenca_markup" in pr:
        r.append(f"\nDividindo o preço de projeto pela meta de {pr.get('licencas_meta_markup', 40)} licenças chegamos ao preço por markup de "
                 f"**{brl(pr['licenca_markup'])}** por cluster/ano. Esse preço cobre o custo de construir, mas não o custo de operar um produto recorrente "
                 f"(equipe, CAC, suporte): com ele o VPL fica em {brl(proj_markup['vpl'])}. Por isso o preço recomendado vem do valor percebido (3.3): "
                 f"**{brl(pr['licenca_anual_cluster'])}** por cluster/ano ({brl(licenca_mes)}/mês).\n")
    r.append("### 3.3 Valor percebido pelo cliente\n")
    r.append(tabela(["Perfil", "Pico 24/7 (USD/mês)", "Burst sob demanda (USD/mês)", "Economia (R$/mês)", "Licença / economia"], [
        [cfg["valor_cliente"]["perfil_lab"]["descricao"], num(lab["estatico_usd"]), num(lab["burst_usd"]), brl(lab["economia_brl"]), pct(licenca_mes / lab["economia_brl"], 0)],
        [cfg["valor_cliente"]["perfil_referencia"]["descricao"], num(ref["estatico_usd"]), num(ref["burst_usd"]), brl(ref["economia_brl"]), pct(licenca_mes / ref["economia_brl"], 1)],
    ]))
    r.append(f"\nLeitura: no cenário de laboratório do TCC (2 nós t3.medium) a economia não paga a licença Pro, então esse perfil fica no plano gratuito (Community). "
             f"No perfil de referência a licença consome só {pct(licenca_mes / ref['economia_brl'], 1)} da economia gerada: "
             f"o cliente obtém {num((ref['economia_brl'] - licenca_mes) / licenca_mes, 1)}x de retorno sobre o que paga. "
             "Markup define o piso; valor percebido define o teto, e o preço proposto está entre os dois.\n")

    r.append("## 4. Fluxo de caixa projetado (Aulas 3 e 5)\n")
    cab = ["Linha", "Ano 0"] + [f"Ano {l['ano']}" for l in base["linhas"]]
    L = base["linhas"]
    r.append(tabela(cab, [
        ["Clusters novos", "-"] + [num(l["novos"], 0) for l in L],
        ["Clusters ativos (churn aplicado)", "-"] + [num(l["ativos"], 1) for l in L],
        ["Licença anual", "-"] + [brl(l["preco"]) for l in L],
        ["Receita bruta", "-"] + [brl(l["receita"]) for l in L],
        ["(-) ISS + PIS/COFINS", "-"] + [brl(-l["deducoes"]) for l in L],
        ["(-) IRPJ + CSLL", "-"] + [brl(-l["irpj_csll"]) for l in L],
        ["(-) OpEx fixo (equipe + infra SaaS)", "-"] + [brl(-l["fixo"]) for l in L],
        ["(-) OpEx variável (suporte/infra por cluster)", "-"] + [brl(-l["variavel"]) for l in L],
        ["(-) CAC (marketing e vendas)", "-"] + [brl(-l["cac"]) for l in L],
        ["(-) CapEx (desenvolvimento + hardware)", brl(-base["capex"])] + ["-" for _ in L],
        ["**Fluxo de caixa livre**"] + [f"**{brl(x)}**" for x in base["fluxos"]],
        ["Fluxo descontado à TMA"] + [brl(x) for x in base["descontados"]],
        ["Saldo acumulado"] + [brl(x) for x in base["acumulado"]],
    ]))
    r.append(f"\nRegime tributário do cenário base: **Lucro {base['regime'].capitalize()}**. CapEx = desenvolvimento capitalizado "
             f"({brl(dev['total'])}) + hardware do cluster local ({brl(cfg['capex_hardware']['valor'])}). Valores nominais com reajuste de "
             f"{pct(pr.get('reajuste_anual', 0), 0)} a.a. Não consideramos valor terminal, o que torna o VPL conservador.\n")

    r.append("## 5. Viabilidade: VPL, TIR e Payback (Aulas 6 e 8)\n")
    r.append(tabela(["Indicador", "Resultado", "Critério", "Leitura"], [
        ["VPL", brl(base["vpl"]), "VPL > 0", "Cria valor acima da TMA" if base["vpl"] > 0 else "Destrói valor"],
        ["TIR", pct(base["tir"]), f"TIR > TMA ({pct(i)})", "Atende" if (base["tir"] or 0) > i else "Não atende"],
        ["Payback simples", anos(base["payback_simples"]), f"< {p['horizonte_anos']} anos", "Ignora o valor do dinheiro no tempo"],
        ["Payback descontado", anos(base["payback_descontado"]), f"< {p['horizonte_anos']} anos", "Critério de risco/liquidez"],
        ["Índice de lucratividade", num(base["il"]), "IL > 1", "Retorno por real investido"],
    ]))
    r.append("\n### 5.1 Sensibilidade\n")
    r.append(tabela(["Cenário", "VPL", "TIR", "Payback descontado"],
                    [[n, brl(c["vpl"]), pct(c["tir"]), anos(c["payback_descontado"])] for n, c in cen]))
    r.append(f"\nPreço de equilíbrio (VPL = 0): **{brl(pe)}** por cluster/ano. Abaixo disso o projeto não remunera a TMA.\n")

    r.append("## 6. Depreciação e impacto tributário (Aulas 6 e 8)\n")
    dep_rows = [[f"Ano {l['ano']}", brl(l["depreciacao"])] for l in L]
    r.append(tabela(["Período", "Depreciação + amortização"], dep_rows))
    r.append(f"\nSoftware capitalizado amortizado em {cfg['vida_util_software']} anos (20% a.a.) e hardware de TI depreciado em "
             f"{cfg['capex_hardware']['vida_util']} anos (20% a.a., IN RFB 1.700/2017). Depreciação não é saída de caixa: "
             "ela só afeta o fluxo via imposto. No Lucro Presumido ela não reduz tributo; no Lucro Real ela reduz a base do IRPJ/CSLL.\n")
    r.append(tabela(["Regime", "Tributos totais (5 anos)", "VPL", "TIR"], [
        [f"Lucro {base['regime'].capitalize()} (base)", brl(sum(l["tributos"] for l in base["linhas"])), brl(base["vpl"]), pct(base["tir"])],
        [f"Lucro {alt['regime'].capitalize()}", brl(sum(l["tributos"] for l in alt["linhas"])), brl(alt["vpl"]), pct(alt["tir"])],
    ]))
    melhor_reg = base if base["vpl"] >= alt["vpl"] else alt
    if melhor_reg is base:
        motivo = ("no Lucro Real o escudo fiscal da amortização e a compensação de prejuízos (trava de 30%) existem, mas PIS/COFINS não cumulativos "
                  "(9,25%, sem créditos no modelo) pesam mais que o ganho no IRPJ/CSLL")
    else:
        motivo = ("no Lucro Real a amortização do software e a compensação dos prejuízos iniciais reduzem o IRPJ/CSLL o suficiente para "
                  "compensar o PIS/COFINS não cumulativo (9,25%, sem créditos no modelo)")
    r.append(f"\nResultado: {motivo}. Recomendação: **Lucro {melhor_reg['regime'].capitalize()}**, a validar com contador "
             "(o Simples Nacional, com fator R, também deve ser avaliado no primeiro ano).\n")

    r.append("## 7. Métricas de produto digital: CAC e LTV (Aulas 6 e 8)\n")
    r.append(tabela(["Métrica", "Valor", "Fórmula"], [
        ["ARPA (receita média por cluster/ano)", brl(pr["licenca_anual_cluster"]), "Licença anual"],
        ["Margem bruta por cluster", pct(margem_bruta), "1 - (tributos + custo variável) / receita"],
        ["Churn anual", pct(cfg["mercado"]["churn_anual"], 0), "Premissa"],
        ["Vida média do cliente", f"{num(1 / cfg['mercado']['churn_anual'], 1)} anos", "1 / churn"],
        ["LTV", brl(ltv), "ARPA x margem / churn"],
        ["CAC", brl(cac), "Marketing + vendas / clusters novos"],
        ["LTV / CAC", num(ltv / cac, 1) + "x", "Saudável acima de 3x"],
        ["Payback do CAC", f"{num(econ.payback_cac_meses(cac, pr['licenca_anual_cluster'], margem_bruta), 1)} meses", "CAC / margem bruta mensal"],
    ]))
    r.append("")

    r.append("## 8. Eficiência ágil: Gerenciamento de Valor Agregado (Aula 9)\n")
    r.append(f"BAC = {brl(ev['bac'])} (custos diretos do ciclo), distribuído em sprints mensais. Data de status: {cfg['evm']['data_status']}.\n")
    ev_rows = []
    for l in ev["linhas"]:
        if l["ev"] is None:
            ev_rows.append([l["sprint"], brl(l["pv"]), "-", "-", "-", "-", "-", "-"])
        else:
            ev_rows.append([l["sprint"], brl(l["pv"]), brl(l["ev"]), brl(l["ac"]), brl(l["cv"]), brl(l["sv"]), num(l["cpi"], 3), num(l["spi"], 3)])
    r.append(tabela(["Sprint", "VP (PV) acum.", "VA (EV) acum.", "CR (AC) acum.", "VC (CV)", "VPr (SV)", "IDC (CPI)", "IDP (SPI)"], ev_rows))
    r.append("\n" + tabela(["Previsão", "Valor", "Fórmula"], [
        ["% concluído", pct(ev["percentual_concluido"], 1), "EV / BAC"],
        ["EAC (desempenho de custo mantido)", brl(ev["eac"]), "BAC / CPI"],
        ["EAC (custo e prazo)", brl(ev["eac_cpi_spi"]), "AC + (BAC - EV) / (CPI x SPI)"],
        ["ETC", brl(ev["etc"]), "EAC - AC"],
        ["VAC", brl(ev["vac"]), "BAC - EAC"],
        ["TCPI", num(ev["tcpi"], 3), "(BAC - EV) / (BAC - AC)"],
    ]))
    r.append(f"\nLeitura: {cfg['evm']['leitura']} Integrando ao valuation, se o estouro previsto pelo EAC se confirmar, "
             f"o VPL cai para {brl(proj_eac['vpl'])} (cenário na seção 5.1).\n")

    r.append("## 9. Estratégia, legado e \"Bom o Suficiente\" (Aulas 10, 11 e 12)\n")
    r.append("### 9.1 Substituição de legado (decisão real da Sprint 1)\n")
    r.append(leg["contexto"] + "\n")
    r.append(tabela(["Alternativa", "Investimento", "Custos anuais", "CAUE"], [
        [leg["defensor"]["nome"], brl(leg["defensor"].get("investimento", 0)), ", ".join(brl(c) for c in leg["defensor"]["custos_anuais"]), brl(sub["caue_defensor"])],
        [leg["desafiante"]["nome"], brl(leg["desafiante"].get("investimento", 0)), ", ".join(brl(c) for c in leg["desafiante"]["custos_anuais"]), brl(sub["caue_desafiante"])],
    ]))
    r.append(f"\nDecisão pelo menor Custo Anual Uniforme Equivalente: **{sub['decisao']}**, economia de {brl(sub['economia_anual'])} por ano equivalente. "
             "Isso confirma, em números, a decisão que tomamos na Sprint 1.\n")
    r.append(f"### 9.2 Princípio \"Bom o Suficiente\": {cfg['bom_o_suficiente']['tema']}\n")
    r.append(tabela(["Passo", "Benefício marginal", "Custo marginal", "Vale a pena?"],
                    [[f"{a['de']} para {a['para']}", brl(a["beneficio_marginal"]), brl(a["custo_marginal"]), "Sim" if a["vale_a_pena"] else "Não"] for a in bos["analise"]]))
    r.append(f"\nParamos em **{bos['escolhido']['nome']}**: a partir daí cada real investido em qualidade retorna menos de um real. "
             f"{cfg['bom_o_suficiente']['leitura']}\n")
    r.append("### 9.3 Priorização econômica do backlog (Valor x Esforço)\n")
    r.append(tabela(["#", "Item", "Valor (1-10)", "Esforço (pts)", "Valor/Esforço", "Quadrante"],
                    [[str(k + 1), b["item"], num(b["valor"], 0), num(b["esforco"], 0), num(b["razao"], 2), b["quadrante"]] for k, b in enumerate(back)]))
    r.append("")
    r.append("### 9.4 Decisão do cliente: on-premises, nuvem estática, Kubernetes ou SwarmBurst\n")
    r.append(tabela(["Alternativa do cliente", "Investimento inicial", "Custo mensal", f"VP dos custos ({meses} meses)"],
                    [[n, brl(ini), brl(mes), brl(v)] for n, ini, mes, v in vp_alt]))
    r.append(f"\nCom TMA mensal de {pct(i_cli_mes, 3)}, a alternativa de menor custo presente para o perfil de referência é **{melhor_alt[0]}**.\n")

    r.append("## 10. Proposta de modelo de negócio (Aula 7)\n")
    mn = cfg["modelo_negocio"]
    r.append(mn["descricao"] + "\n")
    r.append(tabela(["Plano", "Preço", "Para quem", "Limite"], [[x["plano"], x["preco"], x["publico"], x["limite"]] for x in mn["planos"]]))
    r.append("\n**Justificativa de ROI para o cliente:** " + mn["roi_cliente"].format(
        economia=brl(ref["economia_brl"]), licenca=brl(licenca_mes), retorno=num((ref["economia_brl"] - licenca_mes) / licenca_mes, 1)) + "\n")

    r.append("## 11. Riscos e hipóteses financeiras\n")
    r.append(tabela(["Risco / hipótese", "Impacto", "Mitigação"], [[x["risco"], x["impacto"], x["mitigacao"]] for x in cfg["riscos"]]))
    r.append("\n## 12. Reprodutibilidade\n")
    r.append("```bash\npython3 .agents/skills/engenharia-economica-software/scripts/valuation.py examples/swarmburst-input.json --out examples/tcc-valuation-report.md --json examples/tcc-valuation-result.json\n```\n")

    resultado = {"tma": i, "vpl": base["vpl"], "tir": base["tir"], "payback_simples": base["payback_simples"],
                 "payback_descontado": base["payback_descontado"], "il": base["il"], "capex": base["capex"],
                 "fluxos": base["fluxos"], "regime": base["regime"], "vpl_regime_alternativo": alt["vpl"],
                 "preco_equilibrio": pe, "evm": {k: v for k, v in ev.items() if k != "linhas"},
                 "ltv": ltv, "cac": cac, "ltv_cac": ltv / cac, "legado": sub, "bom_o_suficiente": bos["escolhido"]["nome"],
                 "sensibilidade": {n: {"vpl": c["vpl"], "tir": c["tir"]} for n, c in cen}}
    return "\n".join(r), resultado


def main() -> None:
    ap = argparse.ArgumentParser(description="Valoração econômica de projeto de software (VPL, TIR, Payback, GVA, CAC/LTV, tributos, priorização).")
    ap.add_argument("premissas", help="Arquivo JSON de premissas (modelo em assets/input-template.json)")
    ap.add_argument("--out", help="Caminho do relatório Markdown; sem ele imprime no terminal")
    ap.add_argument("--json", dest="json_out", help="Caminho opcional para salvar os resultados numéricos em JSON")
    a = ap.parse_args()
    cfg = json.loads(Path(a.premissas).read_text(encoding="utf-8"))
    cfg["projeto"].setdefault("arquivo_premissas", Path(a.premissas).name)
    md, res = relatorio(cfg)
    if a.out:
        Path(a.out).write_text(md, encoding="utf-8")
    else:
        print(md)
    if a.json_out:
        Path(a.json_out).write_text(json.dumps(res, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"vpl": round(res["vpl"], 2), "tir": res["tir"], "payback_descontado": res["payback_descontado"]}, ensure_ascii=False), file=sys.stderr)


if __name__ == "__main__":
    main()
