"""Câmbio para os estudos do rotzx Pro (D82): PTAX de venda do Banco Central do Brasil, média mensal.

API OData pública do BCB (olinda.bcb.gov.br, serviço PTAX, `CotacaoDolarPeriodo`), dado aberto. A cotação diária fica em cache em
data/fontes/bcb/ (fora do git). Sem rede e sem cache, `media_mensal` devolve {} e o estudo sai só em dólar, nunca com câmbio inventado.
"""
import json
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Dict, Optional, Tuple

from .. import config

PASTA = config.DATA_DIR / "fontes" / "bcb"
URL = ("https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"
       "?@dataInicial='{ini}'&@dataFinalCotacao='{fim}'&$format=json&$select=cotacaoVenda,dataHoraCotacao&$top=10000")
FONTE = "Banco Central do Brasil, PTAX (cotação de venda do dólar), média mensal das cotações diárias"


def diaria(ano_ini: int, ano_fim: int, pasta: Path = PASTA, log=print) -> Dict[str, float]:
    """{"AAAA-MM-DD": PTAX de venda} de 1º/jan de ano_ini a 31/dez de ano_fim (ou hoje). Usa o cache se existir."""
    arq = pasta / f"ptax-{ano_ini}-{ano_fim}.json"
    if arq.exists():
        return json.loads(arq.read_text(encoding="utf-8"))
    fim = min(date(ano_fim, 12, 31), date.today())
    url = URL.format(ini=f"01-01-{ano_ini}", fim=fim.strftime("%m-%d-%Y"))
    url = urllib.parse.quote(url, safe=":/?=&@()$',")
    req = urllib.request.Request(url, headers={"User-Agent": config.USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as r:
        dados = json.loads(r.read())
    out = {}
    for x in dados.get("value", []):
        out[x["dataHoraCotacao"][:10]] = float(x["cotacaoVenda"])      # uma cotação por dia (a de fechamento do boletim)
    pasta.mkdir(parents=True, exist_ok=True)
    arq.write_text(json.dumps(out, sort_keys=True), encoding="utf-8")
    log(f"  PTAX: {len(out)} dias")
    return out


def media_mensal(ano_ini: int, ano_fim: int, pasta: Path = PASTA, log=print) -> Tuple[Dict[Tuple[int, int], float], Optional[str]]:
    """({(ano, mês): média da PTAX de venda}, data da consulta). Sem rede e sem cache: ({}, None)."""
    try:
        d = diaria(ano_ini, ano_fim, pasta, log)
    except Exception as erro:
        log(f"  PTAX indisponível ({erro}); o estudo sai só em dólar")
        return {}, None
    soma = defaultdict(list)
    for dia, v in d.items():
        soma[(int(dia[:4]), int(dia[5:7]))].append(v)
    arq = pasta / f"ptax-{ano_ini}-{ano_fim}.json"
    consulta = date.fromtimestamp(arq.stat().st_mtime).strftime("%d/%m/%Y") if arq.exists() else None
    return {k: sum(v) / len(v) for k, v in soma.items()}, consulta
