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


# ---------- D80: volume × preço × mix, concentração (HHI) e acumulado ----------
def por_item(linhas: Iterable[dict], item: str, meses: Optional[Iterable[int]] = None, filtro=None) -> Dict[str, Tuple[float, float]]:
    """{item: (fob, kg)} somando as linhas (do período e do filtro pedidos)."""
    ms = set(meses) if meses is not None else None
    out: Dict[str, List[float]] = {}
    for x in linhas:
        if (ms is not None and x["mes"] not in ms) or (filtro and not filtro(x)):
            continue
        s = out.setdefault(x[item], [0.0, 0.0])
        s[0] += x["fob"]
        s[1] += x["kg"]
    return {k: (v[0], v[1]) for k, v in out.items()}


def decompor(base: Dict[str, Tuple[float, float]], atual: Dict[str, Tuple[float, float]]) -> dict:
    """Divide a variação de valor (atual − base) em volume, preço (dentro de cada item) e mix (composição dos itens).

    Q = peso total com registro de peso; sᵢ = fatia do item no peso; pᵢ = US$/kg do item.
      volume = (Q₁ − Q₀)·P̄₀        preço = Q₁·Σ s₁ᵢ(p₁ᵢ − p₀ᵢ)        mix = Q₁·Σ (s₁ᵢ − s₀ᵢ)·p₀ᵢ
    Item sem base (novo): p₀ = p₁, entra só no mix. Valor sem peso registrado fica numa parcela à parte ("sem_peso").
    A soma das quatro parcelas é exatamente a variação (conferida aqui).
    """
    def lado(d):
        com = {k: (f, kg) for k, (f, kg) in d.items() if kg > 0}
        return com, sum(f for f, kg in d.values() if kg <= 0)
    c0, sp0 = lado(base)
    c1, sp1 = lado(atual)
    V0, V1 = sum(f for f, _ in base.values()), sum(f for f, _ in atual.values())
    Q0, Q1 = sum(kg for _, kg in c0.values()), sum(kg for _, kg in c1.values())
    W0, W1 = sum(f for f, _ in c0.values()), sum(f for f, _ in c1.values())
    if Q0 <= 0 or Q1 <= 0:
        return {"v0": V0, "v1": V1, "variacao": V1 - V0, "volume": None, "preco": None, "mix": None, "sem_peso": None}
    P0 = W0 / Q0
    p0 = {k: f / kg for k, (f, kg) in c0.items()}
    p1 = {k: f / kg for k, (f, kg) in c1.items()}
    s0 = {k: kg / Q0 for k, (_, kg) in c0.items()}
    s1 = {k: kg / Q1 for k, (_, kg) in c1.items()}
    ref = {k: p0.get(k, p1.get(k)) for k in set(p0) | set(p1)}          # item novo: p₀ = p₁
    volume = (Q1 - Q0) * P0
    preco = Q1 * sum(s1[k] * (p1[k] - ref[k]) for k in s1)
    mix = Q1 * sum((s1.get(k, 0.0) - s0.get(k, 0.0)) * ref[k] for k in ref)
    sem_peso = sp1 - sp0
    out = {"v0": V0, "v1": V1, "variacao": V1 - V0, "volume": volume, "preco": preco, "mix": mix, "sem_peso": sem_peso,
           "q0": Q0, "q1": Q1, "p_medio0": P0, "p_medio1": W1 / Q1}
    assert abs(volume + preco + mix + sem_peso - (V1 - V0)) < 1, "decomposição não fecha"
    # preço médio (US$/kg): ΔP̄ = preço puro + mix (por kg de Q₁)
    out["dp_preco"], out["dp_mix"] = preco / Q1, mix / Q1
    return out


def hhi(partes: Iterable[float]) -> Optional[float]:
    """Índice Herfindahl-Hirschman: soma dos quadrados das participações em % (0 a 10.000)."""
    ps = [p for p in partes if p is not None]
    return sum((p * 100) ** 2 for p in ps) if ps else None


def acumulado(mensal: Dict[int, float]) -> Dict[int, float]:
    """{mês: soma até o mês} só para meses com registro contíguos desde janeiro (lacuna interrompe: sem registro, nunca zero)."""
    out, s = {}, 0.0
    for m in range(1, 13):
        if m not in mensal:
            break
        s += mensal[m]
        out[m] = s
    return out
