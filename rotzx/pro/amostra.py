"""Estudo-amostra do rotzx Pro: "De quem o Brasil compra fertilizantes, e o que mudou em 2026" (D77; refeito em D80).

`python -m rotzx pro-amostra` coleta (com cache), calcula e grava em prototipos/globo/pro/ o PDF, a planilha com as tabelas de cada
seção e as miniaturas da página /pro/. Todos os números saem das consultas ao Comex Stat e do Pink Sheet do Banco Mundial; os
textos de interpretação ("Leitura do analista", perfis e sinais) são montados a partir desses números e marcados como interpretação.
"""
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

from ..mundo import codigos, detalhe_coleta, historia, produtos_nomes
from . import coleta, nomes as N, referencia
from . import indicadores as ind
from . import relatorio as R
from .relatorio import e

SH4 = produtos_nomes.GRUPOS["g-fertilizantes"]["sh4"]          # 3101 a 3105, o mesmo grupo do atlas
FLUXO = "importacao"
ANOS = [2024, 2025, 2026]
PASTA = historia.SAIDA.parent / "pro"
DESTINO = PASTA / "estudo-fertilizantes.pdf"
PLANILHA = PASTA / "estudo-fertilizantes.xlsx"
MINIATURAS = (1, 3)                                                   # capa e a página volume × preço × mix
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
FONTE_COMEX = ("Fonte: Comex Stat (MDIC), dados abertos, importações das posições SH4 3101 a 3105 (capítulo 31: adubos e fertilizantes), "
               "US$ correntes e kg líquido")

# produtos analisados um a um e a série do Pink Sheet mais próxima; a base de preço da importação acompanha a da referência
PRODUTOS = [
    ("31042090", "kcl", "cif"),     # Pink Sheet: CFR Brasil → comparado com o CIF por tonelada da importação
    ("31021010", "ureia", "fob"),   # FOB Oriente Médio
    ("31054000", "dap", "fob"),     # não há série de MAP: DAP (FOB Golfo dos EUA) como referência mais próxima
    ("31022100", None, "fob"),      # sem série no Pink Sheet
    ("31031100", "tsp", "fob"),     # TSP, importação no Golfo dos EUA
    ("31031900", None, "fob"),      # sem série no Pink Sheet
]
GRAFICOS_PRODUTO = ("31042090", "31021010", "31054000", "31031100")

# contexto de fornecimento: só fatos públicos com data, confirmados em mais de uma fonte; contexto, não causa comprovada
CONTEXTO = [
    {"tema": "Estreito de Ormuz (Golfo Pérsico)", "paises": ["Arábia Saudita", "Catar", "Omã", "Irã"],
     "fato": "Desde o conflito iniciado em fevereiro de 2026, o trânsito de fertilizantes pelo Estreito de Ormuz caiu fortemente. "
             "Dados do International Trade Centre citados pela ONU apontam queda de 83% no volume de ureia exportado pelas economias "
             "que dependem do estreito em abril de 2026, na comparação anual; o Banco Mundial associou à interrupção a alta das cotações "
             "de ureia no primeiro semestre.",
     "fontes": [("ONU News, “Strait of Hormuz disruption hits energy, fertilizer and industrial trade”", "ago/2026", "https://news.un.org/en/story/2026/08/1168074"),
                ("Banco Mundial, blog Data, “Fertilizer prices surge as Strait of Hormuz disruptions tighten supplies”", "2026", "https://blogs.worldbank.org/en/opendata/fertilizer-prices-surge-as-strait-of-hormuz-disruptions-tighten-")]},
    {"tema": "China: restrições à exportação", "paises": ["China"],
     "fato": "Em março de 2026, a China ampliou as restrições à exportação de fertilizantes; para fosfatados (MAP, DAP e afins), a suspensão "
             "foi noticiada como válida ao menos até agosto de 2026, com o sulfato de amônio entre os poucos produtos ainda liberados. "
             "Não encontramos confirmação oficial sobre o regime depois de agosto.",
     "fontes": [("The Jakarta Post (Reuters), “China restricts fertilizer exports, further crimping war-tightened supply”", "20/03/2026", "https://www.thejakartapost.com/business/2026/03/20/china-restricts-fertilizer-exports-further-crimping-war-tightened-supply.html"),
                ("Fertilizer Daily, “China extends phosphate export curbs through August 2026 as Russia holds fertilizer quotas”", "29/07/2026", "https://www.fertilizerdaily.com/20260729-china-phosphate-export-restrictions-august-2026-russia-quotas/")]},
    {"tema": "Rússia: cotas de exportação", "paises": ["Rússia"],
     "fato": "A Rússia mantém cotas temporárias para a exportação de fertilizantes minerais: o Decreto nº 431, de 22/04/2026, fixou as cotas "
             "de junho a novembro de 2026, e um novo decreto, noticiado em novembro de 2026, estendeu o regime até maio de 2027. Cota limita o "
             "total exportado; não é proibição de venda a um país.",
     "fontes": [("Global Trade Alert, “Russia: Temporary export quotas on mineral fertilisers (June to November 2026)”", "22/04/2026", "https://globaltradealert.org/intervention/154799-russia-temporary-export-quotas-on-mineral-fertilisers-june-to-november-2026"),
                ("Devdiscourse (Reuters), “Russia cuts fertilizer export quota to 18.8 mln tons for Dec 2026 to May 2027”", "nov/2026", "https://www.devdiscourse.com/article/international/4002565-russia-cuts-fertilizer-export-quota-to-188-mln-tons-for-dec-2026-to-may-2027")]},
    {"tema": "União Europeia: tarifa sobre fertilizantes russos e bielorrussos", "paises": ["Rússia"],
     "fato": "O Regulamento (UE) 2025/1227, em vigor desde 1º de julho de 2025, passou a cobrar tarifa sobre fertilizantes nitrogenados "
             "da Rússia e de Belarus importados pela UE, com aumento gradual até 2028.",
     "fontes": [("Comissão Europeia, Access2Markets, “EU increases tariff duties on Russian and Belarusian imports of agricultural products and fertilizers”", "23/07/2025", "https://trade.ec.europa.eu/access-to-markets/en/news/eu-increases-tariff-duties-russian-and-belarusian-imports-agricultural-products-and-fertilizers")]},
]
CONTEXTO_CONSULTA = "24/11/2026"


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


