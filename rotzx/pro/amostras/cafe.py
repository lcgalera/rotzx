"""Estudo-amostra de exportação: "Quem paga mais pelo café brasileiro, e o que mudou em 2026" (D81).

Para cooperativas e produtores: preço por saca de 60 kg por destino (prêmio sobre a média do Brasil), por estado produtor (arábica ×
conilon, com a produção por espécie da Conab), mês a mês e no café solúvel. Recorte: SH4 0901 (café cru, torrado e descafeinado, o
mesmo item do atlas) mais as NCMs 2101.11 (café solúvel e extratos), filtradas dentro da 2101, que também tem chá e mate. O motor
está em rotzx/pro/estudo.py; aqui ficam a configuração, as seções próprias e os textos de interpretação.
"""
from typing import List

from .. import indicadores as ind
from .. import relatorio as R
from ..estudo import MESES, Recorte, sr, tabela
from ..relatorio import e

SH4 = ["0901", "2101"]
NCM_OK = lambda ncm: ncm.startswith("0901") or ncm.startswith("210111")
FONTE_COMEX = ("Fonte: Comex Stat (MDIC), dados abertos, exportações da posição SH4 0901 (café) e das NCMs 2101.11 (café solúvel e extratos), "
               "US$ correntes e kg líquido")
PRODUTOS = [
    ("09011110", ("arabica", "robusta"), "fob"),   # a NCM junta arábica e conilon: comparação com a faixa entre as duas séries
    ("21011110", None, "fob"),
    ("09012100", None, "fob"),
]
GRAFICOS_PRODUTO = ("09011110", "21011110")

SACA = 60.0
CRU = "09011110"
SOL = "21011110"
# Conab, 3º levantamento da safra de café 2026 (setembro de 2026), produção em mil sacas beneficiadas: (total, arábica, conilon)
CONAB = {"Minas Gerais": (35594.6, 34962.7, 631.9), "Espírito Santo": (16507.0, 4376.0, 12131.0), "São Paulo": (6192.0, 6192.0, 0.0),
         "Bahia": (4488.2, 1188.2, 3300.0), "Rondônia": (2876.3, 0.0, 2876.3), "Paraná": (724.1, 724.1, 0.0)}


def _agg(rows, chave, meses=None, filtro=None):
    out = {}
    for r in rows:
        if (meses and r["mes"] not in meses) or (filtro and not filtro(r)):
            continue
        s = out.setdefault(r[chave] if chave else "_", [0.0, 0.0])
        s[0] += r["fob"]; s[1] += r["kg"]
    return out


def ps(fob, kg):
    return fob / kg * SACA if kg else None


def extras(d, PN, UV, ytd, pais, UF=None):
    from ..referencia import serie
    ult = d["ultimo_mes"]
    cru = lambda r: r["ncm"] == CRU
    b0 = _agg(PN[2025], None, ytd, cru)["_"]; b1 = _agg(PN[2026], None, ytd, cru)["_"]
    d0, d1 = _agg(PN[2025], "pais", ytd, cru), _agg(PN[2026], "pais", ytd, cru)
    p_br0, p_br1 = ps(*b0), ps(*b1)
    dest = []
    for c, (f, kg) in d1.items():
        if kg < 0.01 * b1[1]:
            continue
        f0, kg0 = d0.get(c, (0, 0))
        p1, p0 = ps(f, kg), ps(f0, kg0)
        dest.append({"nome": pais(c), "chave": c, "sacas1": kg / SACA, "sacas0": kg0 / SACA, "parte_vol": kg / b1[1], "p1": p1, "p0": p0,
                     "premio": p1 / p_br1 - 1, "premio0": (p0 / p_br0 - 1) if p0 else None})
    dest.sort(key=lambda x: -x["premio"])
    # mês a mês (2025 e 2026): Brasil e os 4 maiores destinos em volume
    meses = [(a, m) for a in (2025, 2026) for m in range(1, 13) if not (a == 2026 and m > ult)]
    def mensal(filtro):
        out = []
        for a, m in meses:
            s = _agg(PN[a], None, [m], filtro).get("_")
            out.append(ps(*s) if s and s[1] else None)
        return out
    top_vol = sorted(dest, key=lambda x: -x["sacas1"])[:4]
    d["cafe_meses"] = meses
    d["cafe_br_mes"] = mensal(cru)
    d["cafe_dest_mes"] = [(x["nome"], mensal(lambda r, c=x["chave"]: cru(r) and r["pais"] == c)) for x in top_vol]
    acima = {x["nome"]: sum(1 for v, b in zip(s, d["cafe_br_mes"][12:]) if v and b and v > b) for x, (_, s) in zip(top_vol, [(n, s[12:]) for n, s in d["cafe_dest_mes"]])}
    # estados produtores
    ufs = []
    if UF:
        u0, u1 = _agg(UF[2025], "uf", ytd, cru), _agg(UF[2026], "uf", ytd, cru)
        tot = sum(kg for _, kg in u1.values())
        for c, (f, kg) in sorted(u1.items(), key=lambda kv: -kv[1][1]):
            if kg < 0.01 * tot:
                continue
            f0, kg0 = u0.get(c, (0, 0))
            ufs.append({"nome": c, "sacas1": kg / SACA, "parte_vol": kg / tot, "p1": ps(f, kg), "p0": ps(f0, kg0), "conab": CONAB.get(c)})
        anos_m = [(a, m) for a in (2024, 2025, 2026) for m in range(1, 13) if not (a == 2026 and m > ult)]
        def uf_mes(nome):
            out = []
            for a, m in anos_m:
                s = _agg(UF[a], None, [m], lambda r: cru(r) and r["uf"] == nome).get("_")
                out.append(ps(*s) if s and s[1] else None)
            return out
        ref, _ = serie()
        d["cafe_uf_meses"] = anos_m
        d["cafe_uf_mes"] = [("Minas Gerais", uf_mes("Minas Gerais")), ("Espírito Santo", uf_mes("Espírito Santo"))]
        d["cafe_ref_mes"] = [(n, [ref.get(k, {}).get(x) * SACA / 1000 if ref.get(k, {}).get(x) else None for x in anos_m]) for n, k in (("arábica (ref.)", "arabica"), ("robusta (ref.)", "robusta"))]
    d["cafe_ufs"] = ufs
    # quando vender: preço por saca de cada mês, por ano
    d["cafe_preco_ano"] = {a: {m: ps(*s) for m in range(1, 13) for s in [_agg(PN[a], None, [m], cru).get("_")] if s and s[1]} for a in (2024, 2025, 2026)}
    # para onde foi o volume (café cru): maiores ganhos e perdas em sacas
    todos = set(d0) | set(d1)
    mud = sorted(({"nome": pais(c), "ds": (d1.get(c, (0, 0))[1] - d0.get(c, (0, 0))[1]) / SACA, "s0": d0.get(c, (0, 0))[1] / SACA,
                   "s1": d1.get(c, (0, 0))[1] / SACA, "dv": d1.get(c, (0, 0))[0] - d0.get(c, (0, 0))[0]} for c in todos), key=lambda x: x["ds"])
    d["cafe_perdas"], d["cafe_ganhos"] = mud[:6], mud[::-1][:6]
    # solúvel por destino
    s0, s1 = _agg(PN[2025], "pais", ytd, lambda r: r["ncm"] == SOL), _agg(PN[2026], "pais", ytd, lambda r: r["ncm"] == SOL)
    t0, t1 = sum(v[0] for v in s0.values()), sum(v[0] for v in s1.values())
    d["cafe_sol"] = sorted(({"nome": pais(c), "parte1": v[0] / t1, "parte0": s0.get(c, (0, 0))[0] / t0, "p1": v[0] / v[1] if v[1] else None,
                             "kg1": v[1]} for c, v in s1.items()), key=lambda x: -x["parte1"])[:8]
    d["cafe"] = {"p_br0": p_br0, "p_br1": p_br1, "sacas0": b0[1] / SACA, "sacas1": b1[1] / SACA, "fob1": b1[0], "fob0": b0[0],
                 "destinos": dest, "acima": acima, "total_sacas1": sum(kg for _, kg in _agg(PN[2026], None, ytd).values()) / SACA}



