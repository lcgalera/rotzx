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


def extras_todos(d, PN, UV, ytd, pais, UF=None):
    extras(d, PN, UV, ytd, pais, UF)
    from ..estudo import _soma
    ult = d["ultimo_mes"]
    sol = lambda a, ms, eua: _soma(PN[a], meses=ms, filtro=lambda r: r["ncm"] == SOL and (not eua or pais(r["pais"]) == EUA))["fob"]
    parte = lambda a, ms: (sol(a, ms, True) / sol(a, ms, False)) if sol(a, ms, False) else None
    es = dict(zip(d["cafe_uf_meses"], d["cafe_uf_mes"][1][1]))
    rob = dict(zip(d["cafe_uf_meses"], d["cafe_ref_mes"][1][1]))
    d["sinais"].update({"preco_mes": d["cafe_preco_ano"][2026].get(ult), "preco_media": d["cafe"]["p_br1"],
                        "es_mes": es.get((2026, ult)), "rob_mes": rob.get((2026, ult)),
                        "eua_sol_25": parte(2025, None), "eua_sol_ytd26": parte(2026, ytd), "eua_sol_mes": parte(2026, [ult])})


def _dest(d, nome):
    return next((x for x in d["cafe"]["destinos"] if x["nome"] == nome), None)


def _uf(d, nome):
    return next((x for x in d["cafe_ufs"] if x["nome"] == nome), None)


def subtitulo(d):
    ry = d["ry"]
    return (f"Para cooperativas e produtores: o preço por saca que cada destino pagou pelo café cru brasileiro, o prêmio sobre a média do país, "
            f"arábica × conilon pelo estado produtor e o melhor momento de venda, {ry} de 2026 comparado com {ry} de 2025.")


def grandes(d) -> str:
    c, ry, B, A = d["cafe"], d["ry"], d["per"]["ytd26"]["total"], d["per"]["ytd25"]["total"]
    return f"""<div class="grandes"><div><span>Preço médio do café cru</span><b>{e(sc(c['p_br1']))}</b><small>{e(R.sinal_pct(ind.variacao(c['p_br0'], c['p_br1'])))} sobre {ry}/2025 · FOB, saca de 60 kg</small></div>
<div><span>Café cru exportado</span><b>{e(sacas(c['sacas1']))}</b><small>{e(R.sinal_pct(ind.variacao(c['sacas0'], c['sacas1'])))} sobre {ry}/2025</small></div>
<div><span>Valor exportado (todo o café)</span><b>{e(R.usd(B['fob']))}</b><small>{e(R.sinal_pct(ind.variacao(A['fob'], B['fob'])))} sobre {ry}/2025 · US$ FOB</small></div></div>"""


def fatos(d) -> List[str]:
    c, ry, dec = d["cafe"], d["ry"], d["dec_total"]
    acima = [x for x in c["destinos"] if x["premio"] > 0]
    top = c["destinos"][0]
    ita = _dest(d, "Itália")
    mg, es = _uf(d, "Minas Gerais"), _uf(d, "Espírito Santo")
    p26 = d["cafe_preco_ano"][2026]
    mx, mn = max(p26, key=p26.get), min(p26, key=p26.get)
    return [
        f"De {ry} de 2026, o Brasil exportou {e(sacas(c['sacas1']))} de café cru a {e(sc(c['p_br1']))} em média ({e(R.sinal_pct(ind.variacao(c['p_br0'], c['p_br1'])))} "
        f"sobre {ry} de 2025). No total, com torrado e solúvel, foram {e(R.usd(d['per']['ytd26']['total']['fob']))}; a queda de valor veio quase toda do preço "
        f"({e(R.sinal_usd(dec['preco']))}), não do volume ({e(R.sinal_usd(dec['volume']))}).",
        f"Dos {len(c['destinos'])} destinos com pelo menos 1% do volume, {len(acima)} pagaram acima da média do Brasil. O maior prêmio foi de {e(top['nome'])} "
        f"({e(R.sinal_pct(top['premio']))}); entre os grandes compradores, a Itália pagou {e(R.sinal_pct(ita['premio']))} com {e(R.pct(ita['parte_vol']))} do volume.",
        f"Por estado produtor, o café de Minas Gerais saiu a {e(sc(mg['p1']))} ({e(R.sinal_pct(ind.variacao(mg['p0'], mg['p1'])))}) e o do Espírito Santo, de maioria conilon, "
        f"a {e(sc(es['p1']))} ({e(R.sinal_pct(ind.variacao(es['p0'], es['p1'])))}).",
        f"O preço médio por saca foi o mais alto em {MESES[mx - 1]} ({e(sc(p26[mx]))}) e o mais baixo em {MESES[mn - 1]} ({e(sc(p26[mn]))}).",
    ]


