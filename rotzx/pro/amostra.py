"""Estudo-amostra do rotzx Pro: "De quem o Brasil compra fertilizantes, e o que mudou em 2026" (D77).

`python -m rotzx pro-amostra` coleta (com cache), calcula e grava prototipos/globo/pro/estudo-fertilizantes.pdf.
Todos os números saem da coleta; o único texto escrito à mão é a "Leitura do analista" (LEITURA, abaixo), marcada como
interpretação no relatório e revisada pelo dono antes de publicar.
"""
import json
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

from ..mundo import codigos, detalhe_coleta, historia, produtos_nomes
from . import coleta
from . import indicadores as ind
from . import relatorio as R
from .relatorio import e

SH4 = produtos_nomes.GRUPOS["g-fertilizantes"]["sh4"]          # 3101 a 3105, o mesmo grupo do atlas
FLUXO = "importacao"
ANOS = [2024, 2025, 2026]
MINIATURAS = (1, 4)                                                   # capa e a página dos maiores fornecedores (gráfico)
DESTINO = historia.SAIDA.parent / "pro" / "estudo-fertilizantes.pdf"
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

# Interpretação: rascunho do Claude a partir dos números calculados em calcular(); o dono revisa antes de publicar.
LEITURA: List[str] = [
    "O Brasil está comprando menos fertilizante e pagando mais por tonelada. De janeiro a outubro de 2026, o volume importado "
    "caiu 14,7% e o preço médio subiu 12,6% em relação ao mesmo período de 2025; como um efeito compensa parte do outro, o valor "
    "caiu só 3,9%. Os dados de comércio não dizem o motivo da queda de volume: estoques, calendário de safra e preço são "
    "explicações possíveis, a conferir nos próximos meses.",
    "A queda de volume vem de dois fornecedores: China (de 9,74 para 6,64 milhões de toneladas) e Rússia (de 9,73 para 7,11). "
    "Somadas, essas reduções são maiores que a do grupo inteiro, porque outros países aumentaram as vendas ao Brasil.",
    "Com isso, a concentração diminuiu: os 3 maiores fornecedores passaram de 55,9% para 49,1% do valor importado. Turcomenistão "
    "(de 0,4% para 5,4%) e Marrocos (de 8,2% para 11,2%) foram os que mais ganharam espaço. Para quem compra, o mercado "
    "brasileiro de fertilizantes está recebendo de mais origens, o que pede acompanhar preço e prazo de fornecedores novos.",
    "A entrada segue concentrada em poucos portos: Santos, Paranaguá e Rio Grande somaram 60,8% do valor importado no período.",
]


def _nomes_paises() -> Dict[str, str]:
    """Nome do país no Comex Stat → nome usado no atlas (via iso_num); o que não casa fica como na fonte."""
    ponte = detalhe_coleta._ponte(codigos.carregar())
    H = json.loads((historia.SAIDA / "historia.json").read_text(encoding="utf-8"))
    return {nome: H["paises"][iso]["nome"] for nome, iso in ponte.items() if iso in H["paises"]}, ponte, H


