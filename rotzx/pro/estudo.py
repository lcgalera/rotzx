"""Motor dos estudos-amostra do rotzx Pro (D80, D81): coleta, cálculo, HTML → PDF, planilha e miniaturas.

Cada estudo é um `Recorte` (em rotzx/pro/amostras/): posições SH4, fluxo, produtos e séries de referência, contexto com fontes e os
textos de interpretação (fatos, leitura do analista, sinais e perfis), que são funções dos números calculados aqui. Os rótulos
mudam com o fluxo: na importação o parceiro é fornecedor (origem); na exportação, destino. Frete, seguro e CIF só existem na
importação (a API do Comex Stat só os informa nela), então as partes de frete saem limpas na exportação.
"""
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from ..mundo import codigos, detalhe_coleta, historia
from . import coleta, nomes as N, referencia
from . import indicadores as ind
from . import relatorio as R
from .relatorio import e

ANOS = [2024, 2025, 2026]
PASTA = historia.SAIDA.parent / "pro"
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

ROTULOS = {
    "importacao": {"parceiro": "fornecedor", "Parceiro": "Fornecedor", "parceiros": "fornecedores", "origem": "origem", "origens": "origens",
                   "Origem": "Origem", "verbo": "importou", "adj": "importado", "transacao": "compra", "transacionou": "comprou",
                   "negociou": "vendeu", "Valor": "Valor importado", "fluxo": "importações", "mov": "compras", "Mov": "Compras"},
    "exportacao": {"parceiro": "destino", "Parceiro": "Destino", "parceiros": "destinos", "origem": "destino", "origens": "destinos",
                   "Origem": "Destino", "verbo": "exportou", "adj": "exportado", "transacao": "venda", "transacionou": "vendeu",
                   "negociou": "comprou", "Valor": "Valor exportado", "fluxo": "exportações", "mov": "vendas", "Mov": "Vendas"},
}


@dataclass
class Recorte:
    slug: str                                   # nome dos arquivos: estudo-<slug>.pdf/.xlsx, estudo-<slug>-pN.webp
    fluxo: str                                  # "importacao" ou "exportacao"
    sh4: List[str]
    titulo: str
    subtitulo: Callable[[dict], str]
    fonte_comex: str
    metodo_recorte: str                         # frase do método: o que foi consultado
    metodo_series: str                          # frase do método: quais séries do Pink Sheet
    produtos: List[tuple]                       # (ncm, (séries do Pink Sheet...), base "fob"|"cif")
    graficos: Tuple[str, ...]
    contexto: List[dict]
    contexto_consulta: str
    fatos: Callable[[dict], List[str]]
    leitura: Callable[[dict], List[str]]
    perfis: Callable[[dict], List[tuple]]
    sinais: Callable[[dict], str]               # HTML dos 3 sinais
    nota_preco: str
    nota_ref: str
    nota_calendario: str
    kicker_calendario: str = "Calendário de compra"
    nota_via: Optional[Callable[[dict], str]] = None
    extras: Optional[Callable] = None           # extras(d, PN, UV, ytd, pais) → acrescenta chaves em d
    ncm_ok: Optional[Callable[[str], bool]] = None
    chaves: Tuple[str, str, str] = ("pais_ncm", "urf_via", "uf")
    miniaturas: Tuple[int, ...] = (1, 3)
    titulo_doc: str = ""
    licencas_extra: str = ""
    ancora: str = ""
    # D81: ganchos para estudos com perguntas próprias (ex.: café, "quem paga mais")
    secoes: Optional[Callable] = None           # secoes(cfg, d) → [HTML de cada seção]; substitui as seções 1 a 6 padrão
    grandes: Optional[Callable] = None          # grandes(d) → HTML dos 3 números da capa
    planilha_extra: Optional[Callable] = None   # planilha_extra(d, aba) → abas a mais na planilha
    perfis_titulo: str = "O que os números significam para cada perfil"                            # frase da conferência com o atlas (padrão: soma por parceiro = total do atlas)
    L: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.L = ROTULOS[self.fluxo]

    @property
    def importacao(self) -> bool:
        return self.fluxo == "importacao"

    @property
    def destino(self) -> Path:
        return PASTA / f"estudo-{self.slug}.pdf"

    @property
    def planilha(self) -> Path:
        return PASTA / f"estudo-{self.slug}.xlsx"


# ======================================================================================================================
# cálculo
# ======================================================================================================================
def _nomes_paises() -> Dict[str, str]:
    ponte = detalhe_coleta._ponte(codigos.carregar())
    H = json.loads((historia.SAIDA / "historia.json").read_text(encoding="utf-8"))
    return {nome: H["paises"][iso]["nome"] for nome, iso in ponte.items() if iso in H["paises"]}


def _soma(linhas, chave=None, meses=None, filtro=None):
    """{chave: {fob, kg, frete, cif}} (ou um só dict, sem chave)."""
    ms = set(meses) if meses else None
    out = defaultdict(lambda: {"fob": 0.0, "kg": 0.0, "frete": 0.0, "cif": 0.0})
    for x in linhas:
        if (ms and x["mes"] not in ms) or (filtro and not filtro(x)):
            continue
        d = out[x[chave] if chave else "_"]
        for c in ("fob", "kg", "frete", "cif"):
            d[c] += x.get(c) or 0.0
    return dict(out) if chave else out["_"]


def coletar(cfg: Recorte, log=print) -> dict:
    """{"pais_ncm", "urf_via", "uf"}: {ano: linhas}, já filtradas pelas NCMs do recorte (se houver filtro)."""
    X = coleta.recorte_cruzado(ANOS, cfg.fluxo, cfg.sh4, log=log, chaves=cfg.chaves)
    nomes = ("pais_ncm", "urf_via", "uf")
    out = {}
    for nome, chave in zip(nomes, cfg.chaves):
        out[nome] = {a: [r for r in ls if not cfg.ncm_ok or cfg.ncm_ok(r["ncm"])] if cfg.ncm_ok else ls for a, ls in X[chave].items()}
    return out