def leitura(d) -> List[str]:
    c = d["cafe"]
    ita, eua, ale, bel = _dest(d, "Itália"), _dest(d, EUA), _dest(d, "Alemanha"), _dest(d, "Bélgica")
    mg, es = _uf(d, "Minas Gerais"), _uf(d, "Espírito Santo")
    cru = next(p for p in d["produtos"] if p["ncm"] == CRU)
    ref = {r["serie"]: r for r in cru["refs"]}
    ganho = d["cafe_ganhos"][0]
    p26 = d["cafe_preco_ano"][2026]
    mx, mn = max(p26, key=p26.get), min(p26, key=p26.get)
    return [
        f"O prêmio pelo café brasileiro está em destinos menores e na Itália. Entre os grandes compradores, só a Itália pagou bem acima da média "
        f"({R.sinal_pct(ita['premio'])}); Estados Unidos ({R.sinal_pct(eua['premio'])}) e Alemanha ({R.sinal_pct(ale['premio'])}) ficaram perto dela. "
        f"A Bélgica, que mais aumentou as compras ({sacas(ganho['ds'])} a mais), pagou {R.sinal_pct(bel['premio'])}: volume crescendo com desconto. "
        f"Parte dessas diferenças vem do tipo de café que cada destino compra, não só do preço.",
        f"O conilon perdeu muito mais que o arábica. Pelo estado produtor, o café do Espírito Santo caiu {R.sinal_pct(ind.variacao(es['p0'], es['p1']))} por saca "
        f"e o de Minas Gerais, {R.sinal_pct(ind.variacao(mg['p0'], mg['p1']))}, acompanhando as referências internacionais (robusta "
        f"{R.sinal_pct(ind.variacao(ref['robusta']['ref0'], ref['robusta']['ref1']))}, arábica {R.sinal_pct(ind.variacao(ref['arabica']['ref0'], ref['arabica']['ref1']))}), "
        f"mesmo com a safra de conilon menor segundo a Conab.",
        f"O calendário pesou: o preço médio por saca caiu de {sc(p26[mx])} em {MESES[mx - 1]} para {sc(p26[mn])} em {MESES[mn - 1]}, e os embarques "
        f"cresceram justamente no segundo semestre, com a safra nova. Quem vendeu cedo pegou o preço mais alto do ano; quem embarcou na safra, o mais baixo.",
    ]


