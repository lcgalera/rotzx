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