CONTEXTO = [
    {"tema": "Safra brasileira 2026: recorde no arábica, menos conilon", "paises": [],
     "fato": "O 3º levantamento da Conab (setembro de 2026) estima a safra brasileira em 67,6 milhões de sacas beneficiadas (+19,6% sobre 2025): "
             "48,2 milhões de arábica (+34,8%) e 19,4 milhões de conilon (−6,6%). Minas Gerais responde por 35,6 milhões de sacas (98% arábica) "
             "e o Espírito Santo por 16,5 milhões (73% conilon).",
     "fontes": [("Conab, Acompanhamento da safra brasileira de café, 3º levantamento, safra 2026", "set/2026", "https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cafe/3o-levantamento-de-cafe-safra-2026/boletim-de-safras-cafe-set_26.pdf"),
                ("Canal Rural, “Safra de café de 2026 é estimada em 67,6 milhões de sacas, diz Conab”", "set/2026", "https://canalrural.com.br/agricultura/cafe/safra-de-cafe-de-2026-e-estimada-em-676-milhoes-de-sacas-diz-conab")]},
    {"tema": "Estados Unidos: tarifa adicional e isenção do café", "paises": ["Estados Unidos"],
     "fato": "Os EUA passaram a cobrar, a partir de agosto de 2025, uma tarifa adicional de 40% sobre produtos brasileiros, somada à tarifa de 10% "
             "aplicada antes. Uma ordem executiva de 20 de novembro de 2025 retirou o café e outros produtos agrícolas da tarifa (para mercadorias "
             "que entraram a partir de 13 de novembro). Segundo a associação da indústria brasileira de café solúvel, o café solúvel não entrou "
             "na lista de isenções.",
     "fontes": [("Daily Coffee News, “Trump order eliminates all tariffs on Brazilian coffee”", "21/11/2025", "https://dailycoffeenews.com/2025/11/21/trump-order-eliminates-all-tariffs-on-brazilian-coffee/"),
                ("Supply Chain Dive, “Trump exempts coffee, other food products from Brazil tariffs”", "nov/2025", "https://www.supplychaindive.com/news/trump-tariffs-us-exempts-coffee-food-products-brazil/806176/"),
                ("Global Coffee Report, “More than meets the eye to US-Brazil tariff removal”", "nov/2025", "https://www.gcrmag.com/more-than-meets-the-eye-to-us-brazil-tariff-removal")]},
    {"tema": "União Europeia: lei antidesmatamento (EUDR)", "paises": ["Alemanha", "Itália", "Bélgica", "Espanha", "Países Baixos"],
     "fato": "O Regulamento (UE) 2025/2650, publicado em dezembro de 2025, adiou mais uma vez a aplicação da lei europeia contra o desmatamento, "
             "que vale para o café: 30 de dezembro de 2026 para grandes operadores e comerciantes e 30 de junho de 2027 para pequenos e "
             "microempresas. A lei exige comprovar que o produto não vem de área desmatada depois de 2020.",
     "fontes": [("Comissão Europeia, Access2Markets, “Delay until December 2026 and other developments in the implementation of the EUDR Regulation”", "dez/2025", "https://trade.ec.europa.eu/access-to-markets/en/news/delay-until-december-2026-and-other-developments-implementation-eudr-regulation"),
                ("Daily Coffee News, “EU member states sign negotiating mandate to delay EUDR”", "24/11/2025", "https://dailycoffeenews.com/2025/11/24/eu-member-states-sign-negotiating-mandate-to-delay-eudr/")]},
    {"tema": "Cotações internacionais e safra brasileira 2026/27", "paises": [],
     "fato": "Relatórios de mercado e da Organização Internacional do Café ao longo de 2026 associaram a queda das cotações do arábica à expectativa de "
             "uma safra brasileira ampla em 2026/27; chuvas atrasaram a colheita no meio do ano e sustentaram os preços por algumas semanas.",
     "fontes": [("Tea & Coffee Trade Journal, “The ICO reports coffee prices rebound from lows in early June”", "2026", "https://www.teaandcoffee.net/news/39630/the-ico-reports-coffee-prices-rebound-from-lows-in-early-june/"),
                ("Nasdaq (Barchart), “Coffee Prices Sink on Expectations of a Record Brazil Coffee Crop”", "2026", "https://www.nasdaq.com/articles/coffee-prices-sink-expectations-record-brazil-coffee-crop")]},
]
CONTEXTO_CONSULTA = "24/11/2026"
EUA = "Estados Unidos"
FONTE_CONAB = "Conab, Acompanhamento da safra brasileira de café, 3º levantamento, safra 2026 (setembro de 2026)"