def calcular(X: Optional[dict] = None, log=print) -> dict:
    X = X or coleta.recorte_cruzado(ANOS, FLUXO, SH4, log=log)
    nomes = _nomes_paises()
    pais = lambda c: nomes.get(c, c)
    PN, UV, UF = X["pais_ncm"], X["urf_via"], X["uf"]
    ult = max(x["mes"] for x in PN[2026])
    ytd = list(range(1, ult + 1))
    per = {"2024": (2024, None), "2025": (2025, None), "ytd25": (2025, ytd), "ytd26": (2026, ytd)}
    d: dict = {"ultimo_mes": ult, "ry": f"jan–{MESES[ult - 1]}", "coleta": date.today().strftime("%d/%m/%Y"), "per": {}}
    oficial = {x["ncm"]: x["ncm_nome"] for a in ANOS for x in PN[a]}
    d["ncm_oficial"] = oficial

    # 1. totais, fornecedores e concentração por período (denominador: total importado do grupo no período)
    for k, (a, ms) in per.items():
        t = _soma(PN[a], meses=ms)
        porp = _soma(PN[a], "pais", ms)
        rank = sorted(({"chave": c, "nome": pais(c), **v, "parte": v["fob"] / t["fob"]} for c, v in porp.items() if v["fob"] > 0),
                      key=lambda x: -x["fob"])
        d["per"][k] = {"total": t, "preco_t": ind.preco_t(t["fob"], t["kg"]), "cif_t": ind.preco_t(t["cif"], t["kg"]),
                       "frete_t": ind.preco_t(t["frete"], t["kg"]), "rank": rank, "n": len(rank),
                       "maior": rank[0]["parte"], "tres": sum(x["parte"] for x in rank[:3]), "hhi": ind.hhi(x["parte"] for x in rank)}
    A, B = d["per"]["ytd25"], d["per"]["ytd26"]
    a_rank = {x["chave"]: x for x in A["rank"]}

    # 2. volume × preço × mix: no total (itens = NCM) e por fornecedor (as NCMs que ele vendeu)
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
    # o que mais mudou no que a China vende (explica o efeito mix dela)
    c0 = ind.por_item(PN[2025], "ncm", ytd, lambda r: r["pais"] == "China")
    c1 = ind.por_item(PN[2026], "ncm", ytd, lambda r: r["pais"] == "China")
    d["china_ncm"] = sorted(({"nome": N.ncm(k, oficial.get(k, k)), "kg0": c0.get(k, (0, 0))[1], "kg1": c1.get(k, (0, 0))[1]}
                             for k in set(c0) | set(c1)), key=lambda x: -abs(x["kg1"] - x["kg0"]))[:4]

    # 3. preço por produto e origem + referência internacional (Pink Sheet)
    ref, ref_atual = referencia.serie()
    d["ref_atualizado"] = ref_atual
    meses_ser = [(a, m) for a in ANOS for m in range(1, 13) if not (a == 2026 and m > ult)]
    d["meses_ser"] = meses_ser
    prods = []
    for cod, serie_ref, base in PRODUTOS:
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
        refser = [ref.get(serie_ref, {}).get(k) for k in meses_ser] if serie_ref and ref else None
        def media_ref(a):
            v = [ref[serie_ref][(a, m)] for m in ytd if (a, m) in ref.get(serie_ref, {})] if serie_ref and ref else []
            return sum(v) / len(v) if v and len(v) == len(ytd) else None
        # mês a mês do produto no total (para comparar com a referência no mesmo mês)
        mm_tot = {m: _soma(PN[2026], meses=[m], filtro=f) for m in ytd}
        prods.append({"ncm": cod, "nome": N.ncm(cod, oficial.get(cod, cod)), "serie_ref": serie_ref, "base": base,
                      "fob0": t0["fob"], "fob1": t1["fob"], "kg0": t0["kg"], "kg1": t1["kg"], "parte1": t1["fob"] / B["total"]["fob"],
                      "imp0": ind.preco_t(t0[base], t0["kg"]), "imp1": ind.preco_t(t1[base], t1["kg"]),
                      "ref0": media_ref(2025), "ref1": media_ref(2026), "origens": origens, "mensal": ser, "ref_mensal": refser,
                      "imp_mes26": {m: ind.preco_t(v[base], v["kg"]) for m, v in mm_tot.items()},
                      "ref_mes26": {m: ref[serie_ref].get((2026, m)) for m in ytd} if serie_ref and ref else {}})
    d["produtos"] = prods

    # 4. dependência por produto (as NCMs com mais valor) e no agregado
    porncm1 = _soma(PN[2026], "ncm", ytd)
    dep = []
    for cod in [c for c, _ in sorted(porncm1.items(), key=lambda kv: -kv[1]["fob"])[:8]]:
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
        return sorted(({"nome": nome(c), **v, "parte": v["fob"] / tot, "frete_t": ind.preco_t(v["frete"], v["kg"])}
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
    fr = _soma(PN[2026], "pais", ytd)
    fr0 = _soma(PN[2025], "pais", ytd)
    d["frete_origem"] = sorted(({"nome": pais(c), "kg": v["kg"], "frete_t": ind.preco_t(v["frete"], v["kg"]),
                                 "frete_t0": ind.preco_t(fr0[c]["frete"], fr0[c]["kg"]) if c in fr0 else None,
                                 "frete_pct": v["frete"] / v["fob"] if v["fob"] else None} for c, v in fr.items() if v["kg"] > 0),
                               key=lambda x: -x["kg"])[:10]
    d["frete_mes"] = {a: {m: ind.preco_t(v["frete"], v["kg"]) for m in range(1, 13) for v in [_soma(PN[a], meses=[m])] if v["kg"] > 0} for a in ANOS}

    # 7. sinais para o próximo mês (indicador, valor atual e limiar que mudaria a leitura)
    ureia = next(p for p in prods if p["ncm"] == "31021010")
    d["sinais"] = {
        "frete_atual": d["frete_mes"][2026][ult], "frete_max25": max(d["frete_mes"][2025].values()), "frete_ytd25": A["frete_t"],
        "vol_prox_25": cal[2025].get(ult + 1) if ult < 12 else None, "vol_gap": ind.variacao(d["cal_acum"][2025][ult], d["cal_acum"][2026][ult]),
        "ureia_imp": ureia["imp_mes26"][ult], "ureia_ref": ureia["ref_mes26"].get(ult),
    }
    # contexto: o que o Brasil comprou dos países citados (fato do Comex ao lado do evento)
    for c in CONTEXTO:
        c["compras"] = [(p, (_soma(PN[2025], meses=ytd, filtro=lambda r, p=p: pais(r["pais"]) == p)["fob"]),
                         (_soma(PN[2026], meses=ytd, filtro=lambda r, p=p: pais(r["pais"]) == p)["fob"])) for p in c["paises"]]
    return d


# ======================================================================================================================
# texto de interpretação (montado a partir dos números; marcado como interpretação no relatório)
# ======================================================================================================================
def leitura(d: dict) -> List[str]:
    ry, dp, dec, A, B = d["ry"], d["dp"], d["dec_total"], d["per"]["ytd25"], d["per"]["ytd26"]
    china = next(f for f in d["dec_forn"] if f["chave"] == "China")
    cn = d["china_ncm"][0]
    kcl = next(p for p in d["produtos"] if p["ncm"] == "31042090")
    sa = next(x for x in d["dep_prod"] if x["ncm"] == "31022100")
    return [
        f"O Brasil comprou menos fertilizante e pagou mais por tonelada, e a alta de preço é de preço mesmo, não de composição. "
        f"O preço médio do grupo subiu {R.sinal_pct(dp['total'])} de {ry} de 2025 para 2026: o preço dentro de cada NCM contribuiu com "
        f"{R.sinal_pp(dp['preco'])}, e a mudança na composição das compras, com {R.sinal_pp(dp['mix'])}; ou seja, comparando produto com "
        f"produto, o fertilizante ficou mais caro do que a média sugere.",
        f"A queda de {R.usd(-dec['variacao'])} no valor importado veio do volume ({R.sinal_usd(dec['volume'])}), compensada em boa parte pelo "
        f"preço ({R.sinal_usd(dec['preco'])}). O efeito mix vem sobretudo da China: as vendas chinesas de "
        f"“{cn['nome'].lower()}” caíram de {R.ton(cn['kg0'])} para {R.ton(cn['kg1'])}, no mesmo período em que a China restringiu a exportação de "
        f"fosfatados (ver Contexto). O mix da China ({R.sinal_usd(china['mix'])}) foi maior que o do grupo ({R.sinal_usd(dec['mix'])}), porque outros "
        f"fornecedores compensaram parte dele.",
        f"Os preços pagos pelo Brasil acompanham as referências internacionais com defasagem: no cloreto de potássio, o CIF médio importado "
        f"({R.usd_t(kcl['imp1'])}) ficou perto da cotação CFR Brasil do Banco Mundial ({R.usd_t(kcl['ref1'])}). A dependência por produto é bem "
        f"maior que a do agregado: no sulfato de amônio, {sa['nome_maior1']} respondeu por {R.pct(sa['maior1'])} do valor importado, enquanto no "
        f"grupo inteiro o maior fornecedor teve {R.pct(B['maior'])}.",
    ]


def perfis(d: dict) -> List[tuple]:
    B, A, s = d["per"]["ytd26"], d["per"]["ytd25"], d["sinais"]
    gap = s["vol_gap"]
    sa = next(x for x in d["dep_prod"] if x["ncm"] == "31022100")
    mapr = next(x for x in d["dep_prod"] if x["ncm"] == "31054000")
    urf3 = sum(x["parte"] for x in d["urf"][:3])
    return [
        ("Cooperativa ou revenda",
         f"O volume acumulado de {d['ry']} está {R.sinal_pct(gap)} abaixo do mesmo período de 2025. Se a demanda do campo não caiu na mesma "
         f"proporção, parte das compras pode ter ficado para os meses seguintes, o que concentra a disputa por produto e frete perto da safra. "
         f"Vale comparar o próprio calendário de compra com o calendário do país (seção 5)."),
        ("Trading ou importador",
         f"Com o preço subindo dentro de cada produto ({R.sinal_pp(d['dp']['preco'])} na média do grupo) e a origem mudando (Canadá à frente da Rússia no KCl, "
         f"menos China nos fosfatados), a comparação útil é por NCM e por origem, não pela média do grupo. Onde o preço importado se afastar "
         f"da referência internacional (seção 3), há espaço para renegociar ou para rever a origem."),
        ("Porto ou operador logístico",
         f"Três portos somaram {R.pct(urf3)} do valor importado, e o frete médio por tonelada subiu de {R.usd_t(A['frete_t'])} para "
         f"{R.usd_t(B['frete_t'])}. Com volume menor e frete maior, a receita por tonelada movimentada e a ocupação de armazéns tendem a "
         f"seguir caminhos diferentes; o detalhe por porto e origem está na seção 6."),
        ("Banco ou crédito agro",
         f"Insumo mais caro por tonelada eleva a necessidade de capital de giro por hectare. A concentração por produto é um fator a "
         f"considerar na análise de risco de fornecimento: {R.pct(sa['maior1'])} do sulfato de amônio veio de {sa['nome_maior1']} e "
         f"{R.pct(mapr['maior1'])} do MAP veio de {mapr['nome_maior1']}."),
    ]


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


def _tabela(cab: List[str], linhas: List[List[str]], txt=(0,), classes: Optional[List[str]] = None) -> str:
    """`txt`: colunas de texto (à esquerda, com quebra de linha); as outras são números. `classes`: classe de cada linha."""
    cl = lambda i: ' class="txt"' if i in txt else ""
    th = "".join(f"<th{cl(i)}>{e(c)}</th>" for i, c in enumerate(cab))
    corpo = "".join(f"<tr{' class=' + chr(34) + classes[j] + chr(34) if classes and classes[j] else ''}>"
                    + "".join(f"<td{cl(i)}>{c}</td>" for i, c in enumerate(l)) + "</tr>" for j, l in enumerate(linhas))
    return f"<table><thead><tr>{th}</tr></thead><tbody>{corpo}</tbody></table>"


def _sr(v, f):
    return f(v) if v is not None else "sem registro"


def html(d: dict) -> str:
    P, ry, ult = d["per"], d["ry"], d["ultimo_mes"]
    A, B, p25 = P["ytd25"], P["ytd26"], P["2025"]
    ta, tb = A["total"], B["total"]
    dec, dp = d["dec_total"], d["dp"]
    fonte = f"{FONTE_COMEX}. Coleta em {e(d['coleta'])}."
    mes_ult = MESES[ult - 1]
    corpo = []

    # capa
    corpo.append(f"""<section class="capa"><div><div class="marca">rotzx</div><p class="sub" style="margin-top:4pt">Pro · análise sob demanda com dados públicos e oficiais</p></div>
<div><span class="selo">Estudo-amostra</span><h1 style="margin-top:12pt">De quem o Brasil compra fertilizantes, e o que mudou em 2026</h1>
<p class="sub">Importações brasileiras de adubos e fertilizantes (SH4 3101 a 3105), {ry} de 2026 comparado com {ry} de 2025: volume, preço e mix, preço por produto e origem, dependência, calendário de compra, portos e frete.</p>
<div class="grandes"><div><span>Valor importado</span><b>{e(R.usd(tb['fob']))}</b><small>{e(R.sinal_pct(ind.variacao(ta['fob'], tb['fob'])))} sobre {ry}/2025 · US$ FOB</small></div>
<div><span>Volume</span><b>{e(R.ton(tb['kg']))}</b><small>{e(R.sinal_pct(ind.variacao(ta['kg'], tb['kg'])))} sobre {ry}/2025 · peso líquido</small></div>
<div><span>Preço médio</span><b>{e(R.usd_t(B['preco_t']))}</b><small>{e(R.sinal_pct(dp['total']))} sobre {ry}/2025, dos quais {e(R.sinal_pp(dp['preco']))} de preço dentro de cada produto</small></div></div></div>
<div><p class="nota">Exemplo do formato de um diagnóstico do rotzx Pro, com dados reais. Comex Stat (MDIC), dados coletados em {e(d['coleta'])}; Pink Sheet do Banco Mundial ({e(d['ref_atualizado'] or 'sem arquivo')}). Análise de dados públicos; não é recomendação de investimento ou de negócio.</p>
<p class="nota">lcgalera.github.io/rotzx/pro · tabelas deste estudo em planilha: estudo-fertilizantes.xlsx</p></div></section>""")

    # resumo + leitura + sinais
    china = next(f for f in d["dec_forn"] if f["chave"] == "China")
    sa = next(x for x in d["dep_prod"] if x["ncm"] == "31022100")
    s = d["sinais"]
    fatos = [
        f"De {ry} de 2026, o Brasil importou {e(R.usd(tb['fob']))} em fertilizantes ({e(R.ton(tb['kg']))}): {e(R.sinal_pct(ind.variacao(ta['fob'], tb['fob'])))} em valor e "
        f"{e(R.sinal_pct(ind.variacao(ta['kg'], tb['kg'])))} em volume sobre {ry} de 2025.",
        f"Da variação de valor ({e(R.sinal_usd(dec['variacao']))}), o volume respondeu por {e(R.sinal_usd(dec['volume']))}, o preço dentro de cada NCM por "
        f"{e(R.sinal_usd(dec['preco']))} e a mudança de composição (mix) por {e(R.sinal_usd(dec['mix']))}.",
        f"O preço médio do grupo foi de {e(R.usd_t(A['preco_t']))} para {e(R.usd_t(B['preco_t']))} ({e(R.sinal_pct(dp['total']))}): {e(R.sinal_pp(dp['preco']))} vieram do preço "
        f"dentro das NCMs e {e(R.sinal_pp(dp['mix']))} do mix.",
        f"Os 3 maiores fornecedores somaram {e(R.pct(B['tres']))} do valor importado (eram {e(R.pct(A['tres']))} em {ry} de 2025); {e(B['rank'][0]['nome'])} seguiu à frente, com {e(R.pct(B['maior']))}.",
        f"Por produto, a concentração é maior: {e(sa['nome_maior1'])} vendeu {e(R.pct(sa['maior1']))} do sulfato de amônio importado (HHI {e(R.nf(sa['hhi1'], 0))} de 10.000).",
        f"O frete médio declarado subiu de {e(R.usd_t(A['frete_t']))} para {e(R.usd_t(B['frete_t']))} por tonelada.",
    ]
    vol_lim = R.ton(s["vol_prox_25"]) if s["vol_prox_25"] else "sem registro"
    sinais = f"""<div class="sinais">
<div><b>1 · Frete por tonelada</b>{e(MESES[ult - 1])}/2026: {e(R.usd_t(s['frete_atual']))} (média de {ry}/2025: {e(R.usd_t(s['frete_ytd25']))}).<span class="lim">Muda a leitura se: voltar a ficar abaixo de {e(R.usd_t(s['frete_max25']))}, o maior valor mensal de 2025, indicando alívio logístico.</span></div>
<div><b>2 · Volume do próximo mês</b>Acumulado de {ry}: {e(R.sinal_pct(s['vol_gap']))} sobre 2025.<span class="lim">Muda a leitura se: {MESES[ult] if ult < 12 else 'o próximo mês'}/2026 passar de {e(vol_lim)} (o mesmo mês de 2025), primeiro sinal de compra adiada, não perdida.</span></div>
<div><b>3 · Ureia × referência</b>{e(mes_ult)}/2026: importada a {e(R.usd_t(s['ureia_imp']))} FOB; Pink Sheet (FOB Oriente Médio) a {e(_sr(s['ureia_ref'], R.usd_t))}.<span class="lim">Muda a leitura se: a importada ficar acima da referência por dois meses seguidos, o que indicaria prêmio sobre o mercado internacional.</span></div></div>"""
    corpo.append(f"""<section class="sec quebra"><div class="kicker">Resumo</div><h2>O que os números mostram</h2>{''.join(f'<p>{x}</p>' for x in fatos)}
<div class="leitura"><div class="kicker">Leitura do analista</div>{''.join(f'<p>{e(x)}</p>' for x in leitura(d))}<p class="nota" style="margin:0">Interpretação, separada dos fatos acima.</p></div>
<h3>3 sinais para acompanhar no próximo mês</h3>{sinais}
<p class="fonte">{fonte} Participações sobre o total importado do grupo no período. Pink Sheet: World Bank Commodity Price Data, CC BY 4.0. Os limiares dos sinais são critérios de leitura deste estudo, não previsões.</p></section>""")

    # 1. volume × preço × mix
    fmt_c = lambda v, t: R.usd(v) if t == "total" else R.sinal_usd(v)
    passos = [(f"{ry}/25", dec["v0"], "total"), ("Volume", dec["volume"], "delta"), ("Preço", dec["preco"], "delta"), ("Mix", dec["mix"], "delta")]
    if dec["sem_peso"]:
        passos.append(("Sem peso", dec["sem_peso"], "delta"))
    passos.append((f"{ry}/26", dec["v1"], "total"))
    soma_ok = abs(dec["volume"] + dec["preco"] + dec["mix"] + dec["sem_peso"] - dec["variacao"]) < 1
    lin = [[e(f["nome"]), R.sinal_usd(f["variacao"]), _sr(f["volume"], R.sinal_usd), _sr(f["preco"], R.sinal_usd), _sr(f["mix"], R.sinal_usd),
            _sr(f["parte1"], R.pct), _sr(f["pp"], R.sinal_pp)] for f in d["dec_forn"]]
    mixl = [[e(x["nome"]), R.pct(x["s0"]), R.pct(x["s1"]), R.sinal_pp(x["s1"] - x["s0"])] for x in d["mix_ncm"][:5]]
    corpo.append(f"""<section class="sec quebra"><div class="kicker">1 · Volume × preço × mix</div><h2>De onde veio a mudança de valor</h2>
<p>O preço médio de um grupo de produtos muda por dois motivos: porque cada produto ficou mais caro ou mais barato (preço) ou porque se comprou mais de um produto caro e menos de um barato (mix). Aqui a variação de valor é dividida em três partes que somam exatamente a variação: <b>volume</b> (mais ou menos toneladas, ao preço médio de {ry}/2025), <b>preço</b> (variação do US$/t dentro de cada NCM) e <b>mix</b> (mudança na participação de cada NCM no peso total).</p>
{R.cascata(passos, fmt_c, altura=165)}
<p class="nota">Soma conferida: volume + preço + mix{' + sem peso' if dec['sem_peso'] else ''} = {e(R.sinal_usd(dec['variacao']))} {'✓' if soma_ok else '✗'}. No preço médio: {e(R.sinal_pct(dp['total']))} = {e(R.sinal_pp(dp['preco']))} de preço {e(R.sinal_pp(dp['mix']))} de mix.</p>
<h3>Por fornecedor (10 maiores de {ry}/2026)</h3>
{_tabela(['Fornecedor', 'Variação', 'Volume', 'Preço', 'Mix', f'Parte {ry}/26', 'Mudança'], lin)}
<h3>O mix: NCMs cuja participação no peso total mais mudou</h3>
{_tabela(['NCM', f'Parte no peso {ry}/25', f'Parte no peso {ry}/26', 'Mudança'], mixl)}
<p class="fonte">{fonte} Fornecedor decomposto pelas NCMs que vendeu (a soma por fornecedor difere do total, que também tem mix entre fornecedores). Parte = valor do país ÷ total importado do grupo no período; mudança em p.p.</p></section>""")

    # 2. preço por produto e origem + referência
    linhas, cls = [], []
    for p in d["produtos"]:
        base = "CIF" if p["base"] == "cif" else "FOB"
        linhas.append([e(p["nome"]) + f" <span class='nota'>· NCM {p['ncm']} · {base}</span>", _sr(p["imp0"], R.usd_t), _sr(p["imp1"], R.usd_t),
                       R.sinal_pct(ind.variacao(p["imp0"], p["imp1"])), R.pct(p["parte1"])])
        cls.append("prod")
        for o in p["origens"][:3]:
            linhas.append([f"&nbsp;&nbsp;{e(o['nome'])}", _sr(o["p0"], R.usd_t), _sr(o["p1"], R.usd_t), R.sinal_pct(ind.variacao(o["p0"], o["p1"])) if o["p0"] else "sem base", R.pct(o["parte1"])])
            cls.append("sub")
    corpo.append(f"""<section class="sec quebra"><div class="kicker">2 · Preço por produto e origem</div><h2>Quanto cada produto custou, de cada origem</h2>
<p>Comparar produto com produto tira o efeito do mix: a diferença de preço entre origens passa a refletir preço e condições de venda, não a mistura de produtos diferentes. Em cada produto, as 3 maiores origens de {ry}/2026.</p>
{_tabela(['Produto e origem', f'US$/t {ry}/25', f'US$/t {ry}/26', 'Variação', f'Parte do valor {ry}/26'], linhas, classes=cls)}
<p class="fonte">{fonte} US$/t = valor ÷ peso líquido. Base FOB (valor no embarque), exceto no cloreto de potássio, em CIF (com frete e seguro), para comparar com a referência CFR Brasil. Parte: do produto, sobre o valor total importado do grupo; da origem, sobre o valor importado do produto.</p></section>""")

    # 2b. referência internacional
    ref_linhas = []
    rotulo_serie = {k: v[1] for k, v in referencia.SERIES.items()}
    for p in d["produtos"]:
        if not p["serie_ref"]:
            ref_linhas.append([e(p["nome"]), "sem série equivalente no Pink Sheet", _sr(p["imp1"], R.usd_t), "—", "—"])
            continue
        dif = (p["imp1"] - p["ref1"]) if p["imp1"] is not None and p["ref1"] is not None else None
        ref_linhas.append([e(p["nome"]), e(rotulo_serie[p["serie_ref"]]), _sr(p["imp1"], R.usd_t), _sr(p["ref1"], R.usd_t),
                           (f"{R.sinal_usd(dif).replace('US$ ', 'US$ ')} ({R.sinal_pct(dif / p['ref1'])})" if dif is not None else "—")])
    graf = []
    rot = [f"{a}/01" if m == 1 else MESES[m - 1] for a, m in d["meses_ser"]]
    for p in d["produtos"]:
        if p["ncm"] not in GRAFICOS_PRODUTO:
            continue
        series = [(n, s, c) for (n, s), c in zip(p["mensal"], (R.VERDE, R.OCRE, "#6E8FA8"))]
        if p["ref_mensal"]:
            series.append(("Pink Sheet", p["ref_mensal"], R.TINTA, True))
        graf.append(f"<div><h3>{e(p['nome'])} · US$/t {'CIF' if p['base'] == 'cif' else 'FOB'}</h3>{R.linhas_mensais(series, rot, lambda v: R.nf(v, 0), largura=330, altura=150)}</div>")
    if d["ref_atualizado"]:
        ref_bloco = f"""{_tabela(['Produto', 'Série de referência (Pink Sheet)', f'Importado {ry}/26', f'Referência {ry}/26', 'Diferença'], ref_linhas, txt=(0, 1))}
<p class="nota">Aproximação, não equivalência: a importação brasileira é a média do que foi declarado no mês (contratos fechados antes, especificações e portos variados), e a referência é uma cotação spot de um mercado específico. Base de cada comparação: KCl em CIF do Brasil × CFR Brasil; ureia, MAP e superfosfato em FOB da origem × FOB ou importação no mercado da série. O MAP é comparado com o DAP, a série mais próxima disponível. Rocha fosfática (Pink Sheet) não entra: é a posição 2510, fora do capítulo 31.</p>"""
    else:
        ref_bloco = '<p class="nota">Referência internacional indisponível nesta geração: arquivo do Pink Sheet não encontrado.</p>'
    corpo.append(f"""<section class="sec quebra"><div class="kicker">3 · Referência internacional</div><h2>O preço importado diante das cotações do Banco Mundial</h2>
{ref_bloco}
<div class="grade2">{''.join(graf)}</div>
<p class="fonte">{fonte} Cotações: {referencia.FONTE}, médias mensais em US$ nominais por tonelada ({e(d['ref_atualizado'] or '')}). Média de {ry} = média simples das cotações mensais. Linhas: 3 maiores origens de {ry}/2026 em cada produto; meses sem registro ficam em branco.</p></section>""")

    # 4. dependência por produto
    hmax = max(x["hhi1"] or 0 for x in d["dep_prod"])
    dl = [[e(x["nome"]), R.pct(x["parte_grupo"]), e(x["nome_maior1"] or "sem registro"), _sr(x["maior1"], R.pct), _sr(x["tres1"], R.pct),
           R.nf(x["hhi1"], 0) if x["hhi1"] is not None else "sem registro", R.nf(x["hhi0"], 0) if x["hhi0"] is not None else "sem registro"] for x in d["dep_prod"]]
    dl.append(["<b>Grupo inteiro (por país)</b>", "100%", e(B["rank"][0]["nome"]), R.pct(B["maior"]), R.pct(B["tres"]), R.nf(B["hhi"], 0), R.nf(A["hhi"], 0)])
    tabela_dep = _tabela(['Produto (NCM)', f'Parte no grupo {ry}/26', 'Maior fornecedor', 'Parte do maior', 'Parte dos 3 maiores', f'HHI {ry}/26', f'HHI {ry}/25'], dl, txt=(0, 2))
    tabela_dep = tabela_dep.replace(f"<td>{R.nf(hmax, 0)}</td>", f'<td class="forte">{R.nf(hmax, 0)}</td>', 1)
    conc = [[rot_, R.pct(p["maior"]), R.pct(p["tres"]), R.nf(p["hhi"], 0), str(p["n"])] for rot_, p in (("2024", P["2024"]), ("2025", P["2025"]), (f"{ry}/2025", A), (f"{ry}/2026", B))]
    corpo.append(f"""<section class="sec quebra"><div class="kicker">4 · Dependência por produto</div><h2>Onde a concentração de fornecedores é maior</h2>
<p>O HHI (índice Herfindahl-Hirschman) soma os quadrados das participações de cada fornecedor: vai de perto de 0 (muitos fornecedores pequenos) a 10.000 (um só fornecedor). No grupo inteiro a concentração parece moderada, mas produto a produto ela é bem maior, e é no produto que a compra acontece.</p>
{tabela_dep}
<h3>No grupo inteiro, por período</h3>
{_tabela(['Período', 'Parte do maior', 'Parte dos 3 maiores', 'HHI', 'Países com registro'], conc)}
<p class="fonte">{fonte} Partes sobre o valor importado de cada produto (ou do grupo) no período. Em destaque, o maior HHI. Concentração mede dependência de poucos fornecedores; não é juízo sobre eles.</p></section>""")

    # 5. calendário
    ca = d["cal_acum"]
    vs = lambda a: ind.variacao(ca[a][ult], ca[2026][ult])
    corpo.append(f"""<section class="sec quebra"><div class="kicker">5 · Calendário de compra</div><h2>2026 está atrasado ou adiantado?</h2>
<p>Até {mes_ult}, o Brasil importou {e(R.ton(ca[2026][ult]))} em 2026: {e(R.sinal_pct(vs(2025)))} em relação ao mesmo ponto de 2025 ({e(R.ton(ca[2025][ult]))}) e {e(R.sinal_pct(vs(2024)))} em relação a 2024 ({e(R.ton(ca[2024][ult]))}). As compras para a safra de verão costumam se concentrar no segundo semestre, como mostram 2024 e 2025.</p>
<h3>Volume por mês (milhões de toneladas)</h3>{R.linhas_ano({a: {m: v / 1e9 for m, v in d['cal'][a].items()} for a in ANOS}, lambda v: R.nf(v, 1))}
<h3>Volume acumulado no ano (milhões de toneladas)</h3>{R.linhas_ano({a: {m: v / 1e9 for m, v in ca[a].items()} for a in ANOS}, lambda v: R.nf(v, 1))}
<p class="fonte">{fonte} Peso líquido. Meses de 2026 ainda sem registro (depois de {mes_ult}) ficam em branco, nunca como zero.</p></section>""")

    # 6. portos, estados e frete
    ur = [[e(x["nome"]), R.usd(x["fob"]), R.ton(x["kg"]), R.pct(x["parte"]), _sr(x["frete_t"], R.usd_t)] for x in d["urf"][:10]]
    fo = [[e(x["nome"]), R.ton(x["kg"]), _sr(x["frete_t0"], R.usd_t), _sr(x["frete_t"], R.usd_t), _sr(x["frete_pct"], R.pct)] for x in d["frete_origem"]]
    vias = {x["nome"]: x for x in d["via"]["ytd25"]}
    vl = [[e(x["nome"]) + (" *" if x["nome"] == "Aérea" else ""), R.usd(vias[x["nome"]]["fob"]) if x["nome"] in vias else "sem registro", R.usd(x["fob"]), R.pct(x["parte"])] for x in d["via"]["ytd26"]]
    ae = d["aerea"]
    corpo.append(f"""<section class="sec quebra"><div class="kicker">6 · Portos, estados e frete</div><h2>Por onde entra e quanto custa trazer</h2>
<h3>Estados (UF), parte do valor importado de {ry}/2026</h3>{R.barras([(x['nome'], x['parte'], f"{R.pct(x['parte'])} · {R.ton(x['kg'])}") for x in d['uf'][:8]], cor=R.OCRE)}
<h3>Unidades da Receita (portos e alfândegas)</h3>
{_tabela(['Unidade', 'Valor (US$ FOB)', 'Volume', 'Parte do valor', 'Frete/t'], ur)}
<p class="fonte">{fonte} UF e unidade da Receita como registradas pelo Comex Stat. Partes sobre o valor total importado do grupo em {ry}/2026. Frete/t = frete declarado ÷ peso líquido. IRF = Inspetoria da Receita Federal.</p></section>""")
    corpo.append(f"""<section class="sec"><h3>Frete por origem (10 maiores em volume)</h3>
{_tabela(['Origem', f'Volume {ry}/26', f'Frete/t {ry}/25', f'Frete/t {ry}/26', 'Frete ÷ valor FOB'], fo)}
<h3>Vias de transporte, como declaradas</h3>
{_tabela(['Via', f'Valor {ry}/25', f'Valor {ry}/26', f'Parte {ry}/26'], vl)}
<p class="nota">* Via aérea provavelmente registrada por engano. Em {ry} de 2026 a via “aérea” somou {e(R.usd(ae['fob']))} ({e(R.ton(ae['kg']))}), contra {e(R.usd(ae['fob_2025']))} em todo o ano de 2025. Desse total, {e(R.pct(ae['fob_porto'] / ae['fob']))} do valor foi desembaraçado em unidades da Receita de portos marítimos, em lotes de milhares de toneladas, incompatíveis com transporte aéreo, e o volume cresce mês a mês ({e(R.ton(ae['kg_mes'][1]))} em janeiro, {e(R.ton(ae['kg_mes'][ult]))} em {mes_ult}). Mantemos o dado como a fonte publica; as análises de porto e frete usam a unidade da Receita, que não depende da via.</p>
<p class="fonte">{fonte} Frete declarado na importação (Comex Stat, métrica de frete). Frete ÷ valor FOB = frete total ÷ valor FOB da origem no período.</p></section>""")

    # 7. contexto de fornecimento
    cx = []
    for c in CONTEXTO:
        compras = "; ".join(f"{e(p)}: {e(R.usd(v0))} → {e(R.usd(v1))}" for p, v0, v1 in c["compras"] if v0 or v1)
        fontes = "; ".join(f'{e(n)} ({e(dt)}), <span class="url">{e(u)}</span>' for n, dt, u in c["fontes"])
        cx.append(f"""<div class="ctx"><h3>{e(c['tema'])}</h3><p>{e(c['fato'])}</p>
<p class="nota"><b>Compras brasileiras ({ry}/25 → {ry}/26, US$ FOB):</b> {compras or 'sem registro'}.</p><p class="fonte">Fontes: {fontes}.</p></div>""")
    corpo.append(f"""<section class="sec quebra"><div class="kicker">7 · Contexto de fornecimento</div><h2>O que aconteceu com os maiores fornecedores</h2>
<p class="nota">Contexto, não causa comprovada: os fatos abaixo são públicos e datados e acontecem ao mesmo tempo que as mudanças nas compras, mas os dados de comércio não provam relação de causa. Só entram itens confirmados em mais de uma fonte (consulta em {CONTEXTO_CONSULTA}).</p>
{''.join(cx)}</section>""")

    # 8. o que fazer com isso
    corpo.append(f"""<section class="sec quebra"><div class="kicker">8 · O que fazer com isso</div><h2>O que os números significam para cada perfil</h2>
<p class="nota">Interpretação, não recomendação de compra, venda ou crédito. Cada bloco aponta o que observar a partir dos números deste estudo.</p>
{''.join(f'<div class="perfil"><h3>{e(t)}</h3><p>{e(x)}</p></div>' for t, x in perfis(d))}</section>""")

    # 9. o que o diagnóstico inclui
    corpo.append(f"""<section class="sec"><div class="kicker">9 · O que o diagnóstico completo inclui</div><h2>Do exemplo para a sua pergunta</h2>
<ul class="inclui">
<li><b>O seu recorte:</b> os produtos (por NCM), as origens, os estados e os portos que importam para você, em vez do grupo inteiro.</li>
<li><b>Seus preços contra a média do país:</b> você envia os preços que pagou (ou recebeu), e o estudo compara com a média do Comex Stat por NCM, origem e mês, com a mesma base (FOB ou CIF).</li>
<li><b>Planilha com todas as tabelas</b> e as consultas usadas, para refazer ou levar para o seu modelo.</li>
<li><b>Atualização mensal (Acompanhamento):</b> o mesmo recorte a cada nova base do Comex Stat, com os sinais revisados.</li>
<li><b>Conversa de apresentação</b>, se quiser, para discutir a leitura.</li></ul>
<p>Pedido em lcgalera.github.io/rotzx/pro; escopo, prazo e valor chegam por e-mail antes de qualquer compromisso.</p></section>""")

    # 10. fontes e método + apêndice
    citadas = sorted({p["ncm"] for p in d["produtos"]} | {x["ncm"] for x in d["dep_prod"]} | {x["ncm"] for x in d["mix_ncm"]})
    corpo.append(f"""<section class="sec quebra"><div class="kicker">Fontes e método</div><h2>Como este estudo foi feito</h2>
<p><b>Comex Stat (MDIC).</b> API pública (api-comexstat.mdic.gov.br, rota /general), importações, filtro pelas posições SH4 3101 a 3105, com detalhe mensal, valor FOB, peso líquido, frete, seguro e CIF. Três consultas por ano (2024, 2025 e 2026 até {mes_ult}): país × NCM, unidade da Receita × via, e UF. Dados coletados em {e(d['coleta'])}. Conferência: os totais das três consultas são iguais entre si em cada ano, e a soma dos 12 meses de 2025 por fornecedor é igual ao total anual publicado no atlas rotzx.</p>
<p><b>Pink Sheet (Banco Mundial).</b> World Bank Commodity Price Data, arquivo mensal CMO-Historical-Data-Monthly.xlsx ({e(d['ref_atualizado'] or 'sem arquivo')}), licença CC BY 4.0. Séries de ureia, DAP, TSP e cloreto de potássio, com as especificações da aba de descrição do próprio arquivo.</p>
<p><b>Volume × preço × mix.</b> Com Q = peso total, sᵢ = fatia da NCM no peso e pᵢ = US$/kg da NCM: volume = (Q₁ − Q₀) × preço médio₀; preço = Q₁ × Σ s₁ᵢ (p₁ᵢ − p₀ᵢ); mix = Q₁ × Σ (s₁ᵢ − s₀ᵢ) p₀ᵢ. A soma é exatamente a variação de valor, conferida no código. NCM sem registro no período base entra só no mix; valor sem peso registrado ficaria numa parcela à parte.</p>
<p><b>HHI e frete.</b> HHI = soma dos quadrados das participações (em %) no valor importado. Frete/t = frete declarado ÷ peso líquido.</p>
<p>Valores em dólares correntes, sem correção pela inflação. Dados do ano corrente podem ser revistos pela fonte. Ausência de registro aparece como “sem registro”, nunca como zero. Contexto de fornecimento: fontes citadas na seção 7.</p>
<h3>Descrições oficiais das NCMs citadas</h3>
<ol class="apendice">{''.join(f'<li><b>{c}</b> ({e(N.ncm(c, d["ncm_oficial"].get(c, c)))}): {e(d["ncm_oficial"].get(c, "sem registro"))}</li>' for c in citadas)}</ol>
<p class="aviso">rotzx Pro · lcgalera.github.io/rotzx/pro · Análise de dados públicos; não é recomendação de investimento ou de negócio. Licenças: Comex Stat (dados abertos do governo federal), Pink Sheet do Banco Mundial (CC BY 4.0).</p></section>""")
    return R.documento("rotzx Pro · Estudo-amostra: fertilizantes", "".join(corpo), CSS + ".url{word-break:break-all}")


def gerar(destino: Path = DESTINO, log=print) -> dict:
    if not referencia.ARQUIVO.exists():
        try:
            referencia.baixar(log=log)
        except Exception as erro:                                   # sem rede para o Banco Mundial: o estudo sai sem a seção
            log(f"  Pink Sheet indisponível ({erro}); a referência internacional fica de fora")
    d = calcular(log=log)
    R.pdf(html(d), destino)
    log(f"estudo-amostra: {destino}")
    from . import planilha
    planilha.gerar(d, PLANILHA)
    log(f"planilha: {PLANILHA}")
    R.miniaturas(destino, MINIATURAS, log=log)                         # D79: prévia real na página /pro/
    return d
