"""rotzOn #2 — passo 2: calcula as tabelas a partir de dados_brutos/ (gerados por baixar.py).

    .venv/bin/python rotzon/edicao-02/calcular.py

Grava em rotzon/edicao-02/tabelas/ e imprime um resumo. Valor = US$ FOB (dólares correntes); volume = kg líquido.
Toda participação tem o denominador dito na própria coluna ou no título da tabela.
"""
import json
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
BRUTO = AQUI / "dados_brutos"
TAB = AQUI / "tabelas"
TRIO = ["1201", "2601", "2709"]  # soja; minério de ferro; petróleo bruto
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)
pd.set_option("display.max_colwidth", 60)


def carregar(nome: str) -> pd.DataFrame:
    df = pd.DataFrame(json.loads((BRUTO / nome).read_text(encoding="utf-8"))["linhas"])
    df["ano"] = df["coAno"].astype(int)
    if "coMes" in df:
        df["mes"] = df["coMes"].astype(int)
    if "coSh4" in df:
        df["sh4"] = df["coSh4"]
        df["produto"] = df["noSh4pt"].str.replace("\xa0", " ").str.strip()
    if "noPaispt" in df:
        df["pais"] = df["noPaispt"].str.replace("\xa0", " ").str.strip()
    df["fob"] = df["vlFob"].astype(float)
    df["kg"] = df["kgLiquido"].astype(float)
    return df[[c for c in ("ano", "mes", "sh4", "produto", "pais", "fob", "kg") if c in df]]


def hhi(s: pd.Series) -> float:
    """Índice Herfindahl-Hirschman (0 a 10.000) das participações por produto: quanto maior, mais concentrado."""
    p = 100 * s / s.sum()
    return float((p ** 2).sum())