def sinais(d) -> str:
    ry, ult, s = d["ry"], d["ultimo_mes"], d["sinais"]
    mes_ult, prox = MESES[ult - 1], (MESES[ult] if ult < 12 else "o próximo mês")
    return f"""<div class="sinais">
<div><b>1 · Preço por saca</b>{e(mes_ult)}/2026: {e(sc(s['preco_mes']))} (média de {ry}/2026: {e(sc(s['preco_media']))}).<span class="lim">Muda a leitura se: {prox}/2026 voltar acima da média do ano, sinal de que o pior da safra passou.</span></div>
<div><b>2 · Conilon × referência</b>{e(mes_ult)}/2026: Espírito Santo a {e(sc(s['es_mes']))}; robusta (Pink Sheet) a {e(sc(s['rob_mes']))}.<span class="lim">Muda a leitura se: o café do Espírito Santo ficar abaixo da referência do robusta, o que indicaria desconto do conilon brasileiro.</span></div>
<div><b>3 · EUA no café solúvel</b>Parte dos EUA no solúvel exportado: {e(sr(s['eua_sol_mes'], R.pct))} em {e(mes_ult)}/2026 ({e(sr(s['eua_sol_ytd26'], R.pct))} em {ry}).<span class="lim">Muda a leitura se: voltar a passar de {e(sr(s['eua_sol_25'], R.pct))}, a parte de 2025, sinal de que a tarifa deixou de pesar.</span></div></div>"""


