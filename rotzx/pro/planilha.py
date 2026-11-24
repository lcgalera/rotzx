"""Planilha do estudo-amostra do rotzx Pro (D80): as tabelas por trás de cada seção do PDF, uma aba por seção.

Cada aba começa com o título, a fonte, a data da coleta e o denominador das participações. Sem registro = célula vazia
(com a nota no cabeçalho), nunca zero. Valores em US$ correntes; peso em toneladas; participações em fração (0–1, formato %).
"""
from pathlib import Path

from . import nomes as N, referencia


def gerar(d: dict, destino: Path) -> Path:
    import openpyxl
    from openpyxl.styles import Font
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    ry, ult = d["ry"], d["ultimo_mes"]
    comex = (f"Fonte: Comex Stat (MDIC), dados abertos, importações SH4 3101 a 3105, US$ correntes e kg líquido. Coleta em {d['coleta']}. "
             "Célula vazia = sem registro (nunca zero).")
    t = lambda kg: kg / 1000 if kg is not None else None

    def aba(nome, titulo, nota, cab, linhas, pct=(), usd=()):
        ws = wb.create_sheet(nome[:31])
        ws.append([titulo]); ws["A1"].font = Font(bold=True, size=12)
        ws.append([nota])
        ws.append([])
        ws.append(cab)
        for c in ws[4]:
            c.font = Font(bold=True)
        for l in linhas:
            ws.append(l)
        for col in pct:
            for row in ws.iter_rows(min_row=5, min_col=col, max_col=col):
                row[0].number_format = "0.0%"
        for col in usd:
            for row in ws.iter_rows(min_row=5, min_col=col, max_col=col):
                row[0].number_format = "#,##0"
        ws.column_dimensions["A"].width = 42
        return ws

    P = d["per"]
    aba("1 Totais", "Valor, volume, preço, frete e concentração por período",
        comex + " Participações sobre o total importado do grupo no período.",
        ["Período", "Valor US$ FOB", "Volume (t)", "US$/t FOB", "US$/t CIF", "Frete US$/t", "Parte do maior", "Parte dos 3 maiores", "HHI", "Países"],
        [[k.replace("ytd25", f"{ry}/2025").replace("ytd26", f"{ry}/2026"), p["total"]["fob"], t(p["total"]["kg"]), p["preco_t"], p["cif_t"], p["frete_t"],
          p["maior"], p["tres"], p["hhi"], p["n"]] for k, p in P.items()], pct=(7, 8), usd=(2, 3))
    dt = d["dec_total"]
    linhas = [["Total do grupo (itens = NCM)", dt["v0"], dt["v1"], dt["variacao"], dt["volume"], dt["preco"], dt["mix"], dt["sem_peso"], None, None]]
    linhas += [[f["nome"], f["v0"], f["v1"], f["variacao"], f["volume"], f["preco"], f["mix"], f["sem_peso"], f["parte0"], f["parte1"]] for f in d["dec_forn"]]
    aba("2 Volume preço mix", f"Decomposição da variação de valor, {ry}/2025 → {ry}/2026",
        comex + " Volume + preço + mix + sem peso = variação (exato). Parte = valor do país ÷ total do grupo no período.",
        ["Recorte", f"Valor {ry}/25", f"Valor {ry}/26", "Variação", "Efeito volume", "Efeito preço", "Efeito mix", "Sem peso registrado", f"Parte {ry}/25", f"Parte {ry}/26"],
        linhas, pct=(9, 10), usd=(2, 3, 4, 5, 6, 7, 8))
    pl = []
    for p in d["produtos"]:
        pl.append([p["nome"], p["ncm"], "(produto)", p["base"].upper(), p["imp0"], p["imp1"], p["parte1"], t(p["kg1"])])
        for o in p["origens"]:
            pl.append([p["nome"], p["ncm"], o["nome"], p["base"].upper(), o["p0"], o["p1"], o["parte1"], t(o["kg1"])])
    aba("3 Preço produto origem", f"US$/t por produto e origem, {ry}/2025 e {ry}/2026",
        comex + " US$/t = valor ÷ peso. Parte do produto: sobre o total do grupo; da origem: sobre o valor do produto.",
        ["Produto", "NCM", "Origem", "Base", f"US$/t {ry}/25", f"US$/t {ry}/26", f"Parte {ry}/26", f"Volume {ry}/26 (t)"], pl, pct=(7,))
    rot = {k: v[1] for k, v in referencia.SERIES.items()}
    aba("4 Referência", f"Importado × Pink Sheet (média {ry})",
        comex + f" Referência: {referencia.FONTE} ({d['ref_atualizado'] or 'sem arquivo'}). Aproximação: bases e especificações diferentes.",
        ["Produto", "NCM", "Série de referência", "Base da importação", f"Importado {ry}/25", f"Importado {ry}/26", f"Referência {ry}/25", f"Referência {ry}/26"],
        [[p["nome"], p["ncm"], rot.get(p["serie_ref"], "sem série equivalente"), p["base"].upper(), p["imp0"], p["imp1"], p["ref0"], p["ref1"]] for p in d["produtos"]])
    ws = aba("4b Mensal US$ t", "US$/t mensal: 3 maiores origens de cada produto e Pink Sheet", comex, ["Produto", "Série"] + [f"{a}-{m:02d}" for a, m in d["meses_ser"]], [])
    for p in d["produtos"]:
        for n, s in p["mensal"]:
            ws.append([p["nome"], n] + s)
        if p["ref_mensal"]:
            ws.append([p["nome"], "Pink Sheet: " + rot[p["serie_ref"]]] + p["ref_mensal"])
    aba("5 Dependência", f"Concentração por produto, {ry}/2025 e {ry}/2026",
        comex + " Partes sobre o valor importado de cada produto no período. HHI = soma dos quadrados das partes em % (0 a 10.000).",
        ["Produto", "NCM", f"Parte no grupo {ry}/26", f"Maior fornecedor {ry}/26", "Parte do maior", "Parte dos 3 maiores", f"HHI {ry}/26",
         f"Maior fornecedor {ry}/25", f"Parte do maior {ry}/25", f"HHI {ry}/25"],
        [[x["nome"], x["ncm"], x["parte_grupo"], x["nome_maior1"], x["maior1"], x["tres1"], x["hhi1"], x["nome_maior0"], x["maior0"], x["hhi0"]] for x in d["dep_prod"]],
        pct=(3, 5, 6, 9))
    cal = []
    for a in sorted(d["cal"]):
        cal.append([f"{a} mensal"] + [t(d["cal"][a].get(m)) for m in range(1, 13)])
        cal.append([f"{a} acumulado"] + [t(d["cal_acum"][a].get(m)) for m in range(1, 13)])
    aba("6 Calendário", "Volume importado por mês e acumulado no ano (t)", comex,
        ["Ano"] + ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"], cal, usd=tuple(range(2, 14)))
    aba("7 Portos", f"Unidades da Receita, {ry}/2026", comex + " Parte = valor da unidade ÷ total do grupo. Frete/t = frete declarado ÷ peso.",
        ["Unidade", "Valor US$ FOB", "Volume (t)", "Parte do valor", "Frete US$/t"],
        [[x["nome"], x["fob"], t(x["kg"]), x["parte"], x["frete_t"]] for x in d["urf"]], pct=(4,), usd=(2, 3))
    aba("7b Estados", f"UF, {ry}/2026", comex + " Parte = valor da UF ÷ total do grupo.",
        ["UF", "Valor US$ FOB", "Volume (t)", "Parte do valor"], [[x["nome"], x["fob"], t(x["kg"]), x["parte"]] for x in d["uf"]], pct=(4,), usd=(2, 3))
    aba("7c Frete origem", f"Frete por origem, {ry}/2025 e {ry}/2026", comex + " Frete/t = frete declarado ÷ peso; frete ÷ FOB = frete total ÷ valor FOB.",
        ["Origem", f"Volume {ry}/26 (t)", f"Frete US$/t {ry}/25", f"Frete US$/t {ry}/26", "Frete ÷ FOB"],
        [[x["nome"], t(x["kg"]), x["frete_t0"], x["frete_t"], x["frete_pct"]] for x in d["frete_origem"]], pct=(5,), usd=(2,))
    vl = [[k, x["nome"], x["fob"], t(x["kg"]), x["parte"]] for k in ("2025", "ytd25", "ytd26") for x in d["via"][k]]
    aba("8 Vias", "Vias de transporte como declaradas na fonte",
        comex + " Atenção: a via “aérea” de 2026 tem sinais de erro de registro (ver nota do PDF, seção 6).",
        ["Período", "Via", "Valor US$ FOB", "Volume (t)", "Parte do valor"], vl, pct=(5,), usd=(3, 4))
    aba("9 NCM oficiais", "Descrições oficiais das NCMs (Comex Stat)", comex, ["NCM", "Nome curto usado no estudo", "Descrição oficial"],
        [[c, N.ncm(c, o), o] for c, o in sorted(d["ncm_oficial"].items())])
    aba("Fontes", "Fontes, licenças e contexto", "rotzx Pro · estudo-amostra · não é recomendação de investimento ou de negócio.", ["Item", "Detalhe"],
        [["Comex Stat (MDIC)", "api-comexstat.mdic.gov.br, rota /general; dados abertos do governo federal"],
         ["Pink Sheet (Banco Mundial)", f"{referencia.FONTE}; {referencia.URL}"]])
    destino.parent.mkdir(parents=True, exist_ok=True)
    wb.save(destino)
    return destino