def calcular(cfg: Recorte, X: Optional[dict] = None, log=print) -> dict:
    X = X or coletar(cfg, log=log)
    nomes = _nomes_paises()
    pais = lambda c: nomes.get(c, c)
    imp = cfg.importacao
    PN, UV, UF = X["pais_ncm"], X["urf_via"], X["uf"]
    ult = max(x["mes"] for x in PN[2026])
    ytd = list(range(1, ult + 1))
    per = {"2024": (2024, None), "2025": (2025, None), "ytd25": (2025, ytd), "ytd26": (2026, ytd)}
    d: dict = {"ultimo_mes": ult, "ry": f"jan–{MESES[ult - 1]}", "coleta": coleta.data_da_coleta(ANOS, cfg.fluxo, cfg.chaves).strftime("%d/%m/%Y"), "per": {}, "fluxo": cfg.fluxo}
    oficial = {x["ncm"]: x["ncm_nome"] for a in ANOS for x in PN[a]}
    d["ncm_oficial"] = oficial
    pt = lambda v, kg: ind.preco_t(v, kg) if imp else None          # frete e CIF por tonelada: só na importação

    # 1. totais, parceiros e concentração por período (denominador: total do grupo no período)
    for k, (a, ms) in per.items():
        t = _soma(PN[a], meses=ms)
        porp = _soma(PN[a], "pais", ms)
        rank = sorted(({"chave": c, "nome": pais(c), **v, "parte": v["fob"] / t["fob"]} for c, v in porp.items() if v["fob"] > 0),
                      key=lambda x: -x["fob"])
        d["per"][k] = {"total": t, "preco_t": ind.preco_t(t["fob"], t["kg"]), "cif_t": pt(t["cif"], t["kg"]),
                       "frete_t": pt(t["frete"], t["kg"]), "rank": rank, "n": len(rank),
                       "maior": rank[0]["parte"], "tres": sum(x["parte"] for x in rank[:3]), "hhi": ind.hhi(x["parte"] for x in rank)}
    A, B = d["per"]["ytd25"], d["per"]["ytd26"]
    a_rank = {x["chave"]: x for x in A["rank"]}

    # 2. volume × preço × mix: no total (itens = NCM) e por parceiro (as NCMs negociadas com ele)
    dec = ind.decompor(ind.por_item(PN[2025], "ncm", ytd), ind.por_item(PN[2026], "ncm", ytd))
    d["dec_total"] = dec
    p0 = dec["p_medio0"]
    d["dp"] = {"total": (dec["p_medio1"] - p0) / p0, "preco": dec["dp_preco"] / p0, "mix": dec["dp_mix"] / p0}
    s0 = {k: v[1] for k, v in ind.por_item(PN[2025], "ncm", ytd).items()}
    s1 = {k: v[1] for k, v in ind.por_item(PN[2026], "ncm", ytd).items()}
    q0, q1 = sum(s0.values()), sum(s1.values())
    d["mix_ncm"] = sorted(({"ncm": k, "nome": N.ncm(k, oficial.get(k, k)), "s0": s0.get(k, 0) / q0, "s1": s1.get(k, 0) / q1}
                           for k in set(s0) | set(s1)), key=lambda x: -abs(x["s1"] - x["s0"]))[:6]
    forn = []
    for x in B["rank"][:10]:
        f = lambda r, c=x["chave"]: r["pais"] == c
        dd = ind.decompor(ind.por_item(PN[2025], "ncm", ytd, f), ind.por_item(PN[2026], "ncm", ytd, f))
        y = a_rank.get(x["chave"])
        forn.append({"chave": x["chave"], "nome": x["nome"], "parte0": y["parte"] if y else None, "parte1": x["parte"],
                     "pp": ind.pp(y["parte"] if y else None, x["parte"]), **dd})
    d["dec_forn"] = forn

    # 3. preço por produto e parceiro + referência internacional (Pink Sheet)
    ref, ref_atual = referencia.serie()
    d["ref_atualizado"] = ref_atual
    meses_ser = [(a, m) for a in ANOS for m in range(1, 13) if not (a == 2026 and m > ult)]
    d["meses_ser"] = meses_ser

    def media_ref(serie_ref, a):
        v = [ref[serie_ref][(a, m)] for m in ytd if (a, m) in ref.get(serie_ref, {})] if serie_ref and ref else []
        return sum(v) / len(v) if v and len(v) == len(ytd) else None
    prods = []
    for cod, series, base in cfg.produtos:
        f = lambda r, c=cod: r["ncm"] == c
        t0, t1 = _soma(PN[2025], meses=ytd, filtro=f), _soma(PN[2026], meses=ytd, filtro=f)
        o0, o1 = _soma(PN[2025], "pais", ytd, f), _soma(PN[2026], "pais", ytd, f)
        ordem = [c for c, _ in sorted(o1.items(), key=lambda kv: -kv[1]["fob"])]
        origens = []
        for c in ordem[:4]:
            v, w = o1[c], o0.get(c)
            origens.append({"nome": pais(c), "parte1": v["fob"] / t1["fob"], "kg1": v["kg"],
                            "p0": ind.preco_t(w[base], w["kg"]) if w else None, "p1": ind.preco_t(v[base], v["kg"])})
        ser = []
        for c in ordem[:3]:
            mm = defaultdict(lambda: [0.0, 0.0])
            for a in ANOS:
                for r in PN[a]:
                    if r["ncm"] == cod and r["pais"] == c:
                        mm[(a, r["mes"])][0] += r[base] or 0
                        mm[(a, r["mes"])][1] += r["kg"]
            ser.append((pais(c), [ind.preco_t(*mm[k]) if k in mm else None for k in meses_ser]))
        refs = [{"serie": s, "ref0": media_ref(s, 2025), "ref1": media_ref(s, 2026),
                 "mensal": [ref.get(s, {}).get(k) for k in meses_ser] if ref else None,
                 "mes26": {m: ref[s].get((2026, m)) for m in ytd} if ref else {}} for s in (series or ())]
        mm_tot = {m: _soma(PN[2026], meses=[m], filtro=f) for m in ytd}
        r0 = refs[0] if refs else {}
        prods.append({"ncm": cod, "nome": N.ncm(cod, oficial.get(cod, cod)), "serie_ref": r0.get("serie"), "base": base, "refs": refs,
                      "fob0": t0["fob"], "fob1": t1["fob"], "kg0": t0["kg"], "kg1": t1["kg"], "parte1": t1["fob"] / B["total"]["fob"],
                      "imp0": ind.preco_t(t0[base], t0["kg"]), "imp1": ind.preco_t(t1[base], t1["kg"]),
                      "ref0": r0.get("ref0"), "ref1": r0.get("ref1"), "origens": origens, "mensal": ser, "ref_mensal": r0.get("mensal"),
                      "imp_mes26": {m: ind.preco_t(v[base], v["kg"]) for m, v in mm_tot.items()}, "ref_mes26": r0.get("mes26", {})})
    d["produtos"] = prods

    # 4. dependência por produto (as NCMs com mais valor) e no agregado
    porncm1 = _soma(PN[2026], "ncm", ytd)
    dep = []
    relevantes = [c for c, v in sorted(porncm1.items(), key=lambda kv: -kv[1]["fob"]) if v["fob"] >= 0.001 * B["total"]["fob"]]   # ≥ 0,1% do grupo
    for cod in relevantes[:8]:
        linha = {"ncm": cod, "nome": N.ncm(cod, oficial.get(cod, cod)), "parte_grupo": porncm1[cod]["fob"] / B["total"]["fob"]}
        for k, a in (("0", 2025), ("1", 2026)):
            o = _soma(PN[a], "pais", ytd, lambda r, c=cod: r["ncm"] == c)
            tot = sum(v["fob"] for v in o.values())
            ordem = sorted(((c, v["fob"] / tot) for c, v in o.items() if v["fob"] > 0), key=lambda cv: -cv[1]) if tot else []
            linha.update({f"maior{k}": ordem[0][1] if ordem else None, f"nome_maior{k}": pais(ordem[0][0]) if ordem else None,
                          f"tres{k}": sum(p for _, p in ordem[:3]) if ordem else None, f"hhi{k}": ind.hhi(p for _, p in ordem), f"n{k}": len(ordem)})
        dep.append(linha)
    d["dep_prod"] = dep

    # 5. calendário: volume mensal e acumulado por ano (kg)
    cal = {a: {} for a in ANOS}
    for a in ANOS:
        for r in PN[a]:
            cal[a][r["mes"]] = cal[a].get(r["mes"], 0.0) + r["kg"]
    d["cal"] = cal
    d["cal_acum"] = {a: ind.acumulado(cal[a]) for a in ANOS}

    # 6. portos, estados, vias e frete
    def rank_de(linhas, chave, ms, nome=lambda s: s):
        s = _soma(linhas, chave, ms)
        tot = sum(v["fob"] for v in s.values())
        return sorted(({"nome": nome(c), **v, "parte": v["fob"] / tot, "frete_t": pt(v["frete"], v["kg"])}
                       for c, v in s.items() if v["fob"] > 0), key=lambda x: -x["fob"])
    d["urf"] = rank_de(UV[2026], "urf", ytd, N.lugar)
    d["uf"] = rank_de(UF[2026], "uf", ytd)
    d["via"] = {k: rank_de(UV[a], "via", ms, N.lugar) for k, (a, ms) in (("2025", (2025, None)), ("ytd25", (2025, ytd)), ("ytd26", (2026, ytd)))}
    aer = [r for r in UV[2026] if r["via"] == "AEREA" and r["mes"] in ytd]
    porto = lambda r: "PORTO" in r["urf"].upper()
    d["aerea"] = {"fob": sum(r["fob"] for r in aer), "kg": sum(r["kg"] for r in aer),
                  "fob_porto": sum(r["fob"] for r in aer if porto(r)), "kg_porto": sum(r["kg"] for r in aer if porto(r)),
                  "fob_2025": sum(r["fob"] for r in UV[2025] if r["via"] == "AEREA"),
                  "kg_2025": sum(r["kg"] for r in UV[2025] if r["via"] == "AEREA"),
                  "kg_mes": {m: sum(r["kg"] for r in aer if r["mes"] == m) for m in ytd}}
    if imp:
        fr = _soma(PN[2026], "pais", ytd)
        fr0 = _soma(PN[2025], "pais", ytd)
        d["frete_origem"] = sorted(({"nome": pais(c), "kg": v["kg"], "frete_t": ind.preco_t(v["frete"], v["kg"]),
                                     "frete_t0": ind.preco_t(fr0[c]["frete"], fr0[c]["kg"]) if c in fr0 else None,
                                     "frete_pct": v["frete"] / v["fob"] if v["fob"] else None} for c, v in fr.items() if v["kg"] > 0),
                                   key=lambda x: -x["kg"])[:10]
        d["frete_mes"] = {a: {m: ind.preco_t(v["frete"], v["kg"]) for m in range(1, 13) for v in [_soma(PN[a], meses=[m])] if v["kg"] > 0} for a in ANOS}
    else:
        d["frete_origem"], d["frete_mes"] = [], {}
    d["vol_prox_25"] = cal[2025].get(ult + 1) if ult < 12 else None
    d["vol_gap"] = ind.variacao(d["cal_acum"][2025][ult], d["cal_acum"][2026][ult])
    d["sinais"] = {"vol_prox_25": d["vol_prox_25"], "vol_gap": d["vol_gap"]}
    if cfg.extras:
        cfg.extras(d, PN, UV, ytd, pais, UF)
    # contexto: o que o Brasil negociou com os países citados (fato do Comex ao lado do evento)
    d["contexto"] = []
    for c in cfg.contexto:
        d["contexto"].append({**c, "compras": [(p, _soma(PN[2025], meses=ytd, filtro=lambda r, p=p: pais(r["pais"]) == p)["fob"],
                                                 _soma(PN[2026], meses=ytd, filtro=lambda r, p=p: pais(r["pais"]) == p)["fob"]) for p in c["paises"]]})
    return d