def calcular(rec: Optional[dict] = None, log=print) -> dict:
    rec = rec or coleta.recorte(ANOS, FLUXO, SH4, log=log)
    nomes, ponte, H = _nomes_paises()
    ultimo = max(x["mes"] for x in rec["pais"][2026]) if rec["pais"].get(2026) else 12
    ytd = list(range(1, ultimo + 1))
    per = {"2024": (2024, None), "2025": (2025, None), "ytd25": (2025, ytd), "ytd26": (2026, ytd)}
    out: dict = {"ultimo_mes": ultimo, "rotulo_ytd": f"jan–{MESES[ultimo - 1]}", "periodos": {}, "coleta": date.today().isoformat()}
    for k, (ano, meses) in per.items():
        bloco = {}
        for nivel in coleta.NIVEIS:
            ag = ind.agregar(rec[nivel][ano], meses)
            if nivel == "pais":                                    # nome do atlas para os países
                for c, d in ag.items():
                    d["nome"] = nomes.get(c, d["nome"])
            tot = ind.total(ag)
            bloco[nivel] = {"total": tot, "rank": ind.ranking(ag, tot["fob"])}
        bloco["preco_t"] = ind.preco_t(bloco["pais"]["total"]["fob"], bloco["pais"]["total"]["kg"])
        bloco["dep"] = ind.dependencia(bloco["pais"]["rank"])
        out["periodos"][k] = bloco
    # mudanças no mesmo período (jan–último mês de 2025 × 2026), por fornecedor
    a, b = out["periodos"]["ytd25"]["pais"], out["periodos"]["ytd26"]["pais"]
    ia = {x["chave"]: x for x in a["rank"]}
    mud = []
    for x in b["rank"][:12]:
        y = ia.get(x["chave"])
        pv = ind.preco_volume(y["fob"], y["kg"], x["fob"], x["kg"]) if y else None
        mud.append({"nome": x["nome"], "fob0": y["fob"] if y else None, "fob1": x["fob"], "kg0": y["kg"] if y else None, "kg1": x["kg"],
                    "parte0": y["parte"] if y else None, "parte1": x["parte"], "pp": ind.pp(y["parte"] if y else None, x["parte"]),
                    "p0": y["preco_t"] if y else None, "p1": x["preco_t"], "efeito_volume": pv[0] if pv else None, "efeito_preco": pv[1] if pv else None})
    out["mudancas"] = mud
    out["mensal"] = ind.mensal(rec["pais"])
    # contexto dos 3 maiores fornecedores no período mais recente: só o que o atlas já tem
    ctx = []
    for x in b["rank"][:3]:
        iso = ponte.get(x["chave"])
        if not iso:
            continue
        u = (H["onu"]["paises"].get(iso) or [])
        ult_onu = next(((H["onu"]["inicio"] + i, v) for i in range(len(u) - 1, -1, -1) for v in [u[i]] if v is not None), None)
        w = H["omc"].get(iso) or {}
        k = H["conflitos"]["paises"].get(iso) or {}
        eco = {z["id"]: z for z in (H["economia"].get(iso) or [])}
        ctx.append({"nome": x["nome"], "onu": ult_onu, "omc": len(w.get("casos", [])), "omc_ue": w.get("via_ue", False),
                    "conf": k.get(str(H["conflitos"]["fim"])), "conf_fim": H["conflitos"]["fim"], "pib": eco.get("NY.GDP.MKTP.CD")})
    out["contexto"] = ctx
    return out


def _tabela(cab: List[str], linhas: List[List[str]], txt=(0,)) -> str:
    """`txt`: colunas de texto (alinhadas à esquerda e com quebra de linha); as outras são números."""
    cl = lambda i: ' class="txt"' if i in txt else ""
    th = "".join(f"<th{cl(i)}>{e(c)}</th>" for i, c in enumerate(cab))
    return f"<table><thead><tr>{th}</tr></thead><tbody>{''.join('<tr>' + ''.join(f'<td{cl(i)}>{c}</td>' for i, c in enumerate(l)) + '</tr>' for l in linhas)}</tbody></table>"