def sc(v):
    return "sem registro" if v is None else f"US$ {R.nf(v, 0)}/saca"


def sacas(n):
    if n is None:
        return "sem registro"
    return f"{R.nf(n / 1e6, 2)} mi sacas" if n >= 1e6 else f"{R.nf(n / 1e3, 0)} mil sacas"


GRUPOS = {"arábica": ("Minas Gerais", "São Paulo", "Paraná"), "conilon": ("Espírito Santo", "Rondônia")}   # pela produção por espécie da Conab
FERT = (("Cloreto de potássio (KCl)", "31042090"), ("Ureia", "31021010"))


def extras_todos(d, PN, UV, ytd, pais, UF=None):
    """extras() + D82: prêmio por tipo (destino × estado produtor), R$/saca pela PTAX e relação de troca com o fertilizante."""
    extras(d, PN, UV, ytd, pais, UF)
    from .. import cambio, coleta
    from ..estudo import ANOS, _soma
    from . import fertilizantes as F
    ult = d["ultimo_mes"]
    log = lambda *a: None
    # prêmio por tipo
    X = {a: [r for r in coleta.cruzado(a, "exportacao", "pais_uf_ncm", ["0901"], log=log) if r["ncm"] == CRU] for a in ANOS}
    tot1 = sum(r["kg"] for r in X[2026] if r["mes"] in ytd)
    tipos = {}
    for g, ufs in GRUPOS.items():
        s0, s1 = _agg(X[2025], "pais", ytd, lambda r: r["uf"] in ufs), _agg(X[2026], "pais", ytd, lambda r: r["uf"] in ufs)
        t0, t1 = [sum(v[i] for v in s0.values()) for i in (0, 1)], [sum(v[i] for v in s1.values()) for i in (0, 1)]
        m0, m1 = ps(*t0), ps(*t1)
        dest = []
        for c, (f, kg) in s1.items():
            if kg < 0.01 * t1[1]:
                continue
            f0, kg0 = s0.get(c, (0, 0))
            dest.append({"nome": pais(c), "chave": c, "sacas1": kg / SACA, "parte_vol": kg / t1[1], "p1": ps(f, kg), "premio": ps(f, kg) / m1 - 1,
                         "p0": ps(f0, kg0), "premio0": (ps(f0, kg0) / m0 - 1) if kg0 else None})
        dest.sort(key=lambda x: -x["premio"])
        # prêmio mês a mês (% sobre a média do grupo no mês) dos 4 maiores destinos do grupo
        meses = d["cafe_meses"]
        def premio_mes(c):
            out = []
            for a, m in meses:
                g_ = _agg(X[a], None, [m], lambda r: r["uf"] in ufs).get("_")
                x_ = _agg(X[a], None, [m], lambda r: r["uf"] in ufs and r["pais"] == c).get("_")
                out.append((ps(*x_) / ps(*g_) - 1) * 100 if x_ and x_[1] and g_ and g_[1] else None)
            return out
        top4 = sorted(dest, key=lambda x: -x["sacas1"])[:4]
        tipos[g] = {"ufs": ufs, "media0": m0, "media1": m1, "parte_total": t1[1] / tot1, "sacas1": t1[1] / SACA, "destinos": dest,
                    "mes": [(x["nome"], premio_mes(x["chave"])) for x in top4]}
    d["cafe_tipos"] = tipos
    d["cafe_x_ancora"] = {a: sum(r["fob"] for r in X[a]) for a in ANOS}
    # R$/saca pela PTAX (média mensal); o período é valorado mês a mês
    ptax, consulta = cambio.media_mensal(2024, 2026, log=log)
    d["ptax_consulta"] = consulta
    def rs(a, ms, filtro=lambda r: True):
        rows = [r for r in PN[a] if r["ncm"] == CRU and r["mes"] in ms and filtro(r)]
        kg = sum(r["kg"] for r in rows)
        if not kg or any((a, r["mes"]) not in ptax for r in rows):
            return None
        return sum(r["fob"] * ptax[(a, r["mes"])] for r in rows) / kg * SACA
    d["cafe_rs"] = {"ptax": ptax, "br0": rs(2025, ytd) if ptax else None, "br1": rs(2026, ytd) if ptax else None,
                    "br24": rs(2024, ytd) if ptax else None,
                    "ano": {a: {m: rs(a, [m]) for m in range(1, 13) if (a, m) in ptax and m in d["cafe_preco_ano"][a]} for a in ANOS} if ptax else {},
                    "ptax_ytd": {a: sum(ptax[(a, m)] for m in ytd) / len(ytd) for a in (2025, 2026)} if ptax else {}}
    if UF and ptax:
        for x in d["cafe_ufs"]:
            def rs_uf(a, nome=x["nome"]):
                rows = [r for r in UF[a] if r["ncm"] == CRU and r["mes"] in ytd and r["uf"] == nome]
                kg = sum(r["kg"] for r in rows)
                return sum(r["fob"] * ptax[(a, r["mes"])] for r in rows) / kg * SACA if kg else None
            x["r0"], x["r1"] = rs_uf(2025), rs_uf(2026)
    # relação de troca: sacas de café cru (US$/saca FOB) para pagar 1 t de fertilizante importado (US$/t CIF), mês a mês
    FP = {a: coleta.cruzado(a, "importacao", "pais_ncm", F.SH4, log=log) for a in ANOS}
    def cif_t(a, ncm, ms):
        rows = [r for r in FP[a] if r["ncm"] == ncm and r["mes"] in ms]
        kg = sum(r["kg"] for r in rows)
        return sum(r["cif"] or 0 for r in rows) / kg * 1000 if kg else None
    def cafe_saca(a, ms):
        s = _agg(PN[a], None, ms, lambda r: r["ncm"] == CRU).get("_")
        return ps(*s) if s and s[1] else None
    troca = {}
    for nome, ncm in FERT:
        def razao(a, ms):
            c, f = cafe_saca(a, ms), cif_t(a, ncm, ms)
            return f / c if c and f else None
        troca[nome] = {"ytd24": razao(2024, ytd), "ytd25": razao(2025, ytd), "ytd26": razao(2026, ytd),
                       "cif25": cif_t(2025, ncm, ytd), "cif26": cif_t(2026, ncm, ytd),
                       "mes": [razao(a, [m]) for a, m in d["cafe_uf_meses"]]}
    d["cafe_troca"] = troca
    # bienalidade: 2024 (também de alta bienalidade, segundo a Conab) no mesmo período
    s24 = _agg(PN[2024], None, ytd, lambda r: r["ncm"] == CRU).get("_")
    d["cafe"]["sacas24"], d["cafe"]["p_br24"] = s24[1] / SACA, ps(*s24)
    # sinais
    es = dict(zip(d["cafe_uf_meses"], d["cafe_uf_mes"][1][1]))
    rob = dict(zip(d["cafe_uf_meses"], d["cafe_ref_mes"][1][1]))
    sol = lambda a, ms, eua: _soma(PN[a], meses=ms, filtro=lambda r: r["ncm"] == SOL and (not eua or pais(r["pais"]) == EUA))["fob"]
    parte = lambda a, ms: (sol(a, ms, True) / sol(a, ms, False)) if sol(a, ms, False) else None
    kcl = troca[FERT[0][0]]
    d["sinais"].update({"preco_mes": d["cafe_preco_ano"][2026].get(ult), "preco_media": d["cafe"]["p_br1"],
                        "rs_mes": d["cafe_rs"]["ano"].get(2026, {}).get(ult), "rs_media": d["cafe_rs"]["br1"],
                        "es_mes": es.get((2026, ult)), "rob_mes": rob.get((2026, ult)),
                        "troca_mes": kcl["mes"][-1], "troca_ytd25": kcl["ytd25"],
                        "eua_sol_25": parte(2025, None), "eua_sol_ytd26": parte(2026, ytd), "eua_sol_mes": parte(2026, [ult])})