# ======================================================================================================================
# HTML → PDF
# ======================================================================================================================
CSS = f"""
.capa h1{{font-size:28pt}}
.grandes{{display:grid;grid-template-columns:repeat(3,1fr);gap:10pt;margin:14pt 0}}
.grandes div{{border-top:2pt solid {R.VERDE};padding-top:6pt}}
.grandes span{{display:block;font-size:8.5pt;color:{R.TINTA2};text-transform:uppercase;letter-spacing:.06em}}
.grandes b{{display:block;font:500 24pt/1.1 Newsreader,serif;margin:3pt 0}}
.grandes small{{font-size:9pt;color:{R.TINTA2}}}
.sinais{{display:grid;grid-template-columns:repeat(3,1fr);gap:8pt;margin:6pt 0 8pt}}
.sinais div{{border:1px solid {R.REGRA};border-radius:3pt;padding:7pt 8pt;font-size:8.8pt;line-height:1.4}}
.sinais b{{display:block;font-size:9.2pt;margin-bottom:3pt}}
.sinais .lim{{display:block;margin-top:4pt;color:{R.TINTA2}}}
.grade2{{display:grid;grid-template-columns:1fr 1fr;gap:6pt 14pt}}
.grade2 h3{{margin:6pt 0 0;font-size:9.5pt}}
.perfil{{border-left:3pt solid {R.OCRE};padding:4pt 10pt;margin:0 0 9pt}}
.perfil h3{{margin:0 0 3pt}}
td.forte{{font-weight:600;color:{R.NEG}}}
tr.sub td{{color:{R.TINTA2};font-size:8.5pt;padding-top:1.5pt;padding-bottom:1.5pt}}
tr.prod td{{font-weight:600;border-top:1px solid {R.TINTA}}}
.inclui li{{margin-bottom:5pt}}
.ctx{{margin:0 0 9pt;break-inside:avoid}}.ctx h3{{margin:0 0 2pt}}.ctx p{{margin:0 0 2pt}}
ol.apendice{{font-size:8.5pt;padding-left:14pt}}ol.apendice li{{margin-bottom:3pt}}
table{{font-size:8.6pt}}
"""


