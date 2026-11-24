"""Estudo-amostra de exportação: "Para onde o Brasil vende café, e o que mudou em 2026" (D81).

Recorte: SH4 0901 (café cru, torrado e descafeinado, o mesmo item do atlas) mais o café solúvel e os extratos de café (NCMs 2101.11.x),
filtrados dentro da posição 2101, que também tem chá e mate. Só configuração e textos; o motor está em rotzx/pro/estudo.py.
"""
from typing import List

from .. import indicadores as ind
from .. import relatorio as R
from ..estudo import MESES, Recorte, sr
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
CONTEXTO = [
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


def extras(d, PN, UV, ytd, pais):
    """Dados dos sinais: preço mensal do café cru, volume do próximo mês e a parte dos EUA no café solúvel."""
    from ..estudo import _soma
    ult = d["ultimo_mes"]
    cru = next(p for p in d["produtos"] if p["ncm"] == "09011110")
    sol = lambda a, ms, eua: _soma(PN[a], meses=ms, filtro=lambda r: r["ncm"] == "21011110" and (not eua or pais(r["pais"]) == EUA))["fob"]
    parte = lambda a, ms: (sol(a, ms, True) / sol(a, ms, False)) if sol(a, ms, False) else None
    ac25, ac26 = d["cal_acum"][2025][ult], d["cal_acum"][2026][ult]
    d["sinais"].update({
        "cru_mes": cru["imp_mes26"][ult], "cru_media": cru["imp1"], "cru_jan": cru["imp_mes26"][1],
        "vol_virada": (d["vol_prox_25"] + ac25 - ac26) if d["vol_prox_25"] else None,
        "eua_sol_25": parte(2025, None), "eua_sol_ytd26": parte(2026, ytd), "eua_sol_mes": parte(2026, [ult]),
    })


def subtitulo(d):
    ry = d["ry"]
    return (f"Exportações brasileiras de café (cru, torrado, descafeinado e solúvel), {ry} de 2026 comparado com {ry} de 2025: volume, preço e mix, "
            f"preço por produto e destino, referência internacional, dependência, calendário de embarque, estados e portos.")


def fatos(d) -> List[str]:
    P, ry = d["per"], d["ry"]
    A, B = P["ytd25"], P["ytd26"]
    ta, tb = A["total"], B["total"]
    dec, dp = d["dec_total"], d["dp"]
    cru = next(p for p in d["produtos"] if p["ncm"] == "09011110")
    lo, hi = sorted(r["ref1"] for r in cru["refs"])
    return [
        f"De {ry} de 2026, o Brasil exportou {e(R.usd(tb['fob']))} em café ({e(R.ton(tb['kg']))}): {e(R.sinal_pct(ind.variacao(ta['fob'], tb['fob'])))} em valor e "
        f"{e(R.sinal_pct(ind.variacao(ta['kg'], tb['kg'])))} em volume sobre {ry} de 2025.",
        f"Da variação de valor ({e(R.sinal_usd(dec['variacao']))}), o preço dentro de cada NCM respondeu por {e(R.sinal_usd(dec['preco']))}, o volume por "
        f"{e(R.sinal_usd(dec['volume']))} e a mudança de composição (mix) por {e(R.sinal_usd(dec['mix']))}.",
        f"O café cru em grão, {e(R.pct(cru['parte1']))} do valor exportado, saiu a {e(R.usd_t(cru['imp1']))} em média ({e(R.sinal_pct(ind.variacao(cru['imp0'], cru['imp1'])))}), "
        f"entre as referências internacionais do robusta ({e(R.usd_t(lo))}) e do arábica ({e(R.usd_t(hi))}).",
        f"Os destinos são diversificados: os 3 maiores somaram {e(R.pct(B['tres']))} do valor exportado, e {e(B['rank'][0]['nome'])} foi o maior, com {e(R.pct(B['maior']))}; "
        f"{B['n']} países e territórios compraram café do Brasil no período.",
        f"{e(d['uf'][0]['nome'])} produziu {e(R.pct(d['uf'][0]['parte']))} do valor exportado, e {e(d['urf'][0]['nome'])} despachou {e(R.pct(d['urf'][0]['parte']))}.",
    ]


def leitura(d) -> List[str]:
    P, ry, dp, dec, s = d["per"], d["ry"], d["dp"], d["dec_total"], d["sinais"]
    cal, ult = d["cal"], d["ultimo_mes"]
    sol = next(p for p in d["produtos"] if p["ncm"] == "21011110")
    s1 = sum(cal[2026].get(m, 0) for m in range(1, 7)); s0 = sum(cal[2025].get(m, 0) for m in range(1, 7))
    t1 = sum(cal[2026].get(m, 0) for m in range(7, ult + 1)); t0 = sum(cal[2025].get(m, 0) for m in range(7, ult + 1))
    return [
        f"Em 2026, a receita do café caiu por preço, não por volume. O preço dentro de cada produto contribuiu com {R.sinal_pp(dp['preco'])} na variação "
        f"do preço médio, e a composição quase não mudou ({R.sinal_pp(dp['mix'])}); o volume embarcado em {ry} ficou perto do de 2025 "
        f"({R.sinal_pct(d['vol_gap'])}). Na prática, o Brasil vendeu quase a mesma quantidade por menos dinheiro.",
        f"O ano teve dois tempos: no primeiro semestre, os embarques ficaram {R.sinal_pct(ind.variacao(s0, s1))} abaixo de 2025; de julho a {MESES[ult - 1]}, "
        f"{R.sinal_pct(ind.variacao(t0, t1))} acima, com a safra nova. Ao mesmo tempo, o preço do café cru exportado caiu de {R.usd_t(s['cru_jan'])} em janeiro "
        f"para {R.usd_t(s['cru_mes'])} em {MESES[ult - 1]}, no ano em que o mercado esperava uma safra brasileira ampla (ver Contexto).",
        f"No café solúvel, que segue com tarifa adicional nos EUA, a parte dos americanos caiu de {R.pct(s['eua_sol_25'])} em 2025 para "
        f"{R.pct(s['eua_sol_ytd26'])} em {ry} de 2026, e o preço médio do solúvel exportado foi de {R.usd_t(sol['imp0'])} para {R.usd_t(sol['imp1'])}. "
        f"Os dados não provam que a tarifa causou a queda, mas o movimento acompanha a data da medida.",
    ]


def sinais(d) -> str:
    ry, ult, s = d["ry"], d["ultimo_mes"], d["sinais"]
    mes_ult, prox = MESES[ult - 1], (MESES[ult] if ult < 12 else "o próximo mês")
    return f"""<div class="sinais">
<div><b>1 · Preço do café cru</b>{e(mes_ult)}/2026: {e(R.usd_t(s['cru_mes']))} FOB (média de {ry}/2026: {e(R.usd_t(s['cru_media']))}).<span class="lim">Muda a leitura se: {prox}/2026 voltar acima da média do ano, interrompendo a queda que vem desde janeiro ({e(R.usd_t(s['cru_jan']))}).</span></div>
<div><b>2 · Volume do próximo mês</b>Acumulado de {ry}: {e(R.sinal_pct(s['vol_gap']))} sobre 2025.<span class="lim">Muda a leitura se: {prox}/2026 passar de {e(sr(s['vol_virada'], R.ton))}, o que deixaria o acumulado do ano acima do de 2025.</span></div>
<div><b>3 · EUA no café solúvel</b>Parte dos EUA no solúvel exportado: {e(sr(s['eua_sol_mes'], R.pct))} em {e(mes_ult)}/2026 ({e(sr(s['eua_sol_ytd26'], R.pct))} em {ry}).<span class="lim">Muda a leitura se: voltar a passar de {e(sr(s['eua_sol_25'], R.pct))}, a parte de 2025, sinal de que a tarifa deixou de pesar.</span></div></div>"""


def perfis(d) -> List[tuple]:
    B, s, ry = d["per"]["ytd26"], d["sinais"], d["ry"]
    cru = next(p for p in d["produtos"] if p["ncm"] == "09011110")
    lo, hi = sorted(r["ref1"] for r in cru["refs"])
    santos = d["urf"][0]
    return [
        ("Cooperativa ou produtor",
         f"O preço médio do café cru exportado ({R.usd_t(cru['imp1'])} em {ry}) ficou entre as referências do robusta ({R.usd_t(lo)}) e do arábica "
         f"({R.usd_t(hi)}). Comparar o próprio preço de venda com a média por NCM, destino e mês mostra se a cooperativa vendeu acima ou abaixo do "
         f"país no mesmo período, e se o calendário de venda acompanhou o de embarque (seção 5)."),
        ("Exportador ou trading",
         f"Com destinos diversificados (o maior, {B['rank'][0]['nome']}, teve {R.pct(B['maior'])}), a queda de receita veio de preço em quase todos eles "
         f"(seção 1). Para quem vende para a Europa, a aplicação da EUDR em dezembro de 2026 entra no planejamento de rastreabilidade (seção 7)."),
        ("Torrefação ou indústria de solúvel",
         f"O solúvel exportado perdeu espaço nos EUA ({R.pct(s['eua_sol_25'])} em 2025 para {R.pct(s['eua_sol_ytd26'])} em {ry}), único produto do "
         f"recorte que ficou fora da isenção americana. Acompanhar os destinos que compensaram essa queda (seção 2) ajuda a medir o tamanho da "
         f"diversificação."),
        ("Banco ou crédito agro",
         f"Receita menor com volume estável significa menos dinheiro por saca: o preço dentro de cada produto puxou {R.sinal_pp(d['dp']['preco'])} no "
         f"preço médio. Para a análise de crédito, o que conta é o preço de venda de cada cliente diante da média do país, e o calendário de "
         f"embarque, que mostra quando a receita entra; {santos['nome']} despachou {R.pct(santos['parte'])} do valor exportado."),
    ]


RECORTE = Recorte(
    slug="cafe", fluxo="exportacao", sh4=SH4, ncm_ok=NCM_OK, chaves=("pais_ncm", "urf_via_ncm", "uf_ncm"),
    titulo="Para onde o Brasil vende café, e o que mudou em 2026", subtitulo=subtitulo, fonte_comex=FONTE_COMEX,
    metodo_recorte=("API pública (api-comexstat.mdic.gov.br, rota /general), exportações, filtro pelas posições SH4 0901 e 2101, mantidas só as NCMs "
                    "0901.xx.xx e 2101.11.xx (café; ficam de fora chá, mate e seus extratos), com detalhe mensal, valor FOB e peso líquido. Três "
                    "consultas por ano (2024, 2025 e 2026 até {mes_ult}): país × NCM, unidade da Receita × via × NCM, e UF × NCM."),
    metodo_series="Séries de café arábica e robusta (indicadores da Organização Internacional do Café), convertidas de US$/kg para US$/t.",
    produtos=PRODUTOS, graficos=GRAFICOS_PRODUTO, contexto=CONTEXTO, contexto_consulta=CONTEXTO_CONSULTA,
    fatos=fatos, leitura=leitura, perfis=perfis, sinais=sinais, extras=extras,
    nota_preco="Base FOB (valor no embarque).",
    nota_ref=("Aproximação, não equivalência: a exportação brasileira é a média do que foi declarado no mês (contratos fechados antes, qualidades e "
              "portos variados), e as referências são indicadores da OIC com preço ex-dock em Nova York e na Europa, não FOB Brasil. A NCM do café cru "
              "em grão junta arábica e conilon (robusta), que têm preços muito diferentes; por isso a comparação é com a faixa entre as duas séries. "
              "Café solúvel e torrado não têm série no Pink Sheet."),
    nota_calendario="Os embarques acompanham a colheita, que no Brasil vai de abril a setembro, e a comercialização da safra nos meses seguintes.",
    kicker_calendario="Calendário de embarque",
    titulo_doc="rotzx Pro · Estudo-amostra: café",
    ancora=("a soma dos 12 meses de 2025 das NCMs 0901 é igual ao total anual do item 0901 (café) publicado no atlas rotzx; o café solúvel "
            "(2101.11) não faz parte desse item do atlas e foi somado aqui"),
)
