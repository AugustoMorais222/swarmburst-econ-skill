import json
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SCRIPTS = RAIZ / ".agents" / "skills" / "engenharia-economica-software" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import econ  # noqa: E402


class TestTVM(unittest.TestCase):
    def test_vp_vf_inversos(self):
        self.assertAlmostEqual(econ.vp(econ.vf(1000, 0.1, 3), 0.1, 3), 1000, places=8)

    def test_taxa_equivalente_mensal(self):
        self.assertAlmostEqual(econ.taxa_equivalente(0.12, 1, 1 / 12), 0.0094887929, places=8)

    def test_tma_composta(self):
        self.assertAlmostEqual(econ.tma_composta(0.1375, 0.06), 0.20575, places=10)


class TestViabilidade(unittest.TestCase):
    fluxos = [-1000, 500, 500, 500]

    def test_vpl(self):
        self.assertAlmostEqual(econ.vpl(self.fluxos, 0.10), 243.4259955, places=5)

    def test_tir_zera_vpl(self):
        t = econ.tir(self.fluxos)
        self.assertAlmostEqual(t, 0.2337519, places=6)
        self.assertAlmostEqual(econ.vpl(self.fluxos, t), 0.0, places=6)

    def test_tir_inexistente(self):
        self.assertIsNone(econ.tir([100, 100, 100]))

    def test_paybacks(self):
        self.assertAlmostEqual(econ.payback_simples(self.fluxos), 2.0)
        self.assertAlmostEqual(econ.payback_descontado(self.fluxos, 0.10), 2.352, places=3)
        self.assertIsNone(econ.payback_simples([-1000, 100, 100]))


class TestPreco(unittest.TestCase):
    def test_markup_divide_pelo_tributo(self):
        r = econ.preco_markup(223800, 0.20, 0.0865)
        self.assertAlmostEqual(r["preco"], 293990.15, places=2)
        self.assertAlmostEqual(r["tributos"], r["preco"] * 0.0865, places=6)


class TestTributos(unittest.TestCase):
    def test_presumido(self):
        r = econ.tributos_lucro_presumido(100000)
        self.assertAlmostEqual(r["total"], 16330.0, places=6)

    def test_real_compensa_prejuizo_com_trava(self):
        r = econ.tributos_lucro_real([0, 200000], [100000, 0], [0, 0], iss=0, pis=0, cofins=0, adicional_irpj=0)
        self.assertEqual(r[0]["irpj_csll"], 0)
        self.assertAlmostEqual(r[1]["base_ir"], 140000, places=6)

    def test_depreciacao(self):
        self.assertEqual(econ.depreciacao_linear(15000, 5, horizonte=6), [3000, 3000, 3000, 3000, 3000, 0])


class TestEVM(unittest.TestCase):
    def test_indicadores(self):
        r = econ.evm(100000, [{"nome": "S1", "pv_pct": 0.5, "ev_pct": 0.4, "ac": 50000},
                              {"nome": "S2", "pv_pct": 0.5, "ev_pct": None, "ac": None}])
        self.assertAlmostEqual(r["status"]["cpi"], 0.8)
        self.assertAlmostEqual(r["status"]["spi"], 0.8)
        self.assertAlmostEqual(r["eac"], 125000)
        self.assertAlmostEqual(r["tcpi"], 1.2)


class TestEstrategia(unittest.TestCase):
    def test_caue_sem_investimento_igual_custo(self):
        self.assertAlmostEqual(econ.caue(0, [100] * 5, 0.1), 100, places=6)

    def test_bom_o_suficiente_para_no_primeiro_passo_que_nao_paga(self):
        r = econ.bom_o_suficiente([{"nome": "A", "custo": 0, "beneficio": 0},
                                   {"nome": "B", "custo": 10, "beneficio": 30},
                                   {"nome": "C", "custo": 30, "beneficio": 35}])
        self.assertEqual(r["escolhido"]["nome"], "B")

    def test_priorizacao_ordena_por_razao(self):
        r = econ.priorizar_backlog([{"item": "x", "valor": 2, "esforco": 20}, {"item": "y", "valor": 8, "esforco": 3}])
        self.assertEqual(r[0]["item"], "y")
        self.assertEqual(r[0]["quadrante"], "Quick win")
        self.assertEqual(r[1]["quadrante"], "Evitar")


class TestValuationSwarmBurst(unittest.TestCase):
    def test_relatorio_tcc_reprodutivel(self):
        saida = subprocess.run([sys.executable, str(SCRIPTS / "valuation.py"), str(RAIZ / "examples" / "swarmburst-input.json")],
                               capture_output=True, text=True, check=True)
        self.assertIn("Sumário executivo", saida.stdout)
        res = json.loads(saida.stderr.strip().splitlines()[-1])
        self.assertGreater(res["vpl"], 0)


if __name__ == "__main__":
    unittest.main()