def html(d: dict) -> str:
    P, ry = d["periodos"], d["rotulo_ytd"]
    p24, p25, a, b = P["2024"], P["2025"], P["ytd25"], P["ytd26"]
    tot = lambda p: p["pais"]["total"]
    fonte = "Fonte: Comex Stat (MDIC), importações, SH4 3101 a 3105 (capítulo 31: adubos e fertilizantes), US$ FOB correntes e kg líquido."
    corpo = []
    # 1. capa
    corpo.append(f"""<section class="capa"><div><div class="marca">rotzx</div><p class="sub" style="margin-top:4pt">Pro · análise sob demanda com dados públicos e oficiais</p></div>
<div><span class="selo">Estudo-amostra</span><h1 style="margin-top:12pt">De quem o Brasil compra fertilizantes, e o que mudou em 2026</h1>
<p class="sub">Importações brasileiras de adubos e fertilizantes (SH4 3101 a 3105): fornecedores, preço e volume, estados e portos de entrada, de 2024 a {MESES[d['ultimo_mes'] - 1]}/2026.</p></div>
<div><p class="nota">Exemplo do formato de um diagnóstico do rotzx Pro, com dados reais. Dados coletados em {e(d['coleta'])}. Análise de dados públicos; não é recomendação de investimento ou de negócio.</p>
<p class="nota">lcgalera.github.io/rotzx/pro</p></div></section>""")
    # 2. resumo
    t25, ta, tb = tot(p25), tot(a), tot(b)
    fatos = [
        f"Em 2025, o Brasil importou {e(R.usd(t25['fob']))} em fertilizantes ({e(R.ton(t25['kg']))}), a um preço médio de {e(R.usd_t(p25['preco_t']))}.",
        f"De {ry} de 2026, foram {e(R.usd(tb['fob']))} ({e(R.ton(tb['kg']))}): {e(R.sinal_pct(ind.variacao(ta['fob'], tb['fob'])))} em valor e "
        f"{e(R.sinal_pct(ind.variacao(ta['kg'], tb['kg'])))} em volume sobre o mesmo período de 2025; o preço médio foi de {e(R.usd_t(a['preco_t']))} para {e(R.usd_t(b['preco_t']))}.",
        f"O maior fornecedor de {ry}/2026 foi {e(b['pais']['rank'][0]['nome'])}, com {e(R.pct(b['dep']['maior']))} do valor importado; os 3 maiores somaram {e(R.pct(b['dep']['tres']))}, "
        f"e {b['dep']['n']} países e territórios venderam ao Brasil no período.",
        f"{e(b['uf']['rank'][0]['nome'])} foi o estado com a maior parte do valor importado ({e(R.pct(b['uf']['rank'][0]['parte']))}), "
        f"e {e(R.nome_urf(b['urf']['rank'][0]['nome']))} foi a unidade da Receita com a maior parte ({e(R.pct(b['urf']['rank'][0]['parte']))}).",
    ]
    leitura = "".join(f"<p>{e(x)}</p>" for x in LEITURA) or "<p><i>(a escrever)</i></p>"
    corpo.append(f"""<section class="sec quebra"><div class="kicker">Resumo</div><h2>O que os números mostram</h2>{''.join(f'<p>{x}</p>' for x in fatos)}
<div class="leitura"><div class="kicker">Leitura do analista</div>{leitura}<p class="nota" style="margin:0">Interpretação, separada dos fatos acima.</p></div>
<p class="fonte">{fonte} Participações sobre o total importado do grupo no período.</p></section>""")
    # 3. quanto
    lin = []
    for rot, p in ((f"2024", p24), ("2025", p25), (f"{ry} 2025", a), (f"{ry} 2026", b)):
        t = tot(p)
        lin.append([rot, R.usd(t["fob"]), R.ton(t["kg"]), R.usd_t(p["preco_t"]), str(t["n"])])
    corpo.append(f"""<section class="sec"><div class="kicker">1 · Quanto o Brasil importa</div><h2>Valor, volume e preço médio</h2>
<div class="kpis"><div class="kpi"><span>Valor, {ry} 2026</span><b>{e(R.usd(tb['fob']))}</b><small>{e(R.sinal_pct(ind.variacao(ta['fob'], tb['fob'])))} sobre {ry} 2025</small></div>
<div class="kpi"><span>Volume, {ry} 2026</span><b>{e(R.ton(tb['kg']))}</b><small>{e(R.sinal_pct(ind.variacao(ta['kg'], tb['kg'])))} sobre {ry} 2025</small></div>
<div class="kpi"><span>Preço médio, {ry} 2026</span><b>{e(R.usd_t(b['preco_t']))}</b><small>{e(R.sinal_pct(ind.variacao(a['preco_t'], b['preco_t'])))} sobre {ry} 2025</small></div></div>
{_tabela(['Período', 'Valor (US$ FOB)', 'Volume', 'Preço médio', 'Fornecedores'], lin)}
<p class="fonte">{fonte} Preço médio = valor ÷ peso líquido do período (média do grupo; mistura produtos de preços diferentes).</p></section>""")
    # 4. de quem
    top = b["pais"]["rank"][:12]
    corpo.append(f"""<section class="sec quebra"><div class="kicker">2 · De quem o Brasil compra</div><h2>Maiores fornecedores, {ry} 2026</h2>
<p class="nota">Barra: parte de cada país no valor total importado do grupo de {ry} de 2026 ({e(R.usd(tb['fob']))}), de 0 a 100%.</p>
{R.barras([(x['nome'], x['parte'], f"{R.pct(x['parte'])} · {R.usd(x['fob'])}") for x in top])}
{_tabela(['Fornecedor', f'Parte {ry} 2025', f'Parte {ry} 2026', 'Mudança'], [[e(m['nome']), R.pct(m['parte0']) if m['parte0'] is not None else 'sem registro', R.pct(m['parte1']), R.sinal_pp(m['pp'])] for m in d['mudancas']])}
<p class="fonte">{fonte} Parte = valor importado do país ÷ total importado do grupo no mesmo período. Mudança em pontos percentuais (p.p.).</p></section>""")
    # 5. preço x volume
    corpo.append(f"""<section class="sec"><div class="kicker">3 · Preço × volume</div><h2>De onde veio a mudança de valor, por fornecedor</h2>
<p>A variação de valor de cada fornecedor entre {ry} de 2025 e de 2026 se divide em duas partes que somam exatamente a variação: o efeito volume (mais ou menos toneladas, ao preço de 2025) e o efeito preço (diferença de preço médio, sobre as toneladas de 2026).</p>
{_tabela(['Fornecedor', 'Volume 2025 → 2026', 'Preço médio 2025 → 2026', 'Efeito volume', 'Efeito preço'], [[e(m['nome']), f"{R.ton(m['kg0'])} → {R.ton(m['kg1'])}", f"{R.usd_t(m['p0'])} → {R.usd_t(m['p1'])}", R.sinal_usd(m['efeito_volume']), R.sinal_usd(m['efeito_preco'])] for m in d['mudancas'][:8]])}
<p class="fonte">{fonte} Períodos: {ry} de cada ano. Sem registro num dos anos, os efeitos não são calculados.</p></section>""")
    # 6. dependência
    corpo.append(f"""<section class="sec"><div class="kicker">4 · Dependência</div><h2>Concentração dos fornecedores</h2>
{_tabela(['Período', 'Maior fornecedor', 'Parte do maior', 'Parte dos 3 maiores', 'Países com registro'], [[rot, e(p['pais']['rank'][0]['nome']), R.pct(p['dep']['maior']), R.pct(p['dep']['tres']), str(p['dep']['n'])] for rot, p in (('2024', p24), ('2025', p25), (f'{ry} 2026', b))])}
<p class="fonte">{fonte} Partes sobre o valor total importado do grupo em cada período. Concentração alta indica dependência de poucos fornecedores, não um juízo sobre eles.</p></section>""")
    # 7. por onde entra
    corpo.append(f"""<section class="sec quebra"><div class="kicker">5 · Por onde entra</div><h2>Estados e portos, {ry} 2026</h2>
<h3>Estados (UF)</h3>{R.barras([(x['nome'], x['parte'], f"{R.pct(x['parte'])} · {R.ton(x['kg'])}") for x in b['uf']['rank'][:10]], cor=R.OCRE)}
<h3>Unidades da Receita (portos, aeroportos e fronteiras)</h3>{_tabela(['Unidade', 'Valor', 'Volume', 'Parte'], [[e(R.nome_urf(x['nome'])), R.usd(x['fob']), R.ton(x['kg']), R.pct(x['parte'])] for x in b['urf']['rank'][:10]])}
<h3>Vias</h3>{_tabela(['Via', 'Valor', 'Parte'], [[e(x['nome'].capitalize()), R.usd(x['fob']), R.pct(x['parte'])] for x in b['via']['rank'][:5]])}
<p class="fonte">{fonte} UF e unidade da Receita como registradas pelo Comex Stat para cada importação. Partes sobre o valor total importado do grupo no período.</p></section>""")
    # 8. produtos (NCM)
    corpo.append(f"""<section class="sec"><div class="kicker">6 · Quais fertilizantes</div><h2>Os itens (NCM) com maior valor, {ry} 2026</h2>
{_tabela(['NCM', 'Descrição oficial', 'Valor', 'Volume', 'Parte'], [[e(x['chave']), e(x['nome'][:95] + ('…' if len(x['nome']) > 95 else '')), R.usd(x['fob']), R.ton(x['kg']), R.pct(x['parte'])] for x in b['ncm']['rank'][:10]], txt=(0, 1))}
<p class="fonte">{fonte} Descrição oficial da NCM, como no Comex Stat.</p></section>""")
    # 9. mês a mês
    m = d["mensal"]
    rot = [f"{MESES[mm - 1]}/{str(aa)[2:]}" if mm != 1 else f"{aa}/01" for aa, mm, *_ in m]
    corpo.append(f"""<section class="sec quebra"><div class="kicker">7 · Mês a mês</div><h2>Volume importado por mês, 2024–{MESES[d['ultimo_mes'] - 1]}/2026</h2>
{R.linhas_mensais([('mil toneladas', [k / 1e6 for *_, k in m], R.VERDE)], rot, lambda v: R.nf(v, 0))}
<h2 style="margin-top:12pt">Valor importado por mês</h2>
{R.linhas_mensais([('US$ milhões FOB', [f / 1e6 for _, _, f, _ in m], R.OCRE)], rot, lambda v: R.nf(v, 0))}
<p class="fonte">{fonte} Meses sem registro ficam em branco.</p></section>""")
    # 10. contexto
    cx = []
    for c in d["contexto"]:
        onu = f"{round(c['onu'][1] * 100)} de 100 ({c['onu'][0]})" if c["onu"] else "sem votação"
        conf = c["conf"]
        conf_txt = ("guerra no território" if conf and conf.get("t", 0) >= 2 else "conflito no território" if conf and conf.get("t") else "nenhum no território") if conf is not None else "nenhum registro"
        pib = f"{R.usd(c['pib']['valor'])} ({c['pib']['ano']})" if c["pib"] else "sem dado"
        cx.append([e(c["nome"]), onu, f"{c['omc']}{' (pela UE)' if c['omc_ue'] else ''}", f"{conf_txt} ({c['conf_fim']})", pib])
    corpo.append(f"""<section class="sec"><div class="kicker">8 · Contexto dos maiores fornecedores</div><h2>O que o atlas rotzx mostra sobre eles</h2>
{_tabela(['País', 'ONU: concordância com o Brasil', 'OMC: disputas com o Brasil desde 1995', 'Conflito armado', 'PIB'], cx, txt=(0, 3))}
<p class="fonte">Votos na ONU: Voeten, Strezhnev e Bailey (Harvard Dataverse, CC0). OMC: lista oficial de disputas. Conflitos: UCDP/PRIO (CC BY 4.0). PIB: Banco Mundial (CC BY 4.0), valor mais recente. Contexto, não nota de risco.</p></section>""")
    # 11. método
    corpo.append(f"""<section class="sec"><div class="kicker">Fontes e método</div><h2>Como este estudo foi feito</h2>
<p>Consultas à API pública do Comex Stat (api-comexstat.mdic.gov.br, rota /general) com detalhe mensal, valor FOB e peso líquido, filtro pelas posições SH4 3101, 3102, 3103, 3104 e 3105 e detalhe por país, UF, unidade da Receita, via e NCM, para 2024, 2025 e 2026 (até {MESES[d['ultimo_mes'] - 1]}). Dados coletados em {e(d['coleta'])}.</p>
<p>Conferência: a soma dos 12 meses de 2025 por fornecedor é igual ao total anual publicado no atlas rotzx para o mesmo grupo.</p>
<p>Valores em dólares correntes, sem correção pela inflação. Dados do ano corrente podem ser revistos pela fonte. Ausência de registro aparece como "sem registro", nunca como zero.</p>
<p class="aviso">rotzx Pro · lcgalera.github.io/rotzx/pro · Análise de dados públicos; não é recomendação de investimento ou de negócio. Licenças: Comex Stat (dados abertos), Harvard Dataverse (CC0), UCDP/PRIO e Banco Mundial (CC BY 4.0).</p></section>""")
    return R.documento("rotzx Pro · Estudo-amostra: fertilizantes", "".join(corpo))


def gerar(destino: Path = DESTINO, log=print) -> dict:
    d = calcular(log=log)
    R.pdf(html(d), destino)
    log(f"estudo-amostra: {destino}")
    R.miniaturas(destino, MINIATURAS, log=log)                         # D79: prévia real na página /pro/
    return d