def secoes(cfg, d) -> List[str]:
    c, ry, ult = d["cafe"], d["ry"], d["ultimo_mes"]
    fonte = f"{cfg.fonte_comex}. Coleta em {e(d['coleta'])}."
    out = []
    # 1. quem paga mais
    itens = [(x["nome"], x["premio"], f"{R.sinal_pct(x['premio'])} · {sc(x['p1'])}") for x in c["destinos"]]
    lin = [[e(x["nome"]), sacas(x["sacas1"]), R.pct(x["parte_vol"]), sc(x["p1"]), R.sinal_pct(x["premio"]), sc(x["p0"]),
            sr(x["premio0"], R.sinal_pct)] for x in c["destinos"]]
    out.append(f"""<section class="sec quebra"><div class="kicker">1 · Quem paga mais</div><h2>O preço por saca que cada destino pagou pelo café cru</h2>
<p>Média do Brasil em {ry}/2026: <b>{e(sc(c['p_br1']))}</b> (era {e(sc(c['p_br0']))} em {ry}/2025). A barra mostra quanto cada destino pagou acima ou abaixo dessa média. Entram os destinos com pelo menos 1% do volume de café cru exportado.</p>
{R.divergente(itens)}
<p class="nota">Preço por destino mistura preço e tipo de café: a NCM do café cru junta arábica e conilon, e destino que compra mais conilon (mais barato) aparece abaixo da média sem necessariamente pagar menos pelo mesmo café.</p>
{tabela(['Destino', f'Volume {ry}/26', 'Parte do volume', f'US$/saca {ry}/26', 'Prêmio sobre a média', f'US$/saca {ry}/25', f'Prêmio {ry}/25'], lin)}
<p class="fonte">{fonte} Café cru em grão (NCM 0901.11.10). US$/saca = valor FOB ÷ peso líquido × 60 kg. Média do Brasil = valor ÷ peso de todo o café cru exportado no período. Parte do volume = peso do destino ÷ peso total exportado.</p></section>""")
    # 2. prêmio mês a mês
    rot = [f"{a}/01" if m == 1 else MESES[m - 1] for a, m in d["cafe_meses"]]
    series = [(n, s, cor) for (n, s), cor in zip(d["cafe_dest_mes"], (R.VERDE, R.OCRE, "#6E8FA8", "#9A7FB0"))]
    series.append(("Média do Brasil", d["cafe_br_mes"], R.TINTA, True))
    acima = "; ".join(f"{e(n)}: {k} de {ult}" for n, k in c["acima"].items())
    out.append(f"""<section class="sec"><div class="kicker">2 · O prêmio mês a mês</div><h2>Os 4 maiores compradores contra a média do Brasil</h2>
{R.linhas_mensais(series, rot, lambda v: R.nf(v, 0), altura=190)}
<p>Meses de 2026 em que o destino pagou acima da média do Brasil: {acima}.</p>
<p class="fonte">{fonte} US$/saca de café cru por mês; os 4 maiores destinos em volume de {ry}/2026. Meses sem registro ficam em branco.</p></section>""")
    # 3. arábica × conilon pelo estado produtor
    lu = []
    for x in d["cafe_ufs"]:
        cb = x["conab"]
        esp = f"{R.pct(cb[1] / cb[0])} / {R.pct(cb[2] / cb[0])}" if cb else "sem registro"
        lu.append([e(x["nome"]), esp, sacas(x["sacas1"]), R.pct(x["parte_vol"]), sc(x["p0"]), sc(x["p1"]), R.sinal_pct(ind.variacao(x["p0"], x["p1"]))])
    rot3 = [f"{a}/01" if m == 1 else MESES[m - 1] for a, m in d["cafe_uf_meses"]]
    s3 = [(n, s, cor) for (n, s), cor in zip(d["cafe_uf_mes"], (R.VERDE, R.OCRE))]
    s3 += [(n, s, cor, True) for (n, s), cor in zip(d["cafe_ref_mes"], (R.TINTA, R.NEG))]
    out.append(f"""<section class="sec quebra"><div class="kicker">3 · Arábica × conilon</div><h2>Quanto vale o café de cada estado produtor</h2>
<p>O Comex Stat não separa arábica e conilon na NCM, mas registra o estado produtor. Com a produção por espécie da Conab, o estado vira uma aproximação do tipo: Minas Gerais e São Paulo produzem quase só arábica; Espírito Santo, Rondônia e o sul da Bahia, conilon.</p>
{tabela(['Estado produtor', 'Conab 2026: arábica / conilon', f'Volume {ry}/26', 'Parte do volume', f'US$/saca {ry}/25', f'US$/saca {ry}/26', 'Variação'], lu, txt=(0, 1))}
<h3>Minas Gerais e Espírito Santo, mês a mês, com as referências internacionais (US$/saca)</h3>
{R.linhas_mensais(s3, rot3, lambda v: R.nf(v, 0), altura=180)}
<p class="fonte">{fonte} UF = estado produtor da mercadoria, como define o Comex Stat na exportação. Produção por espécie: {FONTE_CONAB}, em mil sacas beneficiadas. Referências: Pink Sheet do Banco Mundial (CC BY 4.0), arábica e robusta (indicadores da OIC, ex-dock em Nova York e na Europa), convertidas para US$ por saca de 60 kg; são aproximação, não equivalência com o FOB Brasil.</p></section>""")
    # 4. quando vender
    p = d["cafe_preco_ano"]
    melhores = {a: max(p[a], key=p[a].get) for a in p}
    out.append(f"""<section class="sec quebra"><div class="kicker">4 · Quando vender</div><h2>O preço por saca ao longo do ano</h2>
<p>Mês de preço médio mais alto: {'; '.join(f"{a}, {MESES[m - 1]} ({sc(p[a][m])})" for a, m in melhores.items())}. Em 2026, o preço caiu de janeiro até agosto, enquanto os embarques da safra nova cresciam (seção de calendário na planilha).</p>
{R.linhas_ano(p, lambda v: R.nf(v, 0))}
<p class="fonte">{fonte} US$/saca de café cru exportado em cada mês (média de todos os destinos). Meses de 2026 ainda sem registro (depois de {MESES[ult - 1]}) ficam em branco. Em Minas Gerais, a colheita de 2026 começou em abril, segundo a Conab.</p></section>""")
    # 5. para onde foi o volume
    g = [[e(x["nome"]), sacas(x["s0"]), sacas(x["s1"]), ("+" if x["ds"] > 0 else "−") + sacas(abs(x["ds"])), R.sinal_usd(x["dv"])] for x in d["cafe_ganhos"]]
    pe = [[e(x["nome"]), sacas(x["s0"]), sacas(x["s1"]), ("+" if x["ds"] > 0 else "−") + sacas(abs(x["ds"])), R.sinal_usd(x["dv"])] for x in d["cafe_perdas"]]
    out.append(f"""<section class="sec"><div class="kicker">5 · Para onde foi o volume</div><h2>Os destinos que mais compraram e os que mais deixaram de comprar</h2>
<h3>Cresceram</h3>{tabela(['Destino', f'{ry}/25', f'{ry}/26', 'Mudança', 'Mudança de valor'], g)}
<h3>Caíram</h3>{tabela(['Destino', f'{ry}/25', f'{ry}/26', 'Mudança', 'Mudança de valor'], pe)}
<p class="fonte">{fonte} Café cru em grão, sacas de 60 kg.</p></section>""")
    # 6. solúvel
    so = [[e(x["nome"]), R.pct(x["parte0"]), R.pct(x["parte1"]), R.sinal_pp(x["parte1"] - x["parte0"]), sr(x["p1"], lambda v: f"US$ {R.nf(v, 2)}/kg")] for x in d["cafe_sol"]]
    solp = next(p for p in d["produtos"] if p["ncm"] == SOL)
    out.append(f"""<section class="sec quebra"><div class="kicker">6 · Café solúvel</div><h2>O café industrializado e a tarifa americana</h2>
<p>O café solúvel foi {e(R.pct(solp['parte1']))} do valor exportado de café em {ry}/2026, a {e(R.usd_t(solp['imp1']))} em média ({e(R.sinal_pct(ind.variacao(solp['imp0'], solp['imp1'])))}). É o único produto do recorte que ficou fora da isenção americana de novembro de 2025 (seção de contexto).</p>
{tabela(['Destino', f'Parte {ry}/25', f'Parte {ry}/26', 'Mudança', f'US$/kg {ry}/26'], so)}
<p class="fonte">{fonte} Café solúvel (NCM 2101.11.10). Parte = valor do destino ÷ valor total de solúvel exportado no período; mudança em p.p.</p></section>""")
    return out


