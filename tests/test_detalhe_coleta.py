"""Gerador do detalhamento (D68): sem rede, com pares inventados e marcados como tal; o resultado passa no validador."""
import json

from rotzx.mundo import detalhe, detalhe_coleta

# FIXTURE DE TESTE: valores inventados (só a forma importa)
PARES = {
    (2024, "e"): {"156": {"1201": 80.0, "2601": 20.0, "0901": 0.2}, "032": {"1201": 5.0}},
    (2025, "e"): {"156": {"1201": 90.0, "2601": 30.0}, "032": {"1201": 10.0}, "076": {"1201": 1.0}},
    (2025, "i"): {"156": {"8517": 40.0}},
}


def _dados(tmp_path):
    d = tmp_path / "dados"
    d.mkdir()
    (d / "historia.json").write_text(json.dumps({"comercio": {"fim": 2025}, "paises": {
        "156": {"iso3": "CHN"}, "032": {"iso3": "ARG"}, "076": {"iso3": "BRA"}}}))
    (d / "produtos.json").write_text(json.dumps({"itens": {"1201": {"nome": "Soja"}, "2601": {"nome": "Minério"}, "8517": {"nome": "Telefones"}}}))
    return d


def test_gera_no_formato_e_passa_no_validador(tmp_path):
    d = _dados(tmp_path)
    r = detalhe_coleta.gerar(d / "detalhe", d, ano_ini=2024, ano_fim=2025, cache=None,
                             pares=lambda ano, k, fluxo: PARES.get((ano, k), {}), log=lambda *_: None)
    assert r == {"prod": 3, "pais": 2, "anos": [2024, 2025]}
    assert detalhe.validar_pasta(d / "detalhe") == []
    soja = json.loads((d / "detalhe" / "prod" / "1201.json").read_text())
    assert soja["parceiros"]["e"]["2025"] == {"t": 101, "n": 3, "top": [["156", 90], ["032", 10], ["076", 1]]}   # mesma regra do retrato: o total inclui tudo
    assert "i" not in soja["parceiros"]                               # sem dado = sem bloco, nunca zero
    chn = json.loads((d / "detalhe" / "pais" / "CHN.json").read_text())
    assert chn["produtos"]["e"]["2024"] == {"t": 100, "n": 3, "top": [["1201", 80], ["2601", 20]]}  # 0,2 conta em n e em t, mas não aparece no topo
    ind = json.loads((d / "detalhe" / "indice.json").read_text())
    assert ind["prod"]["8517"]["anos_parceiros"] == [2025] and ind["pais"]["ARG"]["anos_produtos"] == [2024, 2025]
    assert not (d / "detalhe" / "pais" / "BRA.json").exists()
