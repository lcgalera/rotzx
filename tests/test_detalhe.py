"""Validador do detalhamento do atlas (rotzx.detalhe.v1, docs/SCHEMA.md, D61).

As fixtures usam o formato real com VALORES INVENTADOS, marcados como tal em "consulta".
"""
import json

import pytest

from rotzx.mundo import detalhe

INVENTADO = "FIXTURE DE TESTE: valores inventados"


def _prod():
    return {"schema": "rotzx.detalhe.v1", "codigo": "3105", "nome": "teste", "fonte": "Comex Stat (MDIC)", "consulta": INVENTADO,
            "gerado_em": "2026-11-13T00:00:00Z", "unidade": "US$ FOB correntes",
            "parceiros": {"i": {"2024": {"t": 100.0, "n": 5, "top": [["643", 40.0], ["156", 30.0]]},
                                "2025": {"t": 120.0, "n": 4, "top": [["156", 50.0], ["643", 45.0]]}}},
            "uf": {"i": {"2025": {"t": 120.0, "n": 2, "top": [["MT", 70.0], ["PR", 50.0]]}}},
            "via": {"i": {"2025": {"t": 120.0, "n": 1, "top": [["MARITIMA", 120.0]]}}},
            "ncm": {"i": {"2025": {"t": 120.0, "n": 2, "top": [["31052000", "item de teste", 80.0], ["31059090", "outro item", 40.0]]}}}}


def _pais():
    return {"schema": "rotzx.detalhe.v1", "iso3": "CHN", "iso_num": "156", "fonte": "Comex Stat (MDIC)", "consulta": INVENTADO,
            "gerado_em": "2026-11-13T00:00:00Z", "unidade": "US$ FOB correntes",
            "produtos": {"e": {"2020": {"t": 10.0, "n": 3, "top": [["1201", 6.0], ["2601", 3.0]]}}}}


def _pasta(tmp_path, prod=None, pais=None, indice=None):
    (tmp_path / "prod").mkdir(); (tmp_path / "pais").mkdir()
    (tmp_path / "prod" / "3105.json").write_text(json.dumps(prod or _prod()))
    (tmp_path / "pais" / "CHN.json").write_text(json.dumps(pais or _pais()))
    ind = indice or {"schema": "rotzx.detalhe.v1", "fonte": "Comex Stat (MDIC)", "gerado_em": "2026-11-13T00:00:00Z",
                     "prod": {"3105": {"anos_parceiros": [2024, 2025]}}, "pais": {"CHN": {"anos_produtos": [2020]}}}
    (tmp_path / "indice.json").write_text(json.dumps(ind))
    return tmp_path


def test_pasta_no_formato_passa(tmp_path):
    assert detalhe.validar_pasta(_pasta(tmp_path)) == []


@pytest.mark.parametrize("mexer,trecho", [
    (lambda o: o["parceiros"]["i"]["2025"].update(top=[["643", 45.0], ["156", 50.0]]), "fora de ordem"),
    (lambda o: o["parceiros"]["i"]["2025"].update(t=50.0), "maior que t"),
    (lambda o: o["parceiros"]["i"]["2025"]["top"].append(["156", 0]), "número > 0"),
    (lambda o: o["parceiros"]["i"]["2025"]["top"].__setitem__(0, ["999", 50.0]), "não está em catalog"),
    (lambda o: o["uf"]["i"]["2025"]["top"].__setitem__(0, ["XX", 70.0]), "UF 'XX'"),
    (lambda o: o["ncm"]["i"]["2025"]["top"].__setitem__(0, ["3105", "curto", 80.0]), "8 dígitos"),
    (lambda o: o["parceiros"]["i"].update({"1990": {"t": 1.0, "n": 1, "top": [["156", 1.0]]}}), "fora de"),
    (lambda o: o.pop("fonte"), "falta 'fonte'"),
])
def test_problemas_sao_apontados(tmp_path, mexer, trecho):
    obj = _prod(); mexer(obj)
    probs = detalhe.validar_pasta(_pasta(tmp_path, prod=obj))
    assert any(trecho in p for p in probs), probs


def test_indice_e_arquivos_precisam_conferir(tmp_path):
    ind = {"schema": "rotzx.detalhe.v1", "fonte": "Comex Stat (MDIC)", "gerado_em": "2026-11-13",
           "prod": {"3105": {"anos_parceiros": [2025]}, "3104": {"anos_parceiros": [2025]}}, "pais": {}}
    probs = detalhe.validar_pasta(_pasta(tmp_path, indice=ind))
    assert any("3104.json não encontrado" in p for p in probs)
    assert any("não confere com os anos" in p for p in probs)
    assert any("CHN.json existe mas não está no índice" in p for p in probs)


def test_detalhamento_publicado_esta_no_formato():
    """Se o projeto de dados já copiou arquivos para o site, eles precisam passar no validador."""
    if not (detalhe.PASTA / "indice.json").exists():
        pytest.skip("detalhamento ainda não publicado (prototipos/globo/dados/detalhe)")
    assert detalhe.validar_pasta() == []