def _dest(d, nome, tipo=None):
    lista = d["cafe_tipos"][tipo]["destinos"] if tipo else d["cafe"]["destinos"]
    return next((x for x in lista if x["nome"] == nome), None)


def _uf(d, nome):
    return next((x for x in d["cafe_ufs"] if x["nome"] == nome), None)


def rsc(v):
    return "sem registro" if v is None else f"R$ {R.nf(v, 0)}/saca"


def subtitulo(d):
    ry = d["ry"]
    return (f"Para cooperativas e produtores: o prêmio que cada destino pagou pelo arábica e pelo conilon brasileiros, o preço por saca em dólar e "
            f"em real, quantas sacas pagam o adubo e o melhor momento de venda, {ry} de 2026 comparado com {ry} de 2025.")


def grandes(d) -> str:
    c, ry, r = d["cafe"], d["ry"], d["cafe_rs"]
    rs_txt = (f"<div><span>Em reais</span><b>{e(rsc(r['br1']))}</b><small>{e(R.sinal_pct(ind.variacao(r['br0'], r['br1'])))} sobre {ry}/2025 · PTAX do mês</small></div>"
              if r["br1"] else f"<div><span>Café cru exportado</span><b>{e(sacas(c['sacas1']))}</b><small>{e(R.sinal_pct(ind.variacao(c['sacas0'], c['sacas1'])))} sobre {ry}/2025</small></div>")
    return f"""<div class="grandes"><div><span>Preço médio do café cru</span><b>{e(sc(c['p_br1']))}</b><small>{e(R.sinal_pct(ind.variacao(c['p_br0'], c['p_br1'])))} sobre {ry}/2025 · FOB, saca de 60 kg</small></div>
{rs_txt}
<div><span>Café cru exportado</span><b>{e(sacas(c['sacas1']))}</b><small>{e(R.sinal_pct(ind.variacao(c['sacas0'], c['sacas1'])))} sobre {ry}/2025</small></div></div>"""


def fatos(d) -> List[str]:
    c, ry, dec, r, T = d["cafe"], d["ry"], d["dec_total"], d["cafe_rs"], d["cafe_tipos"]
    ar, co = T["arábica"], T["conilon"]
    kcl = d["cafe_troca"][FERT[0][0]]
    out = [
        f"De {ry} de 2026, o Brasil exportou {e(sacas(c['sacas1']))} de café cru a {e(sc(c['p_br1']))} em média ({e(R.sinal_pct(ind.variacao(c['p_br0'], c['p_br1'])))} "
        f"sobre {ry} de 2025). A queda de valor veio quase toda do preço ({e(R.sinal_usd(dec['preco']))}), não do volume ({e(R.sinal_usd(dec['volume']))}).",
    ]
    if r["br1"]:
        out.append(f"Em reais, pela PTAX de cada mês, a saca foi de {e(rsc(r['br0']))} para {e(rsc(r['br1']))} ({e(R.sinal_pct(ind.variacao(r['br0'], r['br1'])))}): "
                   f"a queda em real foi maior que em dólar porque a PTAX média caiu de {e(R.nf(r['ptax_ytd'][2025], 2))} para {e(R.nf(r['ptax_ytd'][2026], 2))}.")
    out += [
        f"No café dos estados de arábica (Minas Gerais, São Paulo e Paraná, {e(R.pct(ar['parte_total']))} do volume), a média foi {e(sc(ar['media1']))} e os prêmios "
        f"por destino ficaram entre {e(R.sinal_pct(min(x['premio'] for x in ar['destinos'])))} e {e(R.sinal_pct(max(x['premio'] for x in ar['destinos'])))}; "
        f"no dos estados de conilon (Espírito Santo e Rondônia, {e(R.pct(co['parte_total']))}), a média foi {e(sc(co['media1']))}.",
        f"Para pagar 1 t de cloreto de potássio importado foram necessárias {e(R.nf(kcl['ytd26'], 2))} sacas de café cru em {ry} de 2026, contra "
        f"{e(R.nf(kcl['ytd25'], 2))} em {ry} de 2025.",
    ]
    return out


