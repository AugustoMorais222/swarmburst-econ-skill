"""Biblioteca determinística de Engenharia Econômica aplicada a projetos de software (Aulas 1 a 12)."""

from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Iterable, Sequence


def vp(valor_futuro: float, taxa: float, n: float) -> float:
    """Valor presente: VP = VF / (1 + i)^n."""
    return valor_futuro / (1 + taxa) ** n


def vf(valor_presente: float, taxa: float, n: float) -> float:
    """Valor futuro: VF = VP * (1 + i)^n."""
    return valor_presente * (1 + taxa) ** n


def taxa_equivalente(taxa: float, periodos_origem: float, periodos_destino: float) -> float:
    """Converte taxa entre períodos: (1 + i)^(destino/origem) - 1. Ex.: anual para mensal = (1+ia)^(1/12) - 1."""
    return (1 + taxa) ** (periodos_destino / periodos_origem) - 1


def tma_composta(taxa_livre_risco: float, premio_risco: float) -> float:
    """TMA = (1 + taxa livre de risco) * (1 + prêmio de risco) - 1."""
    return (1 + taxa_livre_risco) * (1 + premio_risco) - 1


def pmt(valor_presente: float, taxa: float, n: int) -> float:
    """Série uniforme equivalente (fator de recuperação de capital): P * i / (1 - (1+i)^-n)."""
    if taxa == 0:
        return valor_presente / n
    return valor_presente * taxa / (1 - (1 + taxa) ** -n)


def vpl(fluxos: Sequence[float], taxa: float) -> float:
    """VPL = soma de FC_t / (1 + TMA)^t, com t = 0 no investimento inicial."""
    return sum(fc / (1 + taxa) ** t for t, fc in enumerate(fluxos))


def tir(fluxos: Sequence[float], minimo: float = -0.99, maximo: float = 10.0, tolerancia: float = 1e-10) -> float | None:
    """TIR por bisseção: taxa que zera o VPL. Retorna None se não houver troca de sinal no intervalo."""
    f_min, f_max = vpl(fluxos, minimo), vpl(fluxos, maximo)
    if f_min * f_max > 0:
        return None
    for _ in range(500):
        meio = (minimo + maximo) / 2
        f_meio = vpl(fluxos, meio)
        if abs(f_meio) < tolerancia:
            return meio
        if f_min * f_meio < 0:
            maximo, f_max = meio, f_meio
        else:
            minimo, f_min = meio, f_meio
    return (minimo + maximo) / 2


def _payback(fluxos: Sequence[float]) -> float | None:
    acumulado = 0.0
    for t, fc in enumerate(fluxos):
        anterior = acumulado
        acumulado += fc
        if t > 0 and anterior < 0 <= acumulado:
            return (t - 1) + (-anterior / fc)
    return None


def payback_simples(fluxos: Sequence[float]) -> float | None:
    """Payback simples com interpolação linear dentro do período de recuperação."""
    return _payback(fluxos)


def payback_descontado(fluxos: Sequence[float], taxa: float) -> float | None:
    """Payback descontado: mesmo cálculo sobre os fluxos trazidos a valor presente pela TMA."""
    return _payback([fc / (1 + taxa) ** t for t, fc in enumerate(fluxos)])


def indice_lucratividade(fluxos: Sequence[float], taxa: float) -> float:
    """IL = VP das entradas futuras / |investimento inicial|."""
    return sum(fc / (1 + taxa) ** t for t, fc in enumerate(fluxos) if t > 0) / abs(fluxos[0])


def acumulado(fluxos: Iterable[float]) -> list[float]:
    """Saldo acumulado período a período."""
    saida, soma = [], 0.0
    for fc in fluxos:
        soma += fc
        saida.append(soma)
    return saida


def preco_markup(custo_total: float, margem_sobre_custo: float, aliquota_sobre_preco: float) -> dict:
    """Preço = Custo * (1 + margem) / (1 - alíquota). O tributo incide sobre o preço, por isso divide."""
    base = custo_total * (1 + margem_sobre_custo)
    preco = base / (1 - aliquota_sobre_preco)
    return {
        "custo_total": custo_total,
        "lucro": custo_total * margem_sobre_custo,
        "base_antes_tributos": base,
        "tributos": preco - base,
        "preco": preco,
        "markup_multiplicador": preco / custo_total,
    }


def depreciacao_linear(valor: float, vida_util_anos: int, residual: float = 0.0, horizonte: int | None = None) -> list[float]:
    """Quota anual linear = (valor - residual) / vida útil, limitada ao horizonte."""
    horizonte = horizonte or vida_util_anos
    quota = (valor - residual) / vida_util_anos
    return [quota if ano < vida_util_anos else 0.0 for ano in range(horizonte)]


