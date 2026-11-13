"""Validador dos arquivos de detalhamento do atlas (formato `rotzx.detalhe.v1`, docs/SCHEMA.md, D61).

Os arquivos são gerados num projeto de dados à parte; este módulo só confere a forma antes de publicar:

    .venv/bin/python -m rotzx detalhe-validar prototipos/globo/dados/detalhe

Não coleta nem transforma nada.
"""
import csv
import json
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Set

from .. import config

SCHEMA = "rotzx.detalhe.v1"
PASTA = config.ROOT / "prototipos" / "globo" / "dados" / "detalhe"
ANO_MIN = 1997
CAMADAS_PROD = ("parceiros", "uf", "via", "urf", "ncm")
CAMADAS_PAIS = ("produtos", "uf", "via", "urf")
UFS = {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
       "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"}


def _paises() -> Dict[str, Set[str]]:
    with open(config.ROOT / "catalog" / "paises_mundo.csv", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    return {"iso_num": {r["iso_num"] for r in linhas}, "iso3": {r["iso3"] for r in linhas}}


def _bloco(onde: str, b, camada: str, paises: Dict[str, Set[str]]) -> List[str]:
    """Confere um bloco {t, n, top}: denominador, contagem, ordem, valores positivos e códigos."""
    p = []
    if not isinstance(b, dict) or not {"t", "n", "top"} <= set(b):
        return [f"{onde}: precisa de t, n e top"]
    t, n, top = b["t"], b["n"], b["top"]
    if not isinstance(t, (int, float)) or isinstance(t, bool) or t <= 0:
        p.append(f"{onde}: t deve ser número > 0 (ano sem dado não entra no arquivo)")
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        p.append(f"{onde}: n deve ser inteiro ≥ 1")
    if not isinstance(top, list) or not top:
        return p + [f"{onde}: top deve ser lista não vazia"]
    vals = []
    for i, it in enumerate(top):
        if not isinstance(it, list) or len(it) not in (2, 3) or not isinstance(it[0], str):
            p.append(f"{onde}: top[{i}] deve ser [código, valor] ou [código, descrição, valor]"); continue
        v = it[-1]
        if not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0:
            p.append(f"{onde}: top[{i}] com valor que não é número > 0 ({v!r})"); continue
        vals.append(v)
        cod = it[0]
        if camada == "parceiros" and cod not in paises["iso_num"]:
            p.append(f"{onde}: país {cod!r} não está em catalog/paises_mundo.csv (iso_num com 3 dígitos)")
        if camada == "uf" and cod not in UFS:
            p.append(f"{onde}: UF {cod!r} desconhecida")
        if camada == "ncm" and not (len(cod) == 8 and cod.isdigit()):
            p.append(f"{onde}: NCM {cod!r} deve ter 8 dígitos")
        if camada == "produtos" and not (len(cod) == 4 and cod.isdigit()):
            p.append(f"{onde}: SH4 {cod!r} deve ter 4 dígitos")
    if vals != sorted(vals, reverse=True):
        p.append(f"{onde}: top fora de ordem decrescente")
    if isinstance(t, (int, float)) and sum(vals) > t * (1 + 1e-9) + 1:
        p.append(f"{onde}: soma do top ({sum(vals):.0f}) maior que t ({t:.0f})")
    if isinstance(n, int) and n < len(top):
        p.append(f"{onde}: n ({n}) menor que o número de itens em top ({len(top)})")
    return p


def validar_arquivo(obj, tipo: str, chave: Optional[str] = None, paises=None) -> List[str]:
    """Lista de problemas de um arquivo prod/ ou pais/ (vazia = ok)."""
    paises = paises or _paises()
    nome = f"{tipo}/{chave or '?'}"
    if not isinstance(obj, dict) or obj.get("schema") != SCHEMA:
        return [f"{nome}: schema deve ser {SCHEMA!r}"]
    p = [f"{nome}: falta {c!r}" for c in ("fonte", "consulta", "gerado_em", "unidade") if not obj.get(c)]
    if tipo == "prod" and obj.get("codigo") != chave and chave is not None:
        p.append(f"{nome}: codigo {obj.get('codigo')!r} difere do nome do arquivo")
    if tipo == "pais" and chave is not None and obj.get("iso3") != chave:
        p.append(f"{nome}: iso3 {obj.get('iso3')!r} difere do nome do arquivo")
    camadas = CAMADAS_PROD if tipo == "prod" else CAMADAS_PAIS
    if not any(c in obj for c in camadas):
        p.append(f"{nome}: nenhuma camada ({', '.join(camadas)})")
    ano_max = date.today().year
    for c in camadas:
        if c not in obj:
            continue
        if not isinstance(obj[c], dict) or not set(obj[c]) <= {"e", "i"}:
            p.append(f"{nome}.{c}: chaves devem ser 'e' e/ou 'i'"); continue
        for k, anos in obj[c].items():
            for a, b in anos.items():
                if not (a.isdigit() and ANO_MIN <= int(a) <= ano_max):
                    p.append(f"{nome}.{c}.{k}: ano {a!r} fora de {ANO_MIN}–{ano_max}"); continue
                p += _bloco(f"{nome}.{c}.{k}.{a}", b, c, paises)
    return p


def validar_pasta(pasta: Path = PASTA) -> List[str]:
    """Confere índice, arquivos e a correspondência entre os dois."""
    pasta = Path(pasta)
    fi = pasta / "indice.json"
    if not fi.exists():
        return [f"{fi}: não encontrado"]
    paises = _paises()
    try:
        ind = json.loads(fi.read_text(encoding="utf-8"))
    except ValueError as e:
        return [f"indice.json: JSON inválido ({e})"]
    p = [] if ind.get("schema") == SCHEMA else [f"indice.json: schema deve ser {SCHEMA!r}"]
    p += [f"indice.json: falta {c!r}" for c in ("fonte", "gerado_em") if not ind.get(c)]
    for tipo, campo_anos, campo in (("prod", "anos_parceiros", "parceiros"), ("pais", "anos_produtos", "produtos")):
        listados = ind.get(tipo) or {}
        no_disco = {f.stem for f in (pasta / tipo).glob("*.json")} if (pasta / tipo).exists() else set()
        p += [f"{tipo}/{c}.json existe mas não está no índice" for c in sorted(no_disco - set(listados))]
        if tipo == "pais":
            p += [f"indice.json: país {c!r} não está em catalog/paises_mundo.csv" for c in listados if c not in paises["iso3"]]
        for chave, meta in listados.items():
            f = pasta / tipo / f"{chave}.json"
            if not f.exists():
                p.append(f"indice.json: {tipo}/{chave}.json não encontrado"); continue
            try:
                obj = json.loads(f.read_text(encoding="utf-8"))
            except ValueError as e:
                p.append(f"{tipo}/{chave}.json: JSON inválido ({e})"); continue
            p += validar_arquivo(obj, tipo, chave, paises)
            anos_arq = sorted({int(a) for k in (obj.get(campo) or {}).values() for a in k})
            if sorted(meta.get(campo_anos) or []) != anos_arq:
                p.append(f"indice.json: {tipo}/{chave} {campo_anos} não confere com os anos de {campo} no arquivo")
    return p