def main() -> None:
    TAB.mkdir(exist_ok=True)
    ch = carregar("china_sh4_anual.json")
    mu = carregar("mundo_sh4_anual.json")
    cm = carregar("china_sh4_mensal.json")
    pa = carregar("paises_anual.json")
    atual = json.loads((BRUTO / "atualizacao.json").read_text())
    ult_ano, ult_mes = int(atual["year"]), int(atual["monthNumber"])
    nomes = mu.drop_duplicates("sh4").set_index("sh4").produto

    # conferências: soma por SH4 = total por país?
    d1 = (ch.groupby("ano").fob.sum() - pa[pa.pais == "China"].groupby("ano").fob.sum()).abs().max()
    d2 = (mu.groupby("ano").fob.sum() - pa.groupby("ano").fob.sum()).abs().max()
    d3 = (cm[cm.ano == 2025].fob.sum() - ch[ch.ano == 2025].fob.sum())
    print(f"conferências (devem ser 0): China SH4 × país {d1:,.0f} | mundo SH4 × países {d2:,.0f} | mensal × anual 2025 {d3:,.0f}")

    # 1. China no total exportado, posição e ano em que virou a nº 1
    tot = pa.groupby("ano").fob.sum()
    rank = pa.assign(pos=pa.groupby("ano").fob.rank(ascending=False, method="first"))
    china = rank[rank.pais == "China"].set_index("ano")
    eua = rank[rank.pais == "Estados Unidos"].set_index("ano")
    t1 = pd.DataFrame({
        "China_bi": china.fob / 1e9, "China_part_%": 100 * china.fob / tot, "China_pos": china.pos.astype(int),
        "EUA_bi": eua.fob / 1e9, "EUA_part_%": 100 * eua.fob / tot, "total_Brasil_bi": tot / 1e9,
    })
    lider = rank[rank.pos == 1].set_index("ano").pais
    t1["lider"] = lider
    t1.to_csv(TAB / "1_china_no_total.csv")
    print(f"\n1) CHINA NO TOTAL EXPORTADO PELO BRASIL (US$ FOB; {ult_ano} = jan–{ult_mes:02d})\n", t1.round(1))

    # 2. top 10 produtos para a China em 2025
    def top(df, ano, n=10):
        s = df[df.ano == ano].groupby("sh4").fob.sum().sort_values(ascending=False)
        out = pd.DataFrame({"produto": nomes.reindex(s.index).str[:70], "fob_bi": s / 1e9, "part_%": 100 * s / s.sum()})
        out["acum_%"] = out["part_%"].cumsum()
        return out.head(n), s
    t2, s25 = top(ch, 2025)
    t2.to_csv(TAB / "2_top10_china_2025.csv")
    print("\n2) TOP 10 PRODUTOS EXPORTADOS PARA A CHINA EM 2025 (denominador: total exportado para a China em 2025)\n", t2.round(2))
    print(f"   produtos (SH4) com registro em 2025: {len(s25)} | acima de US$ 1 bi: {(s25 >= 1e9).sum()} | acima de US$ 100 mi: {(s25 >= 1e8).sum()}")
    tm, sm25 = top(mu, 2025)
    tm.to_csv(TAB / "2b_top10_mundo_2025.csv")
    print("\n   comparação: TOP 10 PARA O MUNDO EM 2025 (denominador: total exportado pelo Brasil em 2025)\n", tm.round(2))

    # 3. concentração ao longo do tempo: peso do trio soja + minério + petróleo e HHI
    linhas = []
    for ano in sorted(ch.ano.unique()):
        sc = ch[ch.ano == ano].groupby("sh4").fob.sum()
        sw = mu[mu.ano == ano].groupby("sh4").fob.sum()
        linhas.append({
            "ano": ano,
            **{f"china_{c}_%": 100 * sc.get(c, 0) / sc.sum() for c in TRIO},
            "china_trio_%": 100 * sc.reindex(TRIO).fillna(0).sum() / sc.sum(),
            "china_top3_%": 100 * sc.nlargest(3).sum() / sc.sum(),
            "china_hhi": hhi(sc),
            "mundo_trio_%": 100 * sw.reindex(TRIO).fillna(0).sum() / sw.sum(),
            "mundo_top3_%": 100 * sw.nlargest(3).sum() / sw.sum(),
            "mundo_hhi": hhi(sw),
            "china_n_sh4": len(sc),
        })
    t3 = pd.DataFrame(linhas).set_index("ano")
    t3.to_csv(TAB / "3_concentracao_anual.csv")
    print(f"\n3) CONCENTRAÇÃO (participação no total exportado para a China / para o mundo, US$ FOB; {ult_ano} = jan–{ult_mes:02d})\n", t3.round(1))

    # 4. quanto de cada produto vai para a China (denominador: total exportado do produto para o mundo)
    lin = []
    for c in list(t2.index):
        for ano in (2005, 2015, 2025):
            vc = ch[(ch.ano == ano) & (ch.sh4 == c)].fob.sum()
            vw = mu[(mu.ano == ano) & (mu.sh4 == c)].fob.sum()
            lin.append({"sh4": c, "produto": nomes[c][:50], "ano": ano, "china_%_do_produto": 100 * vc / vw if vw else None})
    t4 = pd.DataFrame(lin).pivot_table(index=["sh4", "produto"], columns="ano", values="china_%_do_produto")
    t4.to_csv(TAB / "4_china_no_destino_de_cada_produto.csv")
    print("\n4) DE TUDO QUE O BRASIL EXPORTA DE CADA PRODUTO, QUANTO VAI PARA A CHINA (%)\n", t4.round(1))

    # 5. 'além do trio': o resto, quanto é e o que cresceu
    resto = ch[~ch.sh4.isin(TRIO)]
    r = resto.groupby("ano").fob.sum() / 1e9
    print("\n5) EXPORTAÇÕES PARA A CHINA FORA DO TRIO (US$ bi):", {a: round(v, 1) for a, v in r.items() if a in (1997, 2005, 2015, 2024, 2025)})
    g = resto[resto.ano.isin([2015, 2025])].pivot_table(index="sh4", columns="ano", values="fob", aggfunc="sum").fillna(0)
    g["dif_bi"] = (g[2025] - g[2015]) / 1e9
    g["produto"] = nomes.reindex(g.index).str[:60]
    g = g.sort_values("dif_bi", ascending=False).head(10)
    g.assign(**{"2015_bi": g[2015] / 1e9, "2025_bi": g[2025] / 1e9})[["produto", "2015_bi", "2025_bi", "dif_bi"]].to_csv(TAB / "5_maiores_altas_fora_do_trio.csv")
    print("   maiores altas fora do trio, 2015→2025 (US$ bi)\n", g.assign(b15=g[2015] / 1e9, b25=g[2025] / 1e9)[["produto", "b15", "b25", "dif_bi"]].round(2))

    # 6. jan–último mês: 2026 × 2025, China
    m = cm[cm.mes <= ult_mes]
    a = m.groupby(["ano", "sh4"]).fob.sum().unstack(0).fillna(0)
    t6 = pd.DataFrame({"produto": nomes.reindex(a.index).str[:50], "2025_bi": a[2025] / 1e9, f"{ult_ano}_bi": a[ult_ano] / 1e9})
    t6["var_%"] = 100 * (a[ult_ano] / a[2025] - 1)
    t6 = t6.sort_values(f"{ult_ano}_bi", ascending=False)
    t6.to_csv(TAB / "6_china_jan_out_2025_2026.csv")
    tot25, tot26 = a[2025].sum(), a[ult_ano].sum()
    print(f"\n6) CHINA, JAN–{ult_mes:02d}: 2025 US$ {tot25 / 1e9:.1f} bi × {ult_ano} US$ {tot26 / 1e9:.1f} bi ({100 * (tot26 / tot25 - 1):+.1f}%)")
    print(t6.head(8).round(1))
    trio25 = a.loc[TRIO, 2025].sum() / tot25 * 100
    trio26 = a.loc[TRIO, ult_ano].sum() / tot26 * 100
    print(f"   trio no total para a China, jan–{ult_mes:02d}: 2025 {trio25:.1f}% × {ult_ano} {trio26:.1f}%")


if __name__ == "__main__":
    main()
