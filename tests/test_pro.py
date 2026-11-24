"""rotzx Pro (D77): indicadores com FIXTURES inventadas (só a forma importa) e a âncora mensal × anual quando há cache real."""
import json

import pytest

from rotzx.pro import indicadores as ind

# FIXTURE DE TESTE: valores inventados
L = [{"mes": 1, "chave": "A", "nome": "País A", "fob": 100.0, "kg": 50.0}, {"mes": 2, "chave": "A", "nome": "País A", "fob": 60.0, "kg": 20.0},
     {"mes": 1, "chave": "B", "nome": "País B", "fob": 40.0, "kg": 40.0}, {"mes": 3, "chave": "C", "nome": "País C", "fob": 0.0, "kg": 0.0}]


def test_agregar_ranking_e_denominador():
    ag = ind.agregar(L)
    t = ind.total(ag)
    assert t == {"fob": 200.0, "kg": 110.0, "n": 2}                 # C sem valor não conta
    r = ind.ranking(ag, t["fob"])
    assert [x["chave"] for x in r] == ["A", "B"] and r[0]["parte"] == 0.8 and r[0]["preco_t"] == 160 / 70 * 1000
    assert ind.agregar(L, meses=[1])["A"]["fob"] == 100.0


def test_variacao_pp_e_ausencia_nunca_vira_zero():
    assert ind.variacao(100, 110) == pytest.approx(0.10) and ind.variacao(None, 5) is None and ind.variacao(0, 5) is None
    assert ind.pp(0.2, 0.25) == pytest.approx(0.05) and ind.pp(None, 0.3) is None
    assert ind.preco_t(10, 0) is None


def test_preco_volume_soma_exata():
    v, p = ind.preco_volume(100, 50, 180, 60)
    assert v + p == pytest.approx(80) and v == pytest.approx(20) and p == pytest.approx(60)
    assert ind.preco_volume(100, 0, 50, 10) is None


def test_dependencia_e_mensal():
    ag = ind.agregar(L)
    d = ind.dependencia(ind.ranking(ag, 200))
    assert d == {"maior": 0.8, "tres": 1.0, "n": 2}
    m = ind.mensal({2025: L})
    assert m[0] == (2025, 1, 140.0, 90.0) and (2025, 4) not in [(a, b) for a, b, *_ in m]   # mês sem linha não vira zero


def test_ancora_12_meses_igual_ao_anual_do_atlas():
    """Com o cache real da coleta (fora do git), a soma de 2025 por fornecedor bate com o total anual publicado no atlas."""
    from rotzx.pro import coleta
    from rotzx.mundo import codigos, detalhe_coleta, historia
    sh4 = ["3101", "3102", "3103", "3104", "3105"]
    try:
        ls = coleta.linhas(2025, "importacao", "pais", sh4, log=lambda *_: None) if any(coleta.CACHE.glob("2025-importacao-pais-*.json")) else None
    except Exception:
        ls = None
    if not ls:
        pytest.skip("sem cache da coleta do Pro (data/fontes/pro)")
    ponte = detalhe_coleta._ponte(codigos.carregar())
    por_iso = {}
    for x in ls:
        iso = ponte.get(x["chave"])
        if iso:
            por_iso[iso] = por_iso.get(iso, 0) + x["fob"]
    P = json.loads((historia.SAIDA / "produtos.json").read_text(encoding="utf-8"))
    anual = P["itens"]["g-fertilizantes"]["p"]["2025"]["i"]
    assert round(sum(por_iso.values())) == anual["t"]
    for iso, v in anual["top"]:
        assert round(por_iso[iso]) == v, iso


def test_pagina_pro_gerada(tmp_path):
    """A página /pro/ e a de privacidade saem do gerador com o botão de contato, o PDF e o aviso de não recomendação."""
    from rotzx.mundo import paginas
    from rotzx.pro import pagina
    urls = pagina.gerar(tmp_path, paginas._pagina, "24/11/2026")
    assert urls == ["pro/", "pro/privacidade/"]
    pro = (tmp_path / "pro" / "index.html").read_text(encoding="utf-8")
    priv = (tmp_path / "pro" / "privacidade" / "index.html").read_text(encoding="utf-8")
    assert (pagina.FORMULARIO or pagina.LINKEDIN) in pro
    assert "estudo-fertilizantes.pdf" in pro and "não é recomendação" in pro
    assert "privacidade/" in pro and "LGPD" in priv