def leitura(d) -> List[str]:
    c, r, T = d["cafe"], d["cafe_rs"], d["cafe_tipos"]
    ar, co = T["arábica"], T["conilon"]
    eua_a, ita_a = _dest(d, EUA, "arábica"), _dest(d, "Itália", "arábica")
    top_a, top_c = ar["destinos"][0], co["destinos"][0]
    mg, es = _uf(d, "Minas Gerais"), _uf(d, "Espírito Santo")
    kcl, ure = d["cafe_troca"][FERT[0][0]], d["cafe_troca"][FERT[1][0]]
    p = r["ano"].get(2026) or d["cafe_preco_ano"][2026]
    mx, mn = max(p, key=p.get), min(p, key=p.get)
    fmt = rsc if r["ano"] else sc
    return [
        f"Separando o arábica do conilon, a diferença entre destinos encolhe: no arábica, os prêmios ficaram em poucos pontos percentuais "
        f"({top_a['nome']} {R.sinal_pct(top_a['premio'])}, Itália {R.sinal_pct(ita_a['premio'])}) e os Estados Unidos, maior comprador, pagaram "
        f"{R.sinal_pct(eua_a['premio'])} em relação à média do grupo. Os descontos grandes que apareciam no café cru como um todo vinham, em boa parte, "
        f"da mistura de tipos. No conilon, a diferença é maior: {top_c['nome']} pagou {R.sinal_pct(top_c['premio'])} sobre a média.",
        f"Em reais, o ano foi pior do que em dólar. O café do Espírito Santo caiu {R.sinal_pct(ind.variacao(es.get('r0'), es.get('r1')) if es.get('r1') else ind.variacao(es['p0'], es['p1']))} "
        f"e o de Minas Gerais {R.sinal_pct(ind.variacao(mg.get('r0'), mg.get('r1')) if mg.get('r1') else ind.variacao(mg['p0'], mg['p1']))} por saca, e a saca "
        f"exportada foi de {fmt(p[mx])} em {MESES[mx - 1]} para {fmt(p[mn])} em {MESES[mn - 1]}.",
        f"O adubo ficou mais caro em café: 1 t de cloreto de potássio custou {R.nf(kcl['ytd26'], 2)} sacas (eram {R.nf(kcl['ytd25'], 2)}) e 1 t de ureia, "
        f"{R.nf(ure['ytd26'], 2)} sacas (eram {R.nf(ure['ytd25'], 2)}). Para quem compra insumo com o café da safra, a conta piorou ao longo do ano.",
    ]


def sinais(d) -> str:
    ry, ult, s = d["ry"], d["ultimo_mes"], d["sinais"]
    mes_ult, prox = MESES[ult - 1], (MESES[ult] if ult < 12 else "o próximo mês")
    p1 = (f"{e(mes_ult)}/2026: {e(rsc(s['rs_mes']))} (média de {ry}/2026: {e(rsc(s['rs_media']))})" if s.get("rs_mes")
          else f"{e(mes_ult)}/2026: {e(sc(s['preco_mes']))} (média de {ry}/2026: {e(sc(s['preco_media']))})")
    return f"""<div class="sinais">
<div><b>1 · Preço por saca, em reais</b>{p1}.<span class="lim">Muda a leitura se: {prox}/2026 voltar acima da média do ano, sinal de que o pior da safra passou.</span></div>
<div><b>2 · Sacas por tonelada de KCl</b>{e(mes_ult)}/2026: {e(sr(s['troca_mes'], lambda v: R.nf(v, 2)))} sacas (média de {ry}/2025: {e(sr(s['troca_ytd25'], lambda v: R.nf(v, 2)))}).<span class="lim">Muda a leitura se: voltar abaixo da média de 2025, sinal de que a relação de troca deixou de piorar.</span></div>
<div><b>3 · Conilon × referência</b>{e(mes_ult)}/2026: Espírito Santo a {e(sc(s['es_mes']))}; robusta (Pink Sheet) a {e(sc(s['rob_mes']))}.<span class="lim">Muda a leitura se: o café do Espírito Santo ficar abaixo da referência do robusta, o que indicaria desconto do conilon brasileiro.</span></div></div>"""


def _secao_tipo(n, tipo, d, fonte, quebra=True):
    T, ry = d["cafe_tipos"][tipo], d["ry"]
    itens = [(x["nome"], x["premio"], f"{R.sinal_pct(x['premio'])} · {sc(x['p1'])} · {R.pct(x['parte_vol'])} do vol.") for x in T["destinos"]]
    estados = " + ".join(T["ufs"])
    return f"""<section class="sec{' quebra' if quebra else ''}"><div class="kicker">{n} · Quem paga mais pelo {tipo}</div><h2>Prêmio de cada destino no café dos estados de {tipo}</h2>
<p>Só o café cru exportado de {estados} ({R.pct(T['parte_total'])} do volume de café cru de {ry}/2026). Média do grupo: <b>{e(sc(T['media1']))}</b> (era {e(sc(T['media0']))} em {ry}/2025). Entram os destinos com pelo menos 1% do volume do grupo.</p>
{R.divergente(itens)}
<p class="fonte">{fonte} Café cru em grão (NCM 0901.11.10) por destino e estado produtor. Prêmio = US$/saca do destino ÷ média do grupo − 1; “do vol.” = parte do destino no volume do grupo. Tabela completa, com o prêmio de {ry}/25, na planilha. Estados agrupados pela produção por espécie da Conab ({FONTE_CONAB}).</p></section>"""