def perfis(d) -> List[tuple]:
    c = d["cafe"]
    mg, es, ro = _uf(d, "Minas Gerais"), _uf(d, "Espírito Santo"), _uf(d, "Rondônia")
    top3 = c["destinos"][:3]
    ita = _dest(d, "Itália")
    p26 = d["cafe_preco_ano"][2026]
    mx, mn = max(p26, key=p26.get), min(p26, key=p26.get)
    lista_top = ", ".join(x["nome"] + " (" + R.sinal_pct(x["premio"]) + ")" for x in top3)
    return [
        ("Cooperativa ou associação",
         f"O prêmio está concentrado: {lista_top} e a Itália ({R.sinal_pct(ita['premio'])}, com "
         f"{R.pct(ita['parte_vol'])} do volume) pagaram acima da média de {sc(c['p_br1'])}. Comparar o preço de venda da cooperativa com a média por destino e "
         f"mês (seções 1 e 2) mostra quanto desse prêmio chega a ela e para quem vale direcionar os lotes de melhor qualidade."),
        ("Produtor de arábica",
         f"O café de Minas Gerais saiu a {sc(mg['p1'])} em média ({R.sinal_pct(ind.variacao(mg['p0'], mg['p1']))}), queda bem menor que a do conilon, com "
         f"a Conab estimando safra recorde de arábica. Com mais café no mercado, a diferença entre vender cedo ou na safra (de {sc(p26[mx])} em "
         f"{MESES[mx - 1]} para {sc(p26[mn])} em {MESES[mn - 1]}) pesou mais que o destino."),
        ("Produtor de conilon",
         f"O café do Espírito Santo saiu a {sc(es['p1'])} ({R.sinal_pct(ind.variacao(es['p0'], es['p1']))}) e o de Rondônia a {sc(ro['p1']) if ro else 'sem registro'}, "
         f"acompanhando a queda do robusta no mercado internacional. O sinal 2 do resumo compara, mês a mês, o preço do Espírito Santo com a "
         f"referência: abaixo dela, o conilon brasileiro estaria saindo com desconto."),
        ("Quem financia a safra",
         f"Receita por saca menor com volume estável: o preço médio do café cru caiu {R.sinal_pct(ind.variacao(c['p_br0'], c['p_br1']))}. Para a análise de "
         f"crédito, contam o preço de venda de cada cliente diante da média do país e do seu estado, e o mês em que a receita entra (seção 4)."),
    ]