def tabela(cab: List[str], linhas: List[List[str]], txt=(0,), classes: Optional[List[str]] = None) -> str:
    """`txt`: colunas de texto (à esquerda, com quebra de linha); as outras são números. `classes`: classe de cada linha."""
    cl = lambda i: ' class="txt"' if i in txt else ""
    th = "".join(f"<th{cl(i)}>{e(c)}</th>" for i, c in enumerate(cab))
    corpo = "".join(f"<tr{' class=' + chr(34) + classes[j] + chr(34) if classes and classes[j] else ''}>"
                    + "".join(f"<td{cl(i)}>{c}</td>" for i, c in enumerate(l)) + "</tr>" for j, l in enumerate(linhas))
    return f"<table><thead><tr>{th}</tr></thead><tbody>{corpo}</tbody></table>"


def sr(v, f):
    return f(v) if v is not None else "sem registro"


def html(cfg: Recorte, d: dict) -> str:
    L, imp = cfg.L, cfg.importacao
    P, ry, ult = d["per"], d["ry"], d["ultimo_mes"]
    A, B = P["ytd25"], P["ytd26"]
    ta, tb = A["total"], B["total"]
    dec, dp = d["dec_total"], d["dp"]
    fonte = f"{cfg.fonte_comex}. Coleta em {e(d['coleta'])}."
    mes_ult = MESES[ult - 1]
    corpo = []

    # capa
    grandes = cfg.grandes(d) if cfg.grandes else f"""<div class="grandes"><div><span>{L['Valor']}</span><b>{e(R.usd(tb['fob']))}</b><small>{e(R.sinal_pct(ind.variacao(ta['fob'], tb['fob'])))} sobre {ry}/2025 · US$ FOB</small></div>
<div><span>Volume</span><b>{e(R.ton(tb['kg']))}</b><small>{e(R.sinal_pct(ind.variacao(ta['kg'], tb['kg'])))} sobre {ry}/2025 · peso líquido</small></div>
<div><span>Preço médio</span><b>{e(R.usd_t(B['preco_t']))}</b><small>{e(R.sinal_pct(dp['total']))} sobre {ry}/2025, dos quais {e(R.sinal_pp(dp['preco']))} de preço dentro de cada produto</small></div></div>"""
    corpo.append(f"""<section class="capa"><div><div class="marca">rotzx</div><p class="sub" style="margin-top:4pt">Pro · análise sob demanda com dados públicos e oficiais</p></div>
<div><span class="selo">Estudo-amostra</span><h1 style="margin-top:12pt">{e(cfg.titulo)}</h1>
<p class="sub">{cfg.subtitulo(d)}</p>
{grandes}</div>
<div><p class="nota">Exemplo do formato de um diagnóstico do rotzx Pro, com dados reais. Comex Stat (MDIC), dados coletados em {e(d['coleta'])}; Pink Sheet do Banco Mundial ({e(d['ref_atualizado'] or 'sem arquivo')}). Análise de dados públicos; não é recomendação de investimento ou de negócio.</p>
<p class="nota">lcgalera.github.io/rotzx/pro · tabelas deste estudo em planilha: {cfg.planilha.name}</p></div></section>""")

    # resumo + leitura + sinais
    corpo.append(f"""<section class="sec quebra"><div class="kicker">Resumo</div><h2>O que os números mostram</h2>{''.join(f'<p>{x}</p>' for x in cfg.fatos(d))}
<div class="leitura"><div class="kicker">Leitura do analista</div>{''.join(f'<p>{e(x)}</p>' for x in cfg.leitura(d))}<p class="nota" style="margin:0">Interpretação, separada dos fatos acima.</p></div>
<h3>3 sinais para acompanhar no próximo mês</h3>{cfg.sinais(d)}
<p class="fonte">{fonte} Participações sobre o total {L['adj']} do grupo no período. Pink Sheet: World Bank Commodity Price Data, CC BY 4.0. Os limiares dos sinais são critérios de leitura deste estudo, não previsões.</p></section>""")

    padrao = []
    corpo_ini = len(corpo)
    # 1. volume × preço × mix
    fmt_c = lambda v, t: R.usd(v) if t == "total" else R.sinal_usd(v)
    passos = [(f"{ry}/25", dec["v0"], "total"), ("Volume", dec["volume"], "delta"), ("Preço", dec["preco"], "delta"), ("Mix", dec["mix"], "delta")]
    if dec["sem_peso"]:
        passos.append(("Sem peso", dec["sem_peso"], "delta"))
    passos.append((f"{ry}/26", dec["v1"], "total"))
    soma_ok = abs(dec["volume"] + dec["preco"] + dec["mix"] + dec["sem_peso"] - dec["variacao"]) < 1
    lin = [[e(f["nome"]), R.sinal_usd(f["variacao"]), sr(f["volume"], R.sinal_usd), sr(f["preco"], R.sinal_usd), sr(f["mix"], R.sinal_usd),
            sr(f["parte1"], R.pct), sr(f["pp"], R.sinal_pp)] for f in d["dec_forn"]]
    mixl = [[e(x["nome"]), R.pct(x["s0"]), R.pct(x["s1"]), R.sinal_pp(x["s1"] - x["s0"])] for x in d["mix_ncm"][:5]]
    corpo.append(f"""<section class="sec quebra"><div class="kicker">1 · Volume × preço × mix</div><h2>De onde veio a mudança de valor</h2>
<p>O preço médio de um grupo de produtos muda por dois motivos: porque cada produto ficou mais caro ou mais barato (preço) ou porque se {L['transacionou']} mais de um produto caro e menos de um barato (mix). Aqui a variação de valor é dividida em três partes que somam exatamente a variação: <b>volume</b> (mais ou menos toneladas, ao preço médio de {ry}/2025), <b>preço</b> (variação do US$/t dentro de cada NCM) e <b>mix</b> (mudança na participação de cada NCM no peso total).</p>
{R.cascata(passos, fmt_c, altura=165)}
<p class="nota">Soma conferida: volume + preço + mix{' + sem peso' if dec['sem_peso'] else ''} = {e(R.sinal_usd(dec['variacao']))} {'✓' if soma_ok else '✗'}. No preço médio: {e(R.sinal_pct(dp['total']))} = {e(R.sinal_pp(dp['preco']))} de preço {e(R.sinal_pp(dp['mix']))} de mix.</p>
<h3>Por {L['parceiro']} (10 maiores de {ry}/2026)</h3>
{tabela([L['Parceiro'], 'Variação', 'Volume', 'Preço', 'Mix', f'Parte {ry}/26', 'Mudança'], lin)}
<h3>O mix: NCMs cuja participação no peso total mais mudou</h3>
{tabela(['NCM', f'Parte no peso {ry}/25', f'Parte no peso {ry}/26', 'Mudança'], mixl)}
<p class="fonte">{fonte} {L['Parceiro']} decomposto pelas NCMs que {L['negociou']} (a soma por {L['parceiro']} difere do total, que também tem mix entre {L['parceiros']}). Parte = valor do país ÷ total {L['adj']} do grupo no período; mudança em p.p.</p></section>""")

    # 2. preço por produto e parceiro
    linhas, cls = [], []
    for p in d["produtos"]:
        base = "CIF" if p["base"] == "cif" else "FOB"
        linhas.append([e(p["nome"]) + f" <span class='nota'>· NCM {p['ncm']} · {base}</span>", sr(p["imp0"], R.usd_t), sr(p["imp1"], R.usd_t),
                       R.sinal_pct(ind.variacao(p["imp0"], p["imp1"])), R.pct(p["parte1"])])
        cls.append("prod")
        for o in p["origens"][:3]:
            linhas.append([f"&nbsp;&nbsp;{e(o['nome'])}", sr(o["p0"], R.usd_t), sr(o["p1"], R.usd_t), R.sinal_pct(ind.variacao(o["p0"], o["p1"])) if o["p0"] else "sem base", R.pct(o["parte1"])])
            cls.append("sub")
    titulo2 = "Quanto cada produto custou, de cada origem" if imp else "Quanto cada produto valeu, em cada destino"
    corpo.append(f"""<section class="sec quebra"><div class="kicker">2 · Preço por produto e {L['origem']}</div><h2>{titulo2}</h2>
<p>Comparar produto com produto tira o efeito do mix: a diferença de preço entre {L['origens']} passa a refletir preço e condições de venda, não a mistura de produtos diferentes. Em cada produto, as 3 maiores {L['origens']} de {ry}/2026.</p>
{tabela([f"Produto e {L['origem']}", f'US$/t {ry}/25', f'US$/t {ry}/26', 'Variação', f'Parte do valor {ry}/26'], linhas, classes=cls)}
<p class="fonte">{fonte} US$/t = valor ÷ peso líquido. {cfg.nota_preco} Parte: do produto, sobre o valor total {L['adj']} do grupo; da {L['origem']}, sobre o valor {L['adj']} do produto.</p></section>""")

    # 3. referência internacional
    ref_linhas = []
    rotulo_serie = {k: v[1] for k, v in referencia.SERIES.items()}
    for p in d["produtos"]:
        refs = [r for r in p["refs"] if r["ref1"] is not None]
        if not p["refs"]:
            ref_linhas.append([e(p["nome"]), "sem série equivalente no Pink Sheet", sr(p["imp1"], R.usd_t), "—", "—"])
            continue
        if len(p["refs"]) == 1:
            dif = (p["imp1"] - p["ref1"]) if p["imp1"] is not None and p["ref1"] is not None else None
            ref_linhas.append([e(p["nome"]), e(rotulo_serie[p["serie_ref"]]), sr(p["imp1"], R.usd_t), sr(p["ref1"], R.usd_t),
                               (f"{R.sinal_usd(dif)} ({R.sinal_pct(dif / p['ref1'])})" if dif is not None else "—")])
        else:                                                   # faixa entre duas séries (ex.: arábica e robusta)
            lo, hi = min(r["ref1"] for r in refs), max(r["ref1"] for r in refs)
            pos = ("dentro da faixa" if lo <= p["imp1"] <= hi else
                   f"{R.sinal_pct((p['imp1'] - hi) / hi)} sobre a maior" if p["imp1"] > hi else f"{R.sinal_pct((p['imp1'] - lo) / lo)} sob a menor")
            ref_linhas.append([e(p["nome"]), " e ".join(e(rotulo_serie[r["serie"]]) for r in p["refs"]), sr(p["imp1"], R.usd_t),
                               f"{R.usd_t(lo)} a {R.usd_t(hi)}", pos])
    graf = []
    rot = [f"{a}/01" if m == 1 else MESES[m - 1] for a, m in d["meses_ser"]]
    curto = {"kcl": "Pink Sheet", "ureia": "Pink Sheet", "dap": "Pink Sheet", "tsp": "Pink Sheet", "rocha": "Pink Sheet",
             "arabica": "arábica (ref.)", "robusta": "robusta (ref.)"}
    for p in d["produtos"]:
        if p["ncm"] not in cfg.graficos:
            continue
        series = [(n, s, c) for (n, s), c in zip(p["mensal"], (R.VERDE, R.OCRE, "#6E8FA8"))]
        for r, cor in zip(p["refs"], (R.TINTA, R.NEG)):
            if r["mensal"]:
                series.append((curto.get(r["serie"], "Pink Sheet"), r["mensal"], cor, True))
        graf.append(f"<div><h3>{e(p['nome'])} · US$/t {'CIF' if p['base'] == 'cif' else 'FOB'}</h3>{R.linhas_mensais(series, rot, lambda v: R.nf(v, 0), largura=330, altura=150)}</div>")
    if d["ref_atualizado"]:
        ref_bloco = f"""{tabela(['Produto', 'Série de referência (Pink Sheet)', f"{L['adj'].capitalize()} {ry}/26", f'Referência {ry}/26', 'Diferença'], ref_linhas, txt=(0, 1))}
<p class="nota">{cfg.nota_ref}</p>"""
    else:
        ref_bloco = '<p class="nota">Referência internacional indisponível nesta geração: arquivo do Pink Sheet não encontrado.</p>'
    corpo.append(f"""<section class="sec quebra"><div class="kicker">3 · Referência internacional</div><h2>O preço {L['adj']} diante das cotações do Banco Mundial</h2>
{ref_bloco}
<div class="grade2">{''.join(graf)}</div>
<p class="fonte">{fonte} Cotações: {referencia.FONTE}, médias mensais em US$ nominais por tonelada ({e(d['ref_atualizado'] or '')}). Média de {ry} = média simples das cotações mensais. Linhas: 3 maiores {L['origens']} de {ry}/2026 em cada produto; meses sem registro ficam em branco.</p></section>""")

    # 4. dependência por produto
    hmax = max(x["hhi1"] or 0 for x in d["dep_prod"])
    dl = [[e(x["nome"]), R.pct(x["parte_grupo"]), e(x["nome_maior1"] or "sem registro"), sr(x["maior1"], R.pct), sr(x["tres1"], R.pct),
           R.nf(x["hhi1"], 0) if x["hhi1"] is not None else "sem registro", R.nf(x["hhi0"], 0) if x["hhi0"] is not None else "sem registro"] for x in d["dep_prod"]]
    dl.append(["<b>Grupo inteiro (por país)</b>", "100%", e(B["rank"][0]["nome"]), R.pct(B["maior"]), R.pct(B["tres"]), R.nf(B["hhi"], 0), R.nf(A["hhi"], 0)])
    tabela_dep = tabela(['Produto (NCM)', f'Parte no grupo {ry}/26', f"Maior {L['parceiro']}", 'Parte do maior', 'Parte dos 3 maiores', f'HHI {ry}/26', f'HHI {ry}/25'], dl, txt=(0, 2))
    tabela_dep = tabela_dep.replace(f"<td>{R.nf(hmax, 0)}</td>", f'<td class="forte">{R.nf(hmax, 0)}</td>', 1)
    conc = [[rot_, R.pct(p["maior"]), R.pct(p["tres"]), R.nf(p["hhi"], 0), str(p["n"])] for rot_, p in (("2024", P["2024"]), ("2025", P["2025"]), (f"{ry}/2025", A), (f"{ry}/2026", B))]
    corpo.append(f"""<section class="sec quebra"><div class="kicker">4 · Dependência por produto</div><h2>Onde a concentração de {L['parceiros']} é maior</h2>
<p>O HHI (índice Herfindahl-Hirschman) soma os quadrados das participações de cada {L['parceiro']}: vai de perto de 0 (muitos {L['parceiros']} pequenos) a 10.000 (um só {L['parceiro']}). No grupo inteiro a concentração parece moderada, mas produto a produto ela é bem maior, e é no produto que a {L['transacao']} acontece.</p>
{tabela_dep}
<h3>No grupo inteiro, por período</h3>
{tabela(['Período', 'Parte do maior', 'Parte dos 3 maiores', 'HHI', 'Países com registro'], conc)}
<p class="fonte">{fonte} Partes sobre o valor {L['adj']} de cada produto (ou do grupo) no período. Em destaque, o maior HHI. Concentração mede dependência de poucos {L['parceiros']}; não é juízo sobre eles.</p></section>""")

    # 5. calendário
    ca = d["cal_acum"]
    vs = lambda a: ind.variacao(ca[a][ult], ca[2026][ult])
    corpo.append(f"""<section class="sec quebra"><div class="kicker">5 · {cfg.kicker_calendario}</div><h2>2026 está atrasado ou adiantado?</h2>
<p>Até {mes_ult}, o Brasil {L['verbo']} {e(R.ton(ca[2026][ult]))} em 2026: {e(R.sinal_pct(vs(2025)))} em relação ao mesmo ponto de 2025 ({e(R.ton(ca[2025][ult]))}) e {e(R.sinal_pct(vs(2024)))} em relação a 2024 ({e(R.ton(ca[2024][ult]))}). {cfg.nota_calendario}</p>
<h3>Volume por mês (milhões de toneladas)</h3>{R.linhas_ano({a: {m: v / 1e9 for m, v in d['cal'][a].items()} for a in ANOS}, lambda v: R.nf(v, 1 if max(d['cal'][2025].values()) >= 1e9 else 2))}
<h3>Volume acumulado no ano (milhões de toneladas)</h3>{R.linhas_ano({a: {m: v / 1e9 for m, v in ca[a].items()} for a in ANOS}, lambda v: R.nf(v, 1))}
<p class="fonte">{fonte} Peso líquido. Meses de 2026 ainda sem registro (depois de {mes_ult}) ficam em branco, nunca como zero.</p></section>""")

    # 6. portos, estados (e frete, na importação)
    vias = {x["nome"]: x for x in d["via"]["ytd25"]}
    nota_via = cfg.nota_via(d) if cfg.nota_via else ""
    marca = lambda nome: " *" if nota_via and nome == "Aérea" else ""
    vl = [[e(x["nome"]) + marca(x["nome"]), R.usd(vias[x["nome"]]["fob"]) if x["nome"] in vias else "sem registro", R.usd(x["fob"]), R.pct(x["parte"])] for x in d["via"]["ytd26"]]
    if imp:
        ur = [[e(x["nome"]), R.usd(x["fob"]), R.ton(x["kg"]), R.pct(x["parte"]), sr(x["frete_t"], R.usd_t)] for x in d["urf"][:10]]
        fo = [[e(x["nome"]), R.ton(x["kg"]), sr(x["frete_t0"], R.usd_t), sr(x["frete_t"], R.usd_t), sr(x["frete_pct"], R.pct)] for x in d["frete_origem"]]
        corpo.append(f"""<section class="sec quebra"><div class="kicker">6 · Portos, estados e frete</div><h2>Por onde entra e quanto custa trazer</h2>
<h3>Estados (UF), parte do valor importado de {ry}/2026</h3>{R.barras([(x['nome'], x['parte'], f"{R.pct(x['parte'])} · {R.ton(x['kg'])}") for x in d['uf'][:8]], cor=R.OCRE)}
<h3>Unidades da Receita (portos e alfândegas)</h3>
{tabela(['Unidade', 'Valor (US$ FOB)', 'Volume', 'Parte do valor', 'Frete/t'], ur)}
<p class="fonte">{fonte} UF e unidade da Receita como registradas pelo Comex Stat. Partes sobre o valor total importado do grupo em {ry}/2026. Frete/t = frete declarado ÷ peso líquido. IRF = Inspetoria da Receita Federal.</p></section>""")
        corpo.append(f"""<section class="sec"><h3>Frete por origem (10 maiores em volume)</h3>
{tabela(['Origem', f'Volume {ry}/26', f'Frete/t {ry}/25', f'Frete/t {ry}/26', 'Frete ÷ valor FOB'], fo)}
<h3>Vias de transporte, como declaradas</h3>
{tabela(['Via', f'Valor {ry}/25', f'Valor {ry}/26', f'Parte {ry}/26'], vl)}
{nota_via}
<p class="fonte">{fonte} Frete declarado na importação (Comex Stat, métrica de frete). Frete ÷ valor FOB = frete total ÷ valor FOB da origem no período.</p></section>""")
    else:
        ur = [[e(x["nome"]), R.usd(x["fob"]), R.ton(x["kg"]), R.pct(x["parte"]), sr(ind.preco_t(x["fob"], x["kg"]), R.usd_t)] for x in d["urf"][:10]]
        corpo.append(f"""<section class="sec quebra"><div class="kicker">6 · Estados e portos</div><h2>De onde sai e por onde embarca</h2>
<h3>Estados produtores (UF), parte do valor exportado de {ry}/2026</h3>{R.barras([(x['nome'], x['parte'], f"{R.pct(x['parte'])} · {R.ton(x['kg'])}") for x in d['uf'][:8]], cor=R.OCRE)}
<h3>Unidades da Receita (portos e alfândegas de embarque)</h3>
{tabela(['Unidade', 'Valor (US$ FOB)', 'Volume', 'Parte do valor', 'US$/t FOB'], ur)}
<h3>Vias de transporte, como declaradas</h3>
{tabela(['Via', f'Valor {ry}/25', f'Valor {ry}/26', f'Parte {ry}/26'], vl)}
{nota_via}
<p class="fonte">{fonte} Na exportação, o Comex Stat registra como UF o estado produtor da mercadoria, e a unidade da Receita é a de despacho. Partes sobre o valor total exportado do grupo em {ry}/2026. A API não informa frete na exportação. IRF = Inspetoria da Receita Federal.</p></section>""")

    n_secoes = 6
    if cfg.secoes:                                              # o recorte troca as seções 1 a 6 pelas suas
        proprias = cfg.secoes(cfg, d)
        corpo[corpo_ini:] = proprias
        n_secoes = len(proprias)
    nc, nf, nd = n_secoes + 1, n_secoes + 2, n_secoes + 3
    # 7. contexto
    cx = []
    for c in d["contexto"]:
        compras = "; ".join(f"{e(p)}: {e(R.usd(v0))} → {e(R.usd(v1))}" for p, v0, v1 in c["compras"] if v0 or v1)
        fontes = "; ".join(f'{e(n)} ({e(dt)}), <span class="url">{e(u)}</span>' for n, dt, u in c["fontes"])
        cx.append(f"""<div class="ctx"><h3>{e(c['tema'])}</h3><p>{e(c['fato'])}</p>
{f'<p class="nota"><b>{L["Mov"]} brasileiras ({ry}/25 → {ry}/26, US$ FOB):</b> {compras or "sem registro"}.</p>' if c["paises"] else ""}<p class="fonte">Fontes: {fontes}.</p></div>""")
    titulo7 = ("Contexto de fornecimento", "O que aconteceu com os maiores fornecedores") if imp else ("Contexto de mercado", "O que aconteceu com os maiores destinos")
    corpo.append(f"""<section class="sec quebra"><div class="kicker">{nc} · {titulo7[0]}</div><h2>{titulo7[1]}</h2>
<p class="nota">Contexto, não causa comprovada: os fatos abaixo são públicos e datados e acontecem ao mesmo tempo que as mudanças nas {L['mov']}, mas os dados de comércio não provam relação de causa. Só entram itens confirmados em mais de uma fonte (consulta em {cfg.contexto_consulta}).</p>
{''.join(cx)}</section>""")

    # 8. o que fazer com isso
    corpo.append(f"""<section class="sec quebra"><div class="kicker">{nf} · O que fazer com isso</div><h2>{cfg.perfis_titulo}</h2>
<p class="nota">Interpretação, não recomendação de compra, venda ou crédito. Cada bloco aponta o que observar a partir dos números deste estudo.</p>
{''.join(f'<div class="perfil"><h3>{e(t)}</h3><p>{e(x)}</p></div>' for t, x in cfg.perfis(d))}</section>""")

    # 9. o que o diagnóstico inclui
    corpo.append(f"""<section class="sec"><div class="kicker">{nd} · O que o diagnóstico completo inclui</div><h2>Do exemplo para a sua pergunta</h2>
<ul class="inclui">
<li><b>O seu recorte:</b> os produtos (por NCM), as {L['origens']}, os estados e os portos que importam para você, em vez do grupo inteiro.</li>
<li><b>Seus preços contra a média do país:</b> você envia os preços que pagou (ou recebeu), e o estudo compara com a média do Comex Stat por NCM, {L['origem']} e mês, com a mesma base (FOB ou CIF).</li>
<li><b>Planilha com todas as tabelas</b> e as consultas usadas, para refazer ou levar para o seu modelo.</li>
<li><b>Atualização mensal (Acompanhamento):</b> o mesmo recorte a cada nova base do Comex Stat, com os sinais revisados.</li>
<li><b>Conversa de apresentação</b>, se quiser, para discutir a leitura.</li></ul>
<p>Pedido em lcgalera.github.io/rotzx/pro; escopo, prazo e valor chegam por e-mail antes de qualquer compromisso.</p></section>""")

    # 10. fontes e método + apêndice
    citadas = sorted({p["ncm"] for p in d["produtos"]} | {x["ncm"] for x in d["dep_prod"]} | {x["ncm"] for x in d["mix_ncm"]})
    hhi_frete = ("<p><b>HHI e frete.</b> HHI = soma dos quadrados das participações (em %) no valor importado. Frete/t = frete declarado ÷ peso líquido.</p>" if imp
                 else f"<p><b>HHI.</b> HHI = soma dos quadrados das participações (em %) no valor {L['adj']}.</p>")
    corpo.append(f"""<section class="sec quebra"><div class="kicker">Fontes e método</div><h2>Como este estudo foi feito</h2>
<p><b>Comex Stat (MDIC).</b> {cfg.metodo_recorte.format(mes_ult=mes_ult)} Dados coletados em {e(d['coleta'])}. Conferência: os totais das três consultas são iguais entre si em cada ano, e {cfg.ancora or 'a soma dos 12 meses de 2025 por ' + L['parceiro'] + ' é igual ao total anual publicado no atlas rotzx'}.</p>
<p><b>Pink Sheet (Banco Mundial).</b> World Bank Commodity Price Data, arquivo mensal CMO-Historical-Data-Monthly.xlsx ({e(d['ref_atualizado'] or 'sem arquivo')}), licença CC BY 4.0. {cfg.metodo_series}</p>
<p><b>Volume × preço × mix.</b> Com Q = peso total, sᵢ = fatia da NCM no peso e pᵢ = US$/kg da NCM: volume = (Q₁ − Q₀) × preço médio₀; preço = Q₁ × Σ s₁ᵢ (p₁ᵢ − p₀ᵢ); mix = Q₁ × Σ (s₁ᵢ − s₀ᵢ) p₀ᵢ. A soma é exatamente a variação de valor, conferida no código. NCM sem registro no período base entra só no mix; valor sem peso registrado ficaria numa parcela à parte.</p>
{hhi_frete}
<p>Valores em dólares correntes, sem correção pela inflação. Dados do ano corrente podem ser revistos pela fonte. Ausência de registro aparece como “sem registro”, nunca como zero. {titulo7[0]}: fontes citadas na seção {nc}.</p>
<h3>Descrições oficiais das NCMs citadas</h3>
<ol class="apendice">{''.join(f'<li><b>{c}</b> ({e(N.ncm(c, d["ncm_oficial"].get(c, c)))}): {e(d["ncm_oficial"].get(c, "sem registro"))}</li>' for c in citadas)}</ol>
<p class="aviso">rotzx Pro · lcgalera.github.io/rotzx/pro · Análise de dados públicos; não é recomendação de investimento ou de negócio. Licenças: Comex Stat (dados abertos do governo federal), Pink Sheet do Banco Mundial (CC BY 4.0).</p></section>""")
    return R.documento(cfg.titulo_doc or f"rotzx Pro · Estudo-amostra: {cfg.slug}", "".join(corpo), CSS + ".url{word-break:break-all}")


def gerar(cfg: Recorte, log=print) -> dict:
    if not referencia.ARQUIVO.exists():
        try:
            referencia.baixar(log=log)
        except Exception as erro:                                   # sem rede para o Banco Mundial: o estudo sai sem a seção
            log(f"  Pink Sheet indisponível ({erro}); a referência internacional fica de fora")
    d = calcular(cfg, log=log)
    R.pdf(html(cfg, d), cfg.destino)
    log(f"estudo-amostra: {cfg.destino}")
    from . import planilha
    planilha.gerar(d, cfg.planilha, cfg)
    log(f"planilha: {cfg.planilha}")
    R.miniaturas(cfg.destino, cfg.miniaturas, log=log)                 # D79: prévia real na página /pro/
    return d
