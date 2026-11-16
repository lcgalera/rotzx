"""Páginas estáticas do atlas (D66): mesmos números dos dados, com fonte, ano e denominador."""
import json

from rotzx.mundo import paginas

GLOBO = paginas.Path(__file__).resolve().parents[1] / "prototipos" / "globo"


def test_formatos_iguais_aos_da_pagina():
    assert paginas.usd(None) == "sem registro"          # ausente nunca vira zero
    assert paginas.usd(99940244710) == "US$ 99,9 bi" and paginas.usd(170855803124) == "US$ 171 bi"
    assert paginas.usd(-7459694768) == "−US$ 7,5 bi" and paginas.usd(350e6) == "US$ 350 mi"
    assert paginas.pct(0.2869549957) == "28,7%" and paginas.pct(0.0001) == "menos de 0,1%"
    assert paginas.slug("Coreia do Sul") == "coreia-do-sul" and paginas.slug("São Tomé e Príncipe") == "sao-tome-e-principe"


def test_gera_paginas_com_os_numeros_dos_dados(tmp_path):
    r = paginas.gerar(tmp_path, GLOBO / "dados")
    H = json.loads((GLOBO / "dados" / "historia.json").read_text(encoding="utf-8"))
    C = H["comercio"]
    fim = C["fim"]
    china = (tmp_path / "pais" / "china" / "index.html").read_text(encoding="utf-8")
    ex = C["paises"]["156"]["e"][-1]
    assert paginas.usd(ex) in china and paginas.pct(ex / C["brasil"]["e"][-1]) in china
    assert f"do total exportado pelo Brasil em {fim}" in china          # denominador dito
    assert 'href="../../#pais=CHN"' in china and "Comex Stat (MDIC)" in china
    assert 'rel="canonical" href="https://lcgalera.github.io/rotzx/pais/china/"' in china
    assert not (tmp_path / "pais" / "brasil").exists()                   # o Brasil não é parceiro de si mesmo
    soja = (tmp_path / "produto" / "1201" / "index.html").read_text(encoding="utf-8")
    P = json.loads((GLOBO / "dados" / "produtos.json").read_text(encoding="utf-8"))
    x = P["itens"]["1201"]["p"][str(fim)]["e"]
    assert paginas.usd(x["t"]) in soja and paginas.pct(x["top"][0][1] / x["t"]) in soja and "sem valor individual" in soja
    mapa = (tmp_path / "sitemap.xml").read_text(encoding="utf-8")
    assert mapa.count("<loc>") == r["urls"] and "/pais/china/</loc>" in mapa
    assert "Sitemap:" in (tmp_path / "robots.txt").read_text(encoding="utf-8")
    # endereços únicos: nenhum país divide slug com outro
    assert len(list((tmp_path / "pais").iterdir())) == r["paises"] + 1