def planilha_extra(d, aba):
    c, ry = d["cafe"], d["ry"]
    nota = "Fonte: Comex Stat (MDIC), exportações de café cru (NCM 0901.11.10), saca de 60 kg. Célula vazia = sem registro."
    aba("C1 Quem paga mais", f"Preço por saca por destino, {ry}/2025 e {ry}/2026", nota + " Destinos com pelo menos 1% do volume.",
        ["Destino", f"Sacas {ry}/26", "Parte do volume", f"US$/saca {ry}/26", "Prêmio sobre a média", f"US$/saca {ry}/25", f"Prêmio {ry}/25"],
        [[x["nome"], x["sacas1"], x["parte_vol"], x["p1"], x["premio"], x["p0"], x["premio0"]] for x in c["destinos"]], pct=(3, 5, 7), usd=(2,))
    aba("C2 Estados", f"Preço por saca por estado produtor, {ry}/2025 e {ry}/2026", nota + " Conab: " + FONTE_CONAB + ", mil sacas.",
        ["Estado", "Conab total", "Conab arábica", "Conab conilon", f"Sacas {ry}/26", f"US$/saca {ry}/25", f"US$/saca {ry}/26"],
        [[x["nome"], *(x["conab"] or (None, None, None)), x["sacas1"], x["p0"], x["p1"]] for x in d["cafe_ufs"]], usd=(5,))
    aba("C3 Preço por mês", "US$/saca de café cru por mês", nota, ["Ano"] + MESES,
        [[a] + [d["cafe_preco_ano"][a].get(m) for m in range(1, 13)] for a in sorted(d["cafe_preco_ano"])])


RECORTE = Recorte(
    slug="cafe", fluxo="exportacao", sh4=SH4, ncm_ok=NCM_OK, chaves=("pais_ncm", "urf_via_ncm", "uf_ncm"),
    titulo="Quem paga mais pelo café brasileiro, e o que mudou em 2026", subtitulo=subtitulo, fonte_comex=FONTE_COMEX,
    metodo_recorte=("API pública (api-comexstat.mdic.gov.br, rota /general), exportações, filtro pelas posições SH4 0901 e 2101, mantidas só as NCMs "
                    "0901.xx.xx e 2101.11.xx (café; ficam de fora chá, mate e seus extratos), com detalhe mensal, valor FOB e peso líquido. Três "
                    "consultas por ano (2024, 2025 e 2026 até {mes_ult}): país × NCM, unidade da Receita × via × NCM, e UF × NCM. Saca = 60 kg."),
    metodo_series=("Séries de café arábica e robusta (indicadores da Organização Internacional do Café), convertidas de US$/kg para US$ por saca. "
                   "Produção por estado e espécie: " + FONTE_CONAB + ", gov.br/conab."),
    produtos=PRODUTOS, graficos=GRAFICOS_PRODUTO, contexto=CONTEXTO, contexto_consulta=CONTEXTO_CONSULTA,
    fatos=fatos, leitura=leitura, perfis=perfis, sinais=sinais, extras=extras_todos, secoes=secoes, grandes=grandes, planilha_extra=planilha_extra,
    perfis_titulo="O que os números significam para quem produz e vende café",
    nota_preco="Base FOB (valor no embarque).", nota_ref="", nota_calendario="",
    kicker_calendario="Calendário de embarque",
    titulo_doc="rotzx Pro · Estudo-amostra: café",
    ancora=("a soma dos 12 meses de 2025 das NCMs 0901 é igual ao total anual do item 0901 (café) publicado no atlas rotzx; o café solúvel "
            "(2101.11) não faz parte desse item do atlas e foi somado aqui"),
)