def secoes(cfg, d) -> List[str]:
    c, ry, ult, r = d["cafe"], d["ry"], d["ultimo_mes"], d["cafe_rs"]
    fonte = f"{cfg.fonte_comex}. Coleta em {e(d['coleta'])}."
    fonte_ptax = (f"Câmbio: {e(__import__('rotzx.pro.cambio', fromlist=['FONTE']).FONTE)}, consulta em {e(d['ptax_consulta'])}." if d.get("ptax_consulta") else "")
    out = []
    # 1 e 2. quem paga mais, por tipo
    out.append(f"""<section class="sec quebra"><div class="kicker">Antes das tabelas</div><h2>Por que separar arábica e conilon</h2>
<p>A NCM do café cru (0901.11.10) junta arábica e conilon, que valem preços muito diferentes. Comparar destinos com todo o café misturado faz parecer que um país paga menos quando ele só compra mais conilon. O Comex Stat registra o estado produtor, e a Conab mede quanto cada estado produz de cada espécie: Minas Gerais, São Paulo e Paraná produzem 98% a 100% de arábica; Espírito Santo e Rondônia, 73% a 100% de conilon. Por isso as seções 1 e 2 comparam destinos dentro de cada grupo de estados. Bahia (produção mista) e os estados menores ficam fora das duas contas.</p>
<p class="nota">Ainda é aproximação: Minas Gerais também tem um pouco de conilon e o Espírito Santo, de arábica, e a NCM não informa qualidade nem certificação. O comparativo com todo o café cru, sem separar tipos, está na planilha (aba C1).</p></section>""")
    out[-1] = out[-1].replace('<section class="sec quebra">', '<section class="sec quebra">', 1)
    out.append(_secao_tipo(1, "arábica", d, fonte, quebra=False))
    out.append(_secao_tipo(2, "conilon", d, fonte))
    # 3. prêmio mês a mês no arábica (%)
    rot = [f"{a}/01" if m == 1 else MESES[m - 1] for a, m in d["cafe_meses"]]
    series = [(n, s, cor) for (n, s), cor in zip(d["cafe_tipos"]["arábica"]["mes"], (R.VERDE, R.OCRE, "#6E8FA8", "#9A7FB0"))]
    out.append(f"""<section class="sec"><div class="kicker">3 · O prêmio mês a mês</div><h2>Os 4 maiores compradores de arábica, em % sobre a média do mês</h2>
{R.linhas_mensais(series, rot, lambda v: R.nf(v, 0) + "%", altura=190)}
<p class="fonte">{fonte} Café cru dos estados de arábica (Minas Gerais, São Paulo e Paraná). Prêmio do mês = US$/saca do destino ÷ média do grupo no mesmo mês − 1; zero é a média. Meses sem registro ficam em branco.</p></section>""")
    # 4. arábica × conilon pelo estado produtor (US$ e R$)
    lu = []
    for x in d["cafe_ufs"]:
        cb = x["conab"]
        esp = f"{R.pct(cb[1] / cb[0])} / {R.pct(cb[2] / cb[0])}" if cb else "sem registro"
        lu.append([e(x["nome"]), esp, sacas(x["sacas1"]), sc(x["p1"]), R.sinal_pct(ind.variacao(x["p0"], x["p1"])), rsc(x.get("r1")),
                   R.sinal_pct(ind.variacao(x.get("r0"), x.get("r1"))) if x.get("r1") else "sem registro"])
    rot3 = [f"{a}/01" if m == 1 else MESES[m - 1] for a, m in d["cafe_uf_meses"]]
    s3 = [(n, s, cor) for (n, s), cor in zip(d["cafe_uf_mes"], (R.VERDE, R.OCRE))]
    s3 += [(n, s, cor, True) for (n, s), cor in zip(d["cafe_ref_mes"], (R.TINTA, R.NEG))]
    out.append(f"""<section class="sec"><div class="kicker">4 · Arábica × conilon</div><h2>Quanto vale o café de cada estado produtor</h2>
{tabela(['Estado', 'Arábica/conilon (Conab)', f'Volume {ry}/26', f'US$/saca {ry}/26', 'Var. US$', f'R$/saca {ry}/26', 'Var. R$'], lu, txt=(0,))}
<h3>Minas Gerais e Espírito Santo, mês a mês, com as referências internacionais (US$/saca)</h3>
{R.linhas_mensais(s3, rot3, lambda v: R.nf(v, 0), altura=170)}
<p class="fonte">{fonte} UF = estado produtor da mercadoria, como define o Comex Stat na exportação. Produção por espécie: {FONTE_CONAB}. Referências: Pink Sheet do Banco Mundial (CC BY 4.0), arábica e robusta (indicadores da OIC, ex-dock), convertidas para US$ por saca; aproximação, não equivalência com o FOB Brasil. {fonte_ptax} R$/saca = valor de cada mês × PTAX média do mês ÷ peso × 60 kg.</p></section>""")
    # 5. quando vender (US$ e R$) + bienalidade
    p, pr = d["cafe_preco_ano"], r["ano"]
    tem_rs = bool(pr)
    mel = {a: max(p[a], key=p[a].get) for a in p}
    graf_rs = (f"<h3>Em reais (R$/saca, PTAX média do mês)</h3>{R.linhas_ano(pr, lambda v: R.nf(v, 0), altura=160)}" if tem_rs else "")
    out.append(f"""<section class="sec quebra"><div class="kicker">5 · Quando vender</div><h2>O preço por saca ao longo do ano</h2>
<p>Mês de preço médio mais alto em dólar: {'; '.join(f"{a}, {MESES[m - 1]} ({sc(p[a][m])})" for a, m in mel.items())}. Em 2026, o preço caiu de fevereiro a agosto, enquanto os embarques da safra nova cresciam.</p>
<p class="nota"><b>Atenção:</b> o Comex Stat registra o mês do embarque, não o do contrato. Quem vende antecipado fixa o preço meses antes do embarque, então o mês de maior preço exportado não é necessariamente o melhor mês para fechar negócio.</p>
<h3>Em dólar (US$/saca)</h3>{R.linhas_ano(p, lambda v: R.nf(v, 0), altura=160)}
{graf_rs}
<p>2026 é ano de alta bienalidade, como 2024, segundo a Conab. No mesmo período de 2024, o Brasil exportou {e(sacas(c['sacas24']))} de café cru a {e(sc(c['p_br24']))}; em 2026, {e(sacas(c['sacas1']))} a {e(sc(c['p_br1']))}.</p>
<p class="fonte">{fonte} US$/saca de café cru exportado em cada mês (média de todos os destinos). {fonte_ptax} Bienalidade: {FONTE_CONAB} (“em comparação com a safra 2024, também de alta bienalidade”). Meses de 2026 ainda sem registro ficam em branco.</p></section>""")
    # 6. relação de troca
    tr = d["cafe_troca"]
    rot6 = [f"{a}/01" if m == 1 else MESES[m - 1] for a, m in d["cafe_uf_meses"]]
    s6 = [(n, t["mes"], cor) for (n, t), cor in zip(tr.items(), (R.VERDE, R.OCRE))]
    lt = [[e(n), R.nf(t["ytd24"], 2) if t["ytd24"] else "sem registro", R.nf(t["ytd25"], 2), R.nf(t["ytd26"], 2), R.sinal_pct(ind.variacao(t["ytd25"], t["ytd26"])),
           R.usd_t(t["cif26"])] for n, t in tr.items()]
    out.append(f"""<section class="sec"><div class="kicker">6 · Quantas sacas pagam o adubo</div><h2>Relação de troca: café cru × fertilizante importado</h2>
<p>Quantas sacas de café cru exportado (ao preço FOB médio do mês) pagam 1 tonelada de fertilizante importado (ao preço CIF médio do mês). Número maior = adubo mais caro em café. Liga este estudo ao estudo-amostra de fertilizantes.</p>
{tabela(['Fertilizante', f'Sacas por t {ry}/24', f'{ry}/25', f'{ry}/26', 'Variação 25 → 26', f'US$/t CIF {ry}/26'], lt)}
{R.linhas_mensais(s6, rot6, lambda v: R.nf(v, 1), altura=150)}
<p class="nota">Aproximação: o CIF no porto não é o preço do adubo na fazenda (frete interno, impostos e margem de revenda ficam de fora), e o FOB de exportação não é o preço que o produtor recebe. O indicador mostra a direção da relação, não o valor que cada produtor paga.</p>
<p class="fonte">{fonte} Fertilizantes: Comex Stat (MDIC), importações, NCM 3104.20.90 (KCl) e 3102.10.10 (ureia), US$ CIF ÷ peso líquido. Sacas por t = US$/t CIF ÷ US$/saca FOB do café cru, no mesmo período.</p></section>""")
    # 7. para onde foi o volume (compacto) + solúvel
    g = [[e(x["nome"]), sacas(x["s0"]), sacas(x["s1"]), ("+" if x["ds"] > 0 else "−") + sacas(abs(x["ds"]))] for x in d["cafe_ganhos"][:5]]
    pe = [[e(x["nome"]), sacas(x["s0"]), sacas(x["s1"]), ("+" if x["ds"] > 0 else "−") + sacas(abs(x["ds"]))] for x in d["cafe_perdas"][:5]]
    so = [[e(x["nome"]), R.pct(x["parte0"]), R.pct(x["parte1"]), R.sinal_pp(x["parte1"] - x["parte0"])] for x in d["cafe_sol"][:6]]
    solp = next(pp for pp in d["produtos"] if pp["ncm"] == SOL)
    out.append(f"""<section class="sec quebra"><div class="kicker">7 · Volume e café solúvel</div><h2>Para onde foi o café, e o solúvel diante da tarifa americana</h2>
<div class="grade2"><div><h3>Destinos que mais cresceram (café cru)</h3>{tabela(['Destino', f'{ry}/25', f'{ry}/26', 'Mudança'], g)}</div>
<div><h3>Destinos que mais caíram</h3>{tabela(['Destino', f'{ry}/25', f'{ry}/26', 'Mudança'], pe)}</div></div>
<p>O café solúvel foi {e(R.pct(solp['parte1']))} do valor exportado de café em {ry}/2026, a {e(R.usd_t(solp['imp1']))} em média ({e(R.sinal_pct(ind.variacao(solp['imp0'], solp['imp1'])))}), e é o único produto do recorte que ficou fora da isenção americana de novembro de 2025.</p>
{tabela(['Destino do solúvel', f'Parte {ry}/25', f'Parte {ry}/26', 'Mudança'], so)}
<p class="fonte">{fonte} Café cru em sacas de 60 kg; café solúvel (NCM 2101.11.10): parte = valor do destino ÷ valor total de solúvel exportado no período; mudança em p.p.</p></section>""")
    return out


