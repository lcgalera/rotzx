"""Cotações internacionais de fertilizantes: World Bank Commodity Price Data, o "Pink Sheet" (D80).

Arquivo mensal CMO-Historical-Data-Monthly.xlsx (aba "Monthly Prices", US$ nominais por tonelada métrica), licença CC BY 4.0.
Fica em data/fontes/bancomundial/ (fora do git). `baixar()` busca a versão do ano; sem o arquivo, `serie()` devolve {} e o
estudo sai sem a comparação (avisando no log), nunca com número inventado.
"""
import re
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Tuple

from .. import config

PASTA = config.DATA_DIR / "fontes" / "bancomundial"
ARQUIVO = PASTA / "CMO-Historical-Data-Monthly.xlsx"
URL = "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx"
FONTE = "World Bank Commodity Price Data (The Pink Sheet), CC BY 4.0"

# série → (coluna no cabeçalho, especificação oficial, da aba "Description")
SERIES = {
    "ureia": ("Urea", "ureia granulada/perolada, spot, FOB Oriente Médio"),
    "dap": ("DAP", "DAP (fosfato diamônico), spot, FOB Golfo dos EUA"),
    "tsp": ("TSP", "TSP (superfosfato triplo), spot, importação no Golfo dos EUA"),
    "rocha": ("Phosphate rock", "rocha fosfática, FOB Norte da África"),
    "kcl": ("Potassium chloride", "cloreto de potássio granulado, spot, CFR Brasil"),
}


def baixar(url: str = URL, destino: Path = ARQUIVO, log=print) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": config.USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as r:
        destino.write_bytes(r.read())
    log(f"  Pink Sheet: {destino}")
    return destino


def serie(arq: Path = ARQUIVO) -> Tuple[Dict[str, Dict[Tuple[int, int], float]], Optional[str]]:
    """({série: {(ano, mês): US$/t}}, "Updated on …" do arquivo). Sem arquivo: ({}, None)."""
    if not arq.exists():
        return {}, None
    import openpyxl
    wb = openpyxl.load_workbook(arq, read_only=True, data_only=True)
    linhas = list(wb["Monthly Prices"].iter_rows(values_only=True))
    atualizado = next((str(r[0]) for r in linhas[:6] if r and r[0] and str(r[0]).startswith("Updated")), None)
    cab = next(i for i, r in enumerate(linhas[:10]) if r and any(isinstance(c, str) and c.strip().startswith("Urea") for c in r))
    col = {}
    for nome, (rot, _) in SERIES.items():
        col[nome] = next(j for j, c in enumerate(linhas[cab]) if isinstance(c, str) and c.strip().startswith(rot))
    out: Dict[str, Dict[Tuple[int, int], float]] = {n: {} for n in SERIES}
    for r in linhas[cab + 2:]:
        m = re.fullmatch(r"(\d{4})M(\d{2})", str(r[0] or ""))
        if not m:
            continue
        for nome, j in col.items():
            v = r[j]
            if isinstance(v, (int, float)):                         # "…" ou vazio = sem registro
                out[nome][(int(m.group(1)), int(m.group(2)))] = float(v)
    return out, atualizado