def tributos_lucro_presumido(receita: float, iss: float = 0.05, pis: float = 0.0065, cofins: float = 0.03,
                             presuncao: float = 0.32, irpj: float = 0.15, adicional_irpj: float = 0.10,
                             limite_adicional_anual: float = 240000.0, csll: float = 0.09) -> dict:
    """Lucro Presumido (serviços): ISS + PIS/COFINS cumulativos sobre a receita; IRPJ e CSLL sobre 32% da receita."""
    deducoes = receita * (iss + pis + cofins)
    base = receita * presuncao
    ir = base * irpj + max(0.0, base - limite_adicional_anual) * adicional_irpj
    cs = base * csll
    return {"deducoes": deducoes, "irpj_csll": ir + cs, "total": deducoes + ir + cs}


def tributos_lucro_real(receitas: Sequence[float], custos_dedutiveis: Sequence[float], depreciacoes: Sequence[float],
                        iss: float = 0.05, pis: float = 0.0165, cofins: float = 0.076, irpj: float = 0.15,
                        adicional_irpj: float = 0.10, limite_adicional_anual: float = 240000.0, csll: float = 0.09,
                        trava_compensacao: float = 0.30) -> list[dict]:
    """Lucro Real: PIS/COFINS não cumulativos (sem créditos, conservador), IRPJ/CSLL sobre o LAIR após depreciação,
    com compensação de prejuízo fiscal limitada a 30% do lucro do período."""
    prejuizo, saida = 0.0, []
    for receita, custo, dep in zip(receitas, custos_dedutiveis, depreciacoes):
        deducoes = receita * (iss + pis + cofins)
        lair = receita - deducoes - custo - dep
        if lair <= 0:
            prejuizo += -lair
            base = 0.0
        else:
            compensado = min(prejuizo, lair * trava_compensacao)
            prejuizo -= compensado
            base = lair - compensado
        ir = base * irpj + max(0.0, base - limite_adicional_anual) * adicional_irpj
        cs = base * csll
        saida.append({"deducoes": deducoes, "lair": lair, "base_ir": base, "irpj_csll": ir + cs,
                      "total": deducoes + ir + cs, "prejuizo_a_compensar": prejuizo})
    return saida


def ltv(arpa_anual: float, margem_bruta: float, churn_anual: float) -> float:
    """LTV = ARPA * margem bruta / churn (vida média do cliente = 1 / churn)."""
    return arpa_anual * margem_bruta / churn_anual


def payback_cac_meses(cac: float, arpa_anual: float, margem_bruta: float) -> float:
    """Meses para recuperar o CAC com a margem bruta mensal do cliente."""
    return cac / (arpa_anual / 12 * margem_bruta)


def evm(bac: float, sprints: Sequence[dict]) -> dict:
    """Gerenciamento de Valor Agregado por sprint. Cada sprint: pv_pct, ev_pct (fração do BAC) e ac (R$).
    CPI = EV/AC, SPI = EV/PV, EAC = BAC/CPI, EAC_cpi_spi = AC + (BAC-EV)/(CPI*SPI), TCPI = (BAC-EV)/(BAC-AC)."""
    linhas, pv_acum, ev_acum, ac_acum = [], 0.0, 0.0, 0.0
    for s in sprints:
        pv_acum += s["pv_pct"] * bac
        if s.get("ac") is None:
            linhas.append({"sprint": s["nome"], "pv": pv_acum, "ev": None, "ac": None})
            continue
        ev_acum += s["ev_pct"] * bac
        ac_acum += s["ac"]
        cpi, spi = ev_acum / ac_acum, ev_acum / pv_acum
        linhas.append({"sprint": s["nome"], "pv": pv_acum, "ev": ev_acum, "ac": ac_acum,
                       "cv": ev_acum - ac_acum, "sv": ev_acum - pv_acum, "cpi": cpi, "spi": spi})
    atual = [l for l in linhas if l["ev"] is not None][-1]
    cpi, spi = atual["cpi"], atual["spi"]
    eac = bac / cpi
    return {
        "bac": bac, "linhas": linhas, "status": atual, "eac": eac,
        "eac_cpi_spi": atual["ac"] + (bac - atual["ev"]) / (cpi * spi),
        "etc": eac - atual["ac"], "vac": bac - eac,
        "tcpi": (bac - atual["ev"]) / (bac - atual["ac"]) if bac != atual["ac"] else math.inf,
        "percentual_concluido": atual["ev"] / bac,
    }


