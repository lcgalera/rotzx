"""Indicadores do rotzx Pro (D77): funções puras sobre as linhas da coleta mensal.

Todas devolvem números brutos; quem formata é o relatório. Participação sempre com o denominador junto; ausente = None (nunca 0).
"""
from typing import Dict, Iterable, List, Optional, Tuple


def agregar(linhas: Iterable[dict], meses: Optional[Iterable[int]] = None) -> Dict[str, dict]:
    """{chave: {nome, fob, kg}} somando os meses pedidos (todos, se None)."""
    ms = set(meses) if meses is not None else None
    out: Dict[str, dict] = {}
    for x in linhas:
        if ms is not None and x["mes"] not in ms:
            continue
        d = out.setdefault(x["chave"], {"nome": x["nome"], "fob": 0.0, "kg": 0.0})
        d["fob"] += x["fob"]
        d["kg"] += x["kg"]
    return out


def total(ag: Dict[str, dict]) -> dict:
    return {"fob": sum(d["fob"] for d in ag.values()), "kg": sum(d["kg"] for d in ag.values()), "n": sum(1 for d in ag.values() if d["fob"] > 0)}


def preco_t(fob: float, kg: float) -> Optional[float]:
    """Preço médio em US$ por tonelada; sem peso registrado = None."""
    return fob / kg * 1000 if kg > 0 else None


def ranking(ag: Dict[str, dict], denominador: float, top: Optional[int] = None) -> List[dict]:
    """Itens em ordem de valor, com a parte no denominador dito (fração 0–1)."""
    r = sorted(({"chave": k, **d, "parte": d["fob"] / denominador if denominador else None, "preco_t": preco_t(d["fob"], d["kg"])}
                for k, d in ag.items() if d["fob"] > 0), key=lambda x: -x["fob"])
    return r[:top] if top else r


def variacao(a: Optional[float], b: Optional[float]) -> Optional[float]:
    """Variação relativa de a para b (0,10 = +10%); sem base = None."""
    return (b - a) / a if a and b is not None else None


def pp(parte_a: Optional[float], parte_b: Optional[float]) -> Optional[float]:
    """Mudança de participação em pontos percentuais (fração: 0,01 = 1 p.p.); falta de um dos lados = None."""
    return parte_b - parte_a if parte_a is not None and parte_b is not None else None


def preco_volume(fob0: float, kg0: float, fob1: float, kg1: float) -> Optional[Tuple[float, float]]:
    """Divide a variação de valor em efeito volume e efeito preço (exato: soma = fob1 − fob0).
    Volume = (kg1 − kg0) × preço0; preço = kg1 × (preço1 − preço0). Sem peso em algum lado = None."""
    if kg0 <= 0 or kg1 <= 0:
        return None
    p0, p1 = fob0 / kg0, fob1 / kg1
    return (kg1 - kg0) * p0, kg1 * (p1 - p0)


def dependencia(rank: List[dict]) -> dict:
    """Fatia do maior fornecedor, dos 3 maiores e quantos têm registro."""
    partes = [x["parte"] for x in rank if x["parte"] is not None]
    return {"maior": partes[0] if partes else None, "tres": sum(partes[:3]) if partes else None, "n": len(rank)}


def mensal(linhas_por_ano: Dict[int, List[dict]]) -> List[Tuple[int, int, float, float]]:
    """[(ano, mês, fob, kg)] somando todas as chaves; meses sem linha não aparecem (sem registro, nunca zero)."""
    soma: Dict[Tuple[int, int], List[float]] = {}
    for ano, ls in linhas_por_ano.items():
        for x in ls:
            s = soma.setdefault((ano, x["mes"]), [0.0, 0.0])
            s[0] += x["fob"]
            s[1] += x["kg"]
    return [(a, m, f, k) for (a, m), (f, k) in sorted(soma.items())]