def test_pagina_pro_tema_planos_e_rodape(tmp_path):
    """D78: mesmo tema do atlas (sem flash, com botão), 3 planos, card do PDF em nova aba, público amplo e rodapé próprio."""
    from rotzx.mundo import paginas
    from rotzx.pro import pagina
    pagina.gerar(tmp_path, paginas._pagina, "24/11/2026")
    pro = (tmp_path / "pro" / "index.html").read_text(encoding="utf-8")
    priv = (tmp_path / "pro" / "privacidade" / "index.html").read_text(encoding="utf-8")
    for h in (pro, priv):
        assert h.index('localStorage.getItem("rotzx-tema")') < h.index("<style>")   # tema antes do CSS: sem flash
        assert 'id="tema"' in h and ':root[data-theme="dark"]' in h
        assert "retrato público do atlas gratuito" in h and "sem atualização em tempo real" not in h
    for nome in ("Diagnóstico", "Acompanhamento", "Sob medida", "Ponto de partida", "Incorporar"):
        assert nome in pro
    assert 'href="estudo-fertilizantes.pdf" target="_blank"' in pro
    assert "pessoa física" in pro and "MEIs" in pro and "opcionais" in pro
    assert "opcionais" in priv and 'href="../"' in priv


def test_pagina_pro_acabamento_d79(tmp_path):
    """D79: copy mantida, Pro ativo no cabeçalho, prévia real do PDF sem CLS, movimento com respeito a prefers-reduced-motion."""
    from rotzx.mundo import paginas
    from rotzx.pro import amostra, pagina
    pagina.gerar(tmp_path, paginas._pagina, "24/11/2026")
    pro = (tmp_path / "pro" / "index.html").read_text(encoding="utf-8")
    priv = (tmp_path / "pro" / "privacidade" / "index.html").read_text(encoding="utf-8")
    for frase in ("Análise sob demanda do comércio exterior", "Pedido individual? Empresa e cargo são opcionais", "Ponto de partida",
                  "Diferente do <b>Incorporar</b>", "Perguntas pontuais cabem em escopos enxutos", "Tem uma pergunta sobre comércio exterior?"):
        assert frase in pro, frase
    assert '<a href="../pro/" aria-current="page">rotzx Pro</a>' in pro and 'aria-current="page">rotzx Pro</a>' in priv
    for n in amostra.MINIATURAS:
        assert (amostra.DESTINO.parent / f"estudo-p{n}.webp").exists()
        assert f'src="estudo-p{n}.webp" width="480" height="680"' in pro
    assert "IntersectionObserver" in pro and "prefers-reduced-motion:reduce" in pro and "prefers-reduced-motion: reduce" in pro
    import re
    assert pagina.PAGINAS_AMOSTRA == len(re.findall(rb"/Type\s*/Page[^s]", amostra.DESTINO.read_bytes()))   # "9 páginas" é o real


# ---------- D80: estudo-amostra v2 ----------
def test_decomposicao_volume_preco_mix_fecha():
    """Fixture inventada: volume + preço + mix + sem peso = variação, com item novo, item que sai e valor sem peso."""
    base = {"A": (100.0, 100.0), "B": (400.0, 100.0), "D": (30.0, 10.0)}
    atual = {"A": (132.0, 120.0), "B": (480.0, 120.0), "C": (50.0, 0.0), "E": (90.0, 30.0)}
    d = ind.decompor(base, atual)
    assert d["volume"] + d["preco"] + d["mix"] + d["sem_peso"] == pytest.approx(d["variacao"])
    assert d["sem_peso"] == pytest.approx(50.0)
    so_mix = ind.decompor({"A": (100.0, 100.0), "B": (400.0, 100.0)}, {"A": (100.0, 100.0), "B": (800.0, 200.0)})
    assert so_mix["preco"] == pytest.approx(0) and so_mix["mix"] == pytest.approx(150.0)
    assert ind.hhi([0.5, 0.5]) == pytest.approx(5000) and ind.hhi([1.0]) == pytest.approx(10000)
    assert ind.acumulado({1: 1.0, 2: 2.0, 4: 5.0}) == {1: 1.0, 2: 3.0}        # lacuna interrompe: sem registro, nunca zero


