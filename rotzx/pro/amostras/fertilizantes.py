"""Estudo-amostra de importação: "De quem o Brasil compra fertilizantes, e o que mudou em 2026" (D77, D80; motor em D81).

Só a configuração e os textos de interpretação deste recorte; o cálculo, o HTML e a planilha estão em rotzx/pro/estudo.py.
"""
from typing import List

from ...mundo import produtos_nomes
from .. import indicadores as ind
from .. import relatorio as R
from ..estudo import MESES, Recorte, sr
from ..relatorio import e

SH4 = produtos_nomes.GRUPOS["g-fertilizantes"]["sh4"]          # 3101 a 3105, o mesmo grupo do atlas
FONTE_COMEX = ("Fonte: Comex Stat (MDIC), dados abertos, importações das posições SH4 3101 a 3105 (capítulo 31: adubos e fertilizantes), "
               "US$ correntes e kg líquido")
# produtos analisados um a um e a série do Pink Sheet mais próxima; a base de preço da importação acompanha a da referência
PRODUTOS = [
    ("31042090", ("kcl",), "cif"),    # Pink Sheet: CFR Brasil → comparado com o CIF por tonelada da importação
    ("31021010", ("ureia",), "fob"),  # FOB Oriente Médio
    ("31054000", ("dap",), "fob"),    # não há série de MAP: DAP (FOB Golfo dos EUA) como referência mais próxima
    ("31022100", None, "fob"),        # sem série no Pink Sheet
    ("31031100", ("tsp",), "fob"),    # TSP, importação no Golfo dos EUA
    ("31031900", None, "fob"),        # sem série no Pink Sheet
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


def extras(d, PN, UV, ytd, pais):
    """O que só este estudo usa: o que mais mudou no que a China vende (explica o mix dela) e os dados dos sinais."""
    from ..estudo import _soma
    oficial = d["ncm_oficial"]
    from .. import nomes as N
    c0 = ind.por_item(PN[2025], "ncm", ytd, lambda r: r["pais"] == "China")
    c1 = ind.por_item(PN[2026], "ncm", ytd, lambda r: r["pais"] == "China")
    d["china_ncm"] = sorted(({"nome": N.ncm(k, oficial.get(k, k)), "kg0": c0.get(k, (0, 0))[1], "kg1": c1.get(k, (0, 0))[1]}
                             for k in set(c0) | set(c1)), key=lambda x: -abs(x["kg1"] - x["kg0"]))[:4]
    ult = d["ultimo_mes"]
    ureia = next(p for p in d["produtos"] if p["ncm"] == "31021010")
    d["sinais"].update({"frete_atual": d["frete_mes"][2026][ult], "frete_max25": max(d["frete_mes"][2025].values()),
                        "frete_ytd25": d["per"]["ytd25"]["frete_t"], "ureia_imp": ureia["imp_mes26"][ult], "ureia_ref": ureia["ref_mes26"].get(ult)})


def subtitulo(d):
    ry = d["ry"]
    return (f"Importações brasileiras de adubos e fertilizantes (SH4 3101 a 3105), {ry} de 2026 comparado com {ry} de 2025: volume, preço e mix, "
            f"preço por produto e origem, dependência, calendário de compra, portos e frete.")


def fatos(d) -> List[str]:
    P, ry = d["per"], d["ry"]
    A, B = P["ytd25"], P["ytd26"]
    ta, tb = A["total"], B["total"]
    dec, dp = d["dec_total"], d["dp"]
    sa = next(x for x in d["dep_prod"] if x["ncm"] == "31022100")
    return [
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


def sinais(d) -> str:
    ry, ult, s = d["ry"], d["ultimo_mes"], d["sinais"]
    mes_ult = MESES[ult - 1]
    vol_lim = R.ton(s["vol_prox_25"]) if s["vol_prox_25"] else "sem registro"
    return f"""<div class="sinais">
<div><b>1 · Frete por tonelada</b>{e(MESES[ult - 1])}/2026: {e(R.usd_t(s['frete_atual']))} (média de {ry}/2025: {e(R.usd_t(s['frete_ytd25']))}).<span class="lim">Muda a leitura se: voltar a ficar abaixo de {e(R.usd_t(s['frete_max25']))}, o maior valor mensal de 2025, indicando alívio logístico.</span></div>
<div><b>2 · Volume do próximo mês</b>Acumulado de {ry}: {e(R.sinal_pct(s['vol_gap']))} sobre 2025.<span class="lim">Muda a leitura se: {MESES[ult] if ult < 12 else 'o próximo mês'}/2026 passar de {e(vol_lim)} (o mesmo mês de 2025), primeiro sinal de compra adiada, não perdida.</span></div>
<div><b>3 · Ureia × referência</b>{e(mes_ult)}/2026: importada a {e(R.usd_t(s['ureia_imp']))} FOB; Pink Sheet (FOB Oriente Médio) a {e(sr(s['ureia_ref'], R.usd_t))}.<span class="lim">Muda a leitura se: a importada ficar acima da referência por dois meses seguidos, o que indicaria prêmio sobre o mercado internacional.</span></div></div>"""


def nota_via(d) -> str:
    ae, ry, ult = d["aerea"], d["ry"], d["ultimo_mes"]
    mes_ult = MESES[ult - 1]
    return (f'<p class="nota">* Via aérea provavelmente registrada por engano. Em {ry} de 2026 a via “aérea” somou {e(R.usd(ae["fob"]))} ({e(R.ton(ae["kg"]))}), '
            f'contra {e(R.usd(ae["fob_2025"]))} em todo o ano de 2025. Desse total, {e(R.pct(ae["fob_porto"] / ae["fob"]))} do valor foi desembaraçado em unidades '
            f'da Receita de portos marítimos, em lotes de milhares de toneladas, incompatíveis com transporte aéreo, e o volume cresce mês a mês '
            f'({e(R.ton(ae["kg_mes"][1]))} em janeiro, {e(R.ton(ae["kg_mes"][ult]))} em {mes_ult}). Mantemos o dado como a fonte publica; as análises de '
            f'porto e frete usam a unidade da Receita, que não depende da via.</p>')


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




RECORTE = Recorte(
    slug="fertilizantes", fluxo="importacao", sh4=SH4,
    titulo="De quem o Brasil compra fertilizantes, e o que mudou em 2026", subtitulo=subtitulo, fonte_comex=FONTE_COMEX,
    metodo_recorte=("API pública (api-comexstat.mdic.gov.br, rota /general), importações, filtro pelas posições SH4 3101 a 3105, com detalhe mensal, "
                    "valor FOB, peso líquido, frete, seguro e CIF. Três consultas por ano (2024, 2025 e 2026 até {mes_ult}): país × NCM, unidade da "
                    "Receita × via, e UF."),
    metodo_series="Séries de ureia, DAP, TSP e cloreto de potássio, com as especificações da aba de descrição do próprio arquivo.",
    produtos=PRODUTOS, graficos=GRAFICOS_PRODUTO, contexto=CONTEXTO, contexto_consulta=CONTEXTO_CONSULTA,
    fatos=fatos, leitura=leitura, perfis=perfis, sinais=sinais, extras=extras, nota_via=nota_via,
    nota_preco="Base FOB (valor no embarque), exceto no cloreto de potássio, em CIF (com frete e seguro), para comparar com a referência CFR Brasil.",
    nota_ref=("Aproximação, não equivalência: a importação brasileira é a média do que foi declarado no mês (contratos fechados antes, especificações e "
              "portos variados), e a referência é uma cotação spot de um mercado específico. Base de cada comparação: KCl em CIF do Brasil × CFR Brasil; "
              "ureia, MAP e superfosfato em FOB da origem × FOB ou importação no mercado da série. O MAP é comparado com o DAP, a série mais próxima "
              "disponível. Rocha fosfática (Pink Sheet) não entra: é a posição 2510, fora do capítulo 31."),
    nota_calendario="As compras para a safra de verão costumam se concentrar no segundo semestre, como mostram 2024 e 2025.",
    titulo_doc="rotzx Pro · Estudo-amostra: fertilizantes",
)