def perfis(d) -> List[tuple]:
    c, r, T = d["cafe"], d["cafe_rs"], d["cafe_tipos"]
    ar, co = T["arábica"], T["conilon"]
    mg, es = _uf(d, "Minas Gerais"), _uf(d, "Espírito Santo")
    top_a = ", ".join(x["nome"] + " (" + R.sinal_pct(x["premio"]) + ")" for x in ar["destinos"][:3])
    top_c = ", ".join(x["nome"] + " (" + R.sinal_pct(x["premio"]) + ")" for x in co["destinos"][:3])
    kcl = d["cafe_troca"][FERT[0][0]]
    return [
        ("Cooperativa ou associação",
         f"No arábica, o prêmio por destino é de poucos pontos percentuais ({top_a}); no conilon, maior ({top_c}). Comparar o preço de venda da "
         f"cooperativa com a média do seu grupo de estados, por destino e mês (seções 1 a 3), mostra quanto desse prêmio chega a ela."),
        ("Produtor de arábica",
         f"O café de Minas Gerais saiu a {sc(mg['p1'])} ({R.sinal_pct(ind.variacao(mg['p0'], mg['p1']))} em dólar"
         + (f", {R.sinal_pct(ind.variacao(mg.get('r0'), mg.get('r1')))} em real)" if mg.get("r1") else ")")
         + f". Com a safra recorde de arábica estimada pela Conab, o momento da venda (seção 5) pesou mais que o destino, e o câmbio pesou contra."),
        ("Produtor de conilon",
         f"O café do Espírito Santo saiu a {sc(es['p1'])} ({R.sinal_pct(ind.variacao(es['p0'], es['p1']))} em dólar"
         + (f", {R.sinal_pct(ind.variacao(es.get('r0'), es.get('r1')))} em real)" if es.get("r1") else ")")
         + f", acompanhando o robusta no mercado internacional. O sinal 3 compara, mês a mês, esse preço com a referência."),
        ("Quem financia a safra",
         f"A relação de troca piorou: 1 t de cloreto de potássio custou {R.nf(kcl['ytd26'], 2)} sacas em média (eram {R.nf(kcl['ytd25'], 2)}). Com a "
         f"saca valendo menos em real, o produtor precisa de mais café para pagar o mesmo insumo, o que pesa no fluxo de caixa da próxima safra."),
    ]