def test_nomes_acentuados():
    from rotzx.pro import nomes as N
    assert N.lugar("0917800 - PORTO DE PARANAGUA") == "Porto de Paranaguá"
    assert N.lugar("0317903 - IRF SAO LUIS") == "IRF São Luís"
    assert N.lugar("0517800 - ALF - SALVADOR") == "Alfândega de Salvador"
    assert [N.lugar(v) for v in ("MARITIMA", "AEREA", "RODOVIARIA", "FERROVIARIA")] == ["Marítima", "Aérea", "Rodoviária", "Ferroviária"]
    assert N.ncm("31042090", "Outros cloretos de potássio") == "Cloreto de potássio (KCl)"
    assert N.ncm("99999999", "Texto oficial longo, inteiro") == "Texto oficial longo, inteiro"   # sem nome curto: oficial inteiro


def _estudo():
    from rotzx.pro import amostra, coleta
    if not any(coleta.CACHE.glob("2026-importacao-pais_ncm-*.json")):
        pytest.skip("sem cache das consultas cruzadas do Pro (data/fontes/pro)")
    return amostra, amostra.calcular(log=lambda *a: None)


def test_estudo_totais_cruzados_batem():
    """Os totais de cada seção batem entre si: resumo, decomposição, fornecedores, portos, estados, vias e calendário."""
    amostra, d = _estudo()
    tb = d["per"]["ytd26"]["total"]
    ult = d["ultimo_mes"]
    assert d["dec_total"]["v1"] == pytest.approx(tb["fob"]) and d["dec_total"]["v0"] == pytest.approx(d["per"]["ytd25"]["total"]["fob"])
    for chave in ("urf", "uf"):
        assert sum(x["fob"] for x in d[chave]) == pytest.approx(tb["fob"])
    assert sum(x["fob"] for x in d["via"]["ytd26"]) == pytest.approx(tb["fob"])
    assert sum(x["fob"] for x in d["per"]["ytd26"]["rank"]) == pytest.approx(tb["fob"])
    assert d["cal_acum"][2026][ult] == pytest.approx(tb["kg"])
    assert sum(x["parte"] for x in d["per"]["ytd26"]["rank"]) == pytest.approx(1.0)
    dec = d["dec_total"]
    assert dec["volume"] + dec["preco"] + dec["mix"] + dec["sem_peso"] == pytest.approx(dec["variacao"], abs=1)
    assert d["dp"]["preco"] + d["dp"]["mix"] == pytest.approx(d["dp"]["total"])
    for f in d["dec_forn"]:
        assert f["volume"] + f["preco"] + f["mix"] + f["sem_peso"] == pytest.approx(f["variacao"], abs=1)


def test_estudo_html_rigor():
    """Sem descrição cortada; a concentração citada no resumo está na tabela; aviso e fontes presentes."""
    amostra, d = _estudo()
    from rotzx.pro import relatorio as R
    h = amostra.html(d)
    assert "…" not in h
    A, B = d["per"]["ytd25"], d["per"]["ytd26"]
    tabela = h[h.index("No grupo inteiro, por período"):]
    for v in (A["tres"], B["tres"]):
        assert R.pct(v) in tabela
    assert "não é recomendação de investimento ou de negócio" in h and "Leitura do analista" in h and "CC BY 4.0" in h
    assert "Contexto, não causa comprovada" in h
    for c in amostra.CONTEXTO:
        assert c["fontes"] and all(dt and u.startswith("https://") for _, dt, u in c["fontes"])


def test_planilha_do_estudo():
    from rotzx.pro import amostra
    import openpyxl
    if not amostra.PLANILHA.exists():
        pytest.skip("planilha ainda não gerada")
    abas = openpyxl.load_workbook(amostra.PLANILHA, read_only=True).sheetnames
    assert abas[0] == "1 Totais" and "2 Volume preço mix" in abas and "Fontes" in abas and len(abas) >= 10
