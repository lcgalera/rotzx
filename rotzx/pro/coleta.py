"""Coleta mensal detalhada no Comex Stat para um recorte de produtos (D77).

Uma consulta por ano e por nível de detalhe (país, UF, URF, via, NCM), com mês (`monthDetail`) e peso (`metricKG`) ligados e o
filtro por SH4. Reaproveita `comex._get` (espera entre chamadas, novas tentativas e resposta bruta guardada). O resumo de cada
consulta fica em data/fontes/pro/ (fora do git), então repetir um recorte não consulta a API de novo.
"""
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional

from .. import config
from ..mundo import comex

CACHE = config.DATA_DIR / "fontes" / "pro"
NIVEIS = {"pais": "noPaispt", "uf": "noUf", "urf": "noUrf", "via": "noVia", "ncm": "noNcmpt"}


def filtro(ano: int, fluxo: str, nivel: str, sh4: List[str], mes_ate: int = 12) -> dict:
    f = comex._filtro(str(ano), fluxo, NIVEIS[nivel])
    f.update(monthDetail=True, metricKG=True, monthEnd=f"{mes_ate:02d}")
    f["filterList"] = [{"id": "noSh4pt"}]
    f["filterArray"] = [{"item": list(sh4), "idInput": "noSh4pt"}]
    return f


def linhas(ano: int, fluxo: str, nivel: str, sh4: List[str], cache: Optional[Path] = CACHE, log=print) -> List[dict]:
    """[{mes, chave, nome, fob, kg}] para um ano e nível; `chave` é o código (NCM) ou o nome que a fonte usa."""
    assinatura = hashlib.sha256(json.dumps([ano, fluxo, nivel, sorted(sh4)]).encode()).hexdigest()[:12]
    arq = cache / f"{ano}-{fluxo}-{nivel}-{assinatura}.json" if cache else None
    if arq and arq.exists():
        return json.loads(arq.read_text(encoding="utf-8"))
    log(f"  Comex Stat: {ano} {fluxo} por {nivel}")
    campo = NIVEIS[nivel]
    out = []
    for x in comex._get(filtro(ano, fluxo, nivel, sh4)):
        chave = x.get("coNcm") or x.get(campo, "")
        out.append({"mes": int(x["coMes"]), "chave": chave, "nome": x.get(campo, "").replace("\xa0", " "),
                    "fob": float(x["vlFob"]), "kg": float(x.get("kgLiquido") or 0)})
    if arq:
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return out


def recorte(anos: List[int], fluxo: str, sh4: List[str], niveis=tuple(NIVEIS), cache: Optional[Path] = CACHE, log=print) -> Dict[str, Dict[int, List[dict]]]:
    """{nivel: {ano: linhas}} para todos os anos e níveis pedidos."""
    return {n: {a: linhas(a, fluxo, n, sh4, cache, log) for a in anos} for n in niveis}


# ---------- D80: consultas cruzadas (vários detalhes ao mesmo tempo) com frete, seguro e CIF ----------
CAMPOS = {"pais": "noPaispt", "ncm": "noNcmpt", "urf": "noUrf", "via": "noVia", "uf": "noUf"}
CRUZADOS = {"pais_ncm": ("pais", "ncm"), "urf_via": ("urf", "via"), "uf": ("uf",),
            # D81: com a NCM junto, para recortes que filtram NCMs dentro de uma posição SH4 (ex.: só o café solúvel na 2101)
            "urf_via_ncm": ("urf", "via", "ncm"), "uf_ncm": ("uf", "ncm")}


def filtro_cruzado(ano: int, fluxo: str, detalhes, sh4: List[str], mes_ate: int = 12, frete: bool = True) -> dict:
    f = comex._filtro(str(ano), fluxo, CAMPOS[detalhes[0]])
    f["detailDatabase"] = [{"id": CAMPOS[d], "text": ""} for d in detalhes]
    f.update(monthDetail=True, metricKG=True, monthEnd=f"{mes_ate:02d}")
    if frete and fluxo == "importacao":                         # a API só informa frete, seguro e CIF na importação
        f.update(metricFreight=True, metricInsurance=True, metricCIF=True)
    f["filterList"] = [{"id": "noSh4pt"}]
    f["filterArray"] = [{"item": list(sh4), "idInput": "noSh4pt"}]
    return f


def cruzado(ano: int, fluxo: str, chave: str, sh4: List[str], cache: Optional[Path] = CACHE, log=print) -> List[dict]:
    """Linhas {mes, <detalhes>, fob, kg, frete, seguro, cif} de uma consulta cruzada (`chave` em CRUZADOS); ausente = None.
    No NCM guarda o código (ncm) e o texto oficial (ncm_nome)."""
    detalhes = CRUZADOS[chave]
    assinatura = hashlib.sha256(json.dumps([ano, fluxo, chave, sorted(sh4), "v2"]).encode()).hexdigest()[:12]
    arq = cache / f"{ano}-{fluxo}-{chave}-{assinatura}.json" if cache else None
    if arq and arq.exists():
        return json.loads(arq.read_text(encoding="utf-8"))
    log(f"  Comex Stat: {ano} {fluxo} por {' × '.join(detalhes)}")
    num = lambda v: float(v) if v not in (None, "") else None
    out = []
    for x in comex._get(filtro_cruzado(ano, fluxo, detalhes, sh4)):
        l = {"mes": int(x["coMes"]), "fob": float(x["vlFob"]), "kg": float(x.get("kgLiquido") or 0),
             "frete": num(x.get("vlFrete")), "seguro": num(x.get("vlSeguro")), "cif": num(x.get("vlCif"))}
        for d in detalhes:
            if d == "ncm":
                l["ncm"], l["ncm_nome"] = x["coNcm"], x["noNcmpt"].replace("\xa0", " ")
            else:
                l[d] = x[CAMPOS[d]].replace("\xa0", " ")
        out.append(l)
    if arq:
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return out


def recorte_cruzado(anos: List[int], fluxo: str, sh4: List[str], cache: Optional[Path] = CACHE, log=print,
                    chaves=("pais_ncm", "urf_via", "uf")) -> Dict[str, Dict[int, List[dict]]]:
    """{chave: {ano: linhas}} para as consultas cruzadas pedidas (padrão: país × NCM, URF × via, UF)."""
    return {c: {a: cruzado(a, fluxo, c, sh4, cache, log) for a in anos} for c in chaves}


def data_da_coleta(anos: List[int], fluxo: str, chaves, cache: Optional[Path] = CACHE):
    """Data (date) da consulta mais antiga em cache para o recorte: é a data em que os dados foram de fato coletados (D81)."""
    from datetime import date
    arqs = [a for ano in anos for c in chaves for a in (cache.glob(f"{ano}-{fluxo}-{c}-*.json") if cache else [])]
    return date.fromtimestamp(min(a.stat().st_mtime for a in arqs)) if arqs else date.today()
