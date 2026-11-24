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