def priorizar_backlog(itens: Sequence[dict], limiar_valor: float = 5.0, limiar_esforco: float = 8.0) -> list[dict]:
    """Priorização Valor x Esforço: razão valor/esforço e quadrante (Quick win, Projeto estratégico, Preenchimento, Evitar)."""
    saida = []
    for item in itens:
        alto_valor = item["valor"] >= limiar_valor
        alto_esforco = item["esforco"] > limiar_esforco
        quadrante = {(True, False): "Quick win", (True, True): "Projeto estratégico",
                     (False, False): "Preenchimento", (False, True): "Evitar"}[(alto_valor, alto_esforco)]
        saida.append({**item, "razao": item["valor"] / item["esforco"], "quadrante": quadrante})
    return sorted(saida, key=lambda x: x["razao"], reverse=True)


def bom_o_suficiente(niveis: Sequence[dict]) -> dict:
    """Análise marginal: avança de nível enquanto o benefício marginal supera o custo marginal."""
    escolhido, analise = niveis[0], []
    for anterior, atual in zip(niveis, niveis[1:]):
        bm = atual["beneficio"] - anterior["beneficio"]
        cm = atual["custo"] - anterior["custo"]
        vale = bm > cm
        analise.append({"de": anterior["nome"], "para": atual["nome"], "beneficio_marginal": bm,
                        "custo_marginal": cm, "vale_a_pena": vale})
        if not vale:
            break
        escolhido = atual
    return {"escolhido": escolhido, "analise": analise}


def caue(investimento: float, custos_anuais: Sequence[float], taxa: float, residual: float = 0.0) -> float:
    """Custo Anual Uniforme Equivalente: VP de todos os custos convertido em série uniforme."""
    n = len(custos_anuais)
    vp_custos = investimento + sum(c / (1 + taxa) ** (t + 1) for t, c in enumerate(custos_anuais)) - residual / (1 + taxa) ** n
    return pmt(vp_custos, taxa, n)


def substituicao(defensor: dict, desafiante: dict, taxa: float) -> dict:
    """Análise de substituição/aposentadoria (legado x refatoração) pelo menor CAUE."""
    c_def = caue(defensor.get("investimento", 0.0), defensor["custos_anuais"], taxa, defensor.get("residual", 0.0))
    c_des = caue(desafiante.get("investimento", 0.0), desafiante["custos_anuais"], taxa, desafiante.get("residual", 0.0))
    return {"caue_defensor": c_def, "caue_desafiante": c_des,
            "decisao": desafiante["nome"] if c_des < c_def else defensor["nome"], "economia_anual": abs(c_def - c_des)}


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Cálculos pontuais de Engenharia Econômica (saída em JSON).")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("vpl", help="VPL, TIR, paybacks e IL de uma série de fluxos")
    p.add_argument("--fluxos", required=True, help="Lista JSON, ex.: [-1000,400,500,600]")
    p.add_argument("--taxa", type=float, required=True, help="TMA por período, ex.: 0.2058")
    p = sub.add_parser("preco", help="Preço por markup com tributo sobre o preço")
    p.add_argument("--custo", type=float, required=True)
    p.add_argument("--margem", type=float, required=True)
    p.add_argument("--aliquota", type=float, required=True)
    p = sub.add_parser("equivalencia", help="VP/VF e taxa equivalente")
    p.add_argument("--valor", type=float, required=True)
    p.add_argument("--taxa", type=float, required=True)
    p.add_argument("--n", type=float, required=True)
    p = sub.add_parser("evm", help="GVA a partir de um JSON {bac, sprints:[{nome,pv_pct,ev_pct,ac}]}")
    p.add_argument("--json", required=True)
    args = parser.parse_args()
    if args.cmd == "vpl":
        f = json.loads(args.fluxos)
        out = {"vpl": vpl(f, args.taxa), "tir": tir(f), "payback_simples": payback_simples(f),
               "payback_descontado": payback_descontado(f, args.taxa), "il": indice_lucratividade(f, args.taxa)}
    elif args.cmd == "preco":
        out = preco_markup(args.custo, args.margem, args.aliquota)
    elif args.cmd == "equivalencia":
        out = {"vp_de_vf": vp(args.valor, args.taxa, args.n), "vf_de_vp": vf(args.valor, args.taxa, args.n),
               "taxa_mensal_equivalente": taxa_equivalente(args.taxa, 1, 1 / 12)}
    else:
        d = json.loads(args.json)
        out = evm(d["bac"], d["sprints"])
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2, default=str)
    print()


if __name__ == "__main__":
    _cli()
