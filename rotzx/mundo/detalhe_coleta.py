"""Gera o detalhamento do atlas (formato `rotzx.detalhe.v1`, docs/SCHEMA.md) a partir do Comex Stat (D68).

    .venv/bin/python -m rotzx detalhe-gerar            # 1997 até o último ano do retrato

Uma consulta por ano e fluxo (todos os pares país × SH4 do ano), com o intervalo de `comex.INTERVALO`. O resumo de cada
consulta fica em `data/fontes/mundo/detalhe/` (fora do git), então uma coleta interrompida continua de onde parou.

Camadas geradas:
- `prod/{codigo}.json` → `parceiros`: os 12 maiores parceiros de cada produto do explorador, em todos os anos;
- `pais/{iso3}.json`   → `produtos`: os 10 maiores produtos do comércio com cada país, em todos os anos.
UF, via, porto e NCM pedem outras consultas e ficam para depois; a página já sabe lê-las.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .. import config
from . import codigos, comex, detalhe, historia, produtos_nomes

CACHE = config.ROOT / "data" / "fontes" / "mundo" / "detalhe"
FLUXOS = (("exportacao", "e"), ("importacao", "i"))
CONSULTA = "api-comexstat.mdic.gov.br /general; detailDatabase=[noPaispt, noSh4pt]; uma consulta por ano e fluxo; {a}–{b}"


def _ponte(tabela: List[dict]) -> Dict[str, str]:
    """Nome do país no Comex Stat → iso_num (a mesma ponte do retrato histórico)."""
    cod_de = {x["text"]: x["id"] for x in codigos._json(codigos.COMEX_PAISES)["data"]["list"]}
    iso_de = {c: r["iso_num"] for r in tabela for c in r["comex"]}
    return {nome: iso_de[c] for nome, c in cod_de.items() if c in iso_de}


def pares_do_ano(ano: int, k: str, fluxo: str, ponte: Dict[str, str], cache: Optional[Path] = CACHE, log=print) -> Dict[str, Dict[str, float]]:
    """{iso_num: {sh4: US$ FOB}} de um ano e fluxo; lê do cache quando existe."""
    arq = cache / f"{ano}-{k}.json" if cache else None
    if arq and arq.exists():
        return json.loads(arq.read_text(encoding="utf-8"))
    log(f"  Comex Stat: {ano} {fluxo}")
    por_iso: Dict[str, Dict[str, float]] = {}
    for nome, itens in comex.produtos_todos(str(ano), fluxo).items():
        iso = ponte.get(nome)
        if not iso:
            continue                                   # operações sem país identificado ficam fora, como no retrato
        d = por_iso.setdefault(iso, {})
        for sh4, _nome, fob in itens:
            d[sh4] = d.get(sh4, 0) + fob
    if arq:
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(json.dumps(por_iso, separators=(",", ":")), encoding="utf-8")
    return por_iso


def _bloco(soma: Dict[str, float], top: int) -> Optional[dict]:
    """{t, n, top} só com valores que continuam positivos depois de arredondar; sem dado = sem bloco (nunca zero)."""
    vals = {c: round(v) for c, v in soma.items() if round(v) > 0}
    if not vals:
        return None
    maiores = sorted(vals.items(), key=lambda kv: -kv[1])[:top]
    return {"t": sum(vals.values()), "n": len(vals), "top": [[c, v] for c, v in maiores]}


def gerar(saida: Path = detalhe.PASTA, dados: Optional[Path] = None, ano_ini: int = historia.ANO_COMEX, ano_fim: Optional[int] = None,
          cache: Optional[Path] = CACHE, pares=None, log=print) -> dict:
    """Escreve índice, `prod/` e `pais/`. `pares` (função ano, k → {iso: {sh4: v}}) existe para os testes não irem à rede."""
    saida = Path(saida)
    dados = Path(dados or saida.parent)
    H = json.loads((dados / "historia.json").read_text(encoding="utf-8"))
    P = json.loads((dados / "produtos.json").read_text(encoding="utf-8"))
    ano_fim = ano_fim or H["comercio"]["fim"]
    itens = P["itens"]
    grupos = {gid: set(g["sh4"]) for gid, g in produtos_nomes.GRUPOS.items() if gid in itens}
    iso3 = {i: d["iso3"] for i, d in H["paises"].items()}
    if pares is None:
        ponte = _ponte(codigos.carregar())
        pares = lambda ano, k, fluxo: pares_do_ano(ano, k, fluxo, ponte, cache, log)
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    prod: Dict[str, dict] = {}
    pais: Dict[str, dict] = {}
    for ano in range(ano_ini, ano_fim + 1):
        for fluxo, k in FLUXOS:
            por_iso = pares(ano, k, fluxo)
            por_produto: Dict[str, Dict[str, float]] = {}
            for iso, d in por_iso.items():
                if iso not in iso3 or iso == "076":
                    continue
                b = _bloco(d, historia.TOP_PRODUTOS)
                if b:
                    pais.setdefault(iso, {}).setdefault(k, {})[str(ano)] = b
                for c, v in d.items():
                    alvos = ([c] if c in itens else []) + [g for g, cods in grupos.items() if c in cods]
                    for a in alvos:
                        por_produto.setdefault(a, {})[iso] = por_produto.setdefault(a, {}).get(iso, 0) + v
            for a, d in por_produto.items():
                b = _bloco(d, historia.TOP_PARCEIROS)
                if b:
                    prod.setdefault(a, {}).setdefault(k, {})[str(ano)] = b
    cab = {"schema": detalhe.SCHEMA, "fonte": "Comex Stat (MDIC)", "consulta": CONSULTA.format(a=ano_ini, b=ano_fim),
           "gerado_em": agora, "unidade": "US$ FOB correntes"}
    for sub in ("prod", "pais"):
        (saida / sub).mkdir(parents=True, exist_ok=True)
        for velho in (saida / sub).glob("*.json"):
            velho.unlink()
    indice = {"schema": detalhe.SCHEMA, "gerado_em": agora, "fonte": "Comex Stat (MDIC)", "licenca": "dados abertos (MDIC)", "prod": {}, "pais": {}}
    grava = lambda arq, obj: arq.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for c, camadas in sorted(prod.items()):
        grava(saida / "prod" / f"{c}.json", {**cab, "codigo": c, "nome": itens[c]["nome"], "parceiros": camadas})
        indice["prod"][c] = {"anos_parceiros": sorted({int(a) for d in camadas.values() for a in d}), "camadas": ["parceiros"]}
    for iso, camadas in sorted(pais.items()):
        grava(saida / "pais" / f"{iso3[iso]}.json", {**cab, "iso3": iso3[iso], "iso_num": iso, "produtos": camadas})
        indice["pais"][iso3[iso]] = {"anos_produtos": sorted({int(a) for d in camadas.values() for a in d}), "camadas": ["produtos"]}
    grava(saida / "indice.json", indice)
    log(f"detalhe: {len(prod)} produtos e {len(pais)} países em {saida}")
    return {"prod": len(prod), "pais": len(pais), "anos": [ano_ini, ano_fim]}