def planilha_extra(d, aba):
    c, ry = d["cafe"], d["ry"]
    nota = "Fonte: Comex Stat (MDIC), exportações de café cru (NCM 0901.11.10), saca de 60 kg. Célula vazia = sem registro."
    aba("C1 Todo o café cru", f"Preço por saca por destino, todo o café cru (sem separar tipo), {ry}/2025 e {ry}/2026", nota + " Destinos com pelo menos 1% do volume.",
        ["Destino", f"Sacas {ry}/26", "Parte do volume", f"US$/saca {ry}/26", "Prêmio sobre a média", f"US$/saca {ry}/25", f"Prêmio {ry}/25"],
        [[x["nome"], x["sacas1"], x["parte_vol"], x["p1"], x["premio"], x["p0"], x["premio0"]] for x in c["destinos"]], pct=(3, 5, 7), usd=(2,))
    for tipo, T in d["cafe_tipos"].items():
        aba(f"C1 {tipo.capitalize()}", f"Prêmio por destino no café dos estados de {tipo} ({', '.join(T['ufs'])})", nota + f" Média do grupo: US$ {T['media1']:.0f}/saca.",
            ["Destino", f"Sacas {ry}/26", "Parte do volume do grupo", f"US$/saca {ry}/26", "Prêmio", f"Prêmio {ry}/25"],
            [[x["nome"], x["sacas1"], x["parte_vol"], x["p1"], x["premio"], x["premio0"]] for x in T["destinos"]], pct=(3, 5, 6), usd=(2,))
    aba("C2 Estados", f"Preço por saca por estado produtor, {ry}/2025 e {ry}/2026", nota + " Conab: " + FONTE_CONAB + ", mil sacas.",
        ["Estado", "Conab total", "Conab arábica", "Conab conilon", f"Sacas {ry}/26", f"US$/saca {ry}/25", f"US$/saca {ry}/26", f"R$/saca {ry}/25", f"R$/saca {ry}/26"],
        [[x["nome"], *(x["conab"] or (None, None, None)), x["sacas1"], x["p0"], x["p1"], x.get("r0"), x.get("r1")] for x in d["cafe_ufs"]], usd=(5,))
    aba("C3 Preço por mês", "US$/saca e R$/saca de café cru por mês", nota + " R$ pela PTAX média do mês (Banco Central).", ["Ano", "Moeda"] + MESES,
        [[a, "US$"] + [d["cafe_preco_ano"][a].get(m) for m in range(1, 13)] for a in sorted(d["cafe_preco_ano"])]
        + [[a, "R$"] + [d["cafe_rs"]["ano"].get(a, {}).get(m) for m in range(1, 13)] for a in sorted(d["cafe_rs"]["ano"])])
    aba("C4 Relação de troca", "Sacas de café cru por tonelada de fertilizante importado, por mês", nota + " Fertilizantes: Comex Stat, importações, US$ CIF.",
        ["Fertilizante"] + [f"{a}-{m:02d}" for a, m in d["cafe_uf_meses"]],
        [[n] + t["mes"] for n, t in d["cafe_troca"].items()])


RECORTE = Recorte(
    slug="cafe", fluxo="exportacao", sh4=SH4, ncm_ok=NCM_OK, chaves=("pais_ncm", "urf_via_ncm", "uf_ncm"),
    titulo="Quem paga mais pelo café brasileiro, e o que mudou em 2026", subtitulo=subtitulo, fonte_comex=FONTE_COMEX,
    metodo_recorte=("API pública (api-comexstat.mdic.gov.br, rota /general), exportações, filtro pelas posições SH4 0901 e 2101, mantidas só as NCMs "
                    "0901.xx.xx e 2101.11.xx (café; ficam de fora chá, mate e seus extratos), com detalhe mensal, valor FOB e peso líquido. Quatro "
                    "consultas por ano (2024, 2025 e 2026 até {mes_ult}): país × NCM, unidade da Receita × via × NCM, UF × NCM e país × UF × NCM. "
                    "Fertilizantes da seção 6: as consultas do estudo-amostra de fertilizantes. Saca = 60 kg."),
    metodo_series=("Séries de café arábica e robusta (indicadores da Organização Internacional do Café), convertidas de US$/kg para US$ por saca. "
                   "Produção por estado e espécie: " + FONTE_CONAB + ", gov.br/conab. Câmbio: PTAX de venda do Banco Central (olinda.bcb.gov.br), "
                   "média mensal das cotações diárias, dado aberto."),
    produtos=PRODUTOS, graficos=GRAFICOS_PRODUTO, contexto=CONTEXTO, contexto_consulta=CONTEXTO_CONSULTA,
    fatos=fatos, leitura=leitura, perfis=perfis, sinais=sinais, extras=extras_todos, secoes=secoes, grandes=grandes, planilha_extra=planilha_extra,
    perfis_titulo="O que os números significam para quem produz e vende café",
    nota_preco="Base FOB (valor no embarque).", nota_ref="", nota_calendario="",
    kicker_calendario="Calendário de embarque",
    titulo_doc="rotzx Pro · Estudo-amostra: café",
    ancora=("a soma dos 12 meses de 2025 das NCMs 0901 é igual ao total anual do item 0901 (café) publicado no atlas rotzx; o café solúvel "
            "(2101.11) não faz parte desse item do atlas e foi somado aqui"),
)
