"""rotzOn #3 — passo 2: calcula as tabelas a partir de dados_brutos/ (gerados por baixar.py).

    .venv/bin/python rotzon/edicao-03/calcular.py

Grava em rotzon/edicao-03/tabelas/ e imprime um resumo.
Volume = kg líquido, também em sacas de 60 kg (unidade usual do café: 1 saca = 60 kg). Valor = US$ FOB correntes.
Participação: denominador = total exportado de café (SH4 0901) no mesmo ano e na mesma métrica.
"""
import json
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
BRUTO = AQUI / "dados_brutos"
TAB = AQUI / "tabelas"
SACA = 60.0
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)


def carregar(nome: str) -> pd.DataFrame:
    df = pd.DataFrame(json.loads((BRUTO / nome).read_text(encoding="utf-8"))["linhas"])
    df["ano"] = df["coAno"].astype(int)
    if "coMes" in df:
        df["mes"] = df["coMes"].astype(int)
    if "noPaispt" in df:
        df["pais"] = df["noPaispt"].str.replace("\xa0", " ").str.strip()
    if "coNcm" in df:
        df["ncm"] = df["coNcm"]
        df["nome_ncm"] = df["noNcmpt"].str.replace("\xa0", " ").str.strip()
    df["fob"] = df["vlFob"].astype(float)
    df["kg"] = df["kgLiquido"].astype(float)
    return df[[c for c in ("ano", "mes", "pais", "ncm", "nome_ncm", "fob", "kg") if c in df]]


def ranking(df: pd.DataFrame, ano: int, metr: str = "kg") -> pd.DataFrame:
    s = df[df.ano == ano].groupby("pais")[metr].sum().sort_values(ascending=False)
    return pd.DataFrame({metr: s, "part_%": 100 * s / s.sum(), "pos": range(1, len(s) + 1)})


def main() -> None:
    TAB.mkdir(exist_ok=True)
    pa = carregar("cafe_pais_anual.json")
    nc = carregar("cafe_ncm_anual.json")
    me = carregar("cafe_pais_mensal.json")
    ex = carregar("extratos_ncm_anual.json")
    sp = carregar("soluvel_pais_anual.json")
    atual = json.loads((BRUTO / "atualizacao.json").read_text())
    ult_ano, ult_mes = int(atual["year"]), int(atual["monthNumber"])

    d1 = (pa.groupby("ano").fob.sum() - nc.groupby("ano").fob.sum()).abs().max()
    d2 = me[me.ano == 2025].fob.sum() - pa[pa.ano == 2025].fob.sum()
    print(f"conferências (devem ser 0): país × NCM {d1:,.0f} | mensal × anual 2025 {d2:,.0f}")

    # 1. totais por ano
    t = pa.groupby("ano")[["kg", "fob"]].sum()
    t["mi_sacas"] = t.kg / SACA / 1e6
    t["fob_bi"] = t.fob / 1e9
    t["us$_por_saca"] = t.fob / (t.kg / SACA)
    t["n_paises"] = pa[pa.kg > 0].groupby("ano").pais.nunique()
    t.to_csv(TAB / "1_total_anual.csv")
    print(f"\n1) CAFÉ (SH4 0901) EXPORTADO POR ANO ({ult_ano} = jan–{ult_mes:02d})\n", t[["mi_sacas", "fob_bi", "us$_por_saca", "n_paises"]].round(1))
    for a, b in ((1997, 2025), (2015, 2025)):
        print(f"   {a}→{b}: sacas {100 * (t.kg[b] / t.kg[a] - 1):+.1f}% | US$ {100 * (t.fob[b] / t.fob[a] - 1):+.1f}%")

    # 2. composição por NCM em 2025
    c = nc[nc.ano == 2025].groupby(["ncm", "nome_ncm"])[["kg", "fob"]].sum()
    c["part_fob_%"] = 100 * c.fob / c.fob.sum()
    c.to_csv(TAB / "2_composicao_ncm_2025.csv")
    print("\n2) COMPOSIÇÃO DO 0901 EM 2025 (denominador: total do 0901, US$)\n", c[["part_fob_%"]].round(2))

    # 3. rankings 1997 × 2025 (volume)
    r97, r25 = ranking(pa, 1997), ranking(pa, 2025)
    r97.to_csv(TAB / "3a_ranking_1997_kg.csv")
    r25.to_csv(TAB / "3b_ranking_2025_kg.csv")
    print("\n3) TOP 10 COMPRADORES POR VOLUME (denominador: total exportado de café no ano, kg)")
    lado = pd.concat([r97.head(10).reset_index().add_suffix("_1997"), r25.head(10).reset_index().add_suffix("_2025")], axis=1)
    print(lado[["pais_1997", "part_%_1997", "pais_2025", "part_%_2025"]].round(1).to_string(index=False))
    for n in (3, 5, 10):
        print(f"   top {n}: 1997 {r97['part_%'].head(n).sum():.1f}% | 2025 {r25['part_%'].head(n).sum():.1f}%")
    rf25 = ranking(pa, 2025, "fob")
    print("   top 10 por US$ em 2025:", [(p, round(v, 1)) for p, v in rf25["part_%"].head(10).items()])

    # 3b. quem foi o nº 1 em cada ano (volume e valor)
    lid = pd.DataFrame({m: {ano: ranking(pa, ano, m).index[0] for ano in range(1997, ult_ano + 1)} for m in ("kg", "fob")})
    lid.index.name = "ano"
    lid.to_csv(TAB / "3c_lider_por_ano.csv")
    print("   nº 1 por ano (kg):", lid.kg.value_counts().to_dict(), "| (US$):", lid.fob.value_counts().to_dict())

    # 4. slope: países que estão no top 10 de 1997 ou de 2025
    paises = list(dict.fromkeys(list(r97.head(10).index) + list(r25.head(10).index)))
    sl = pd.DataFrame({"part_1997_%": r97["part_%"].reindex(paises), "pos_1997": r97.pos.reindex(paises),
                       "part_2025_%": r25["part_%"].reindex(paises), "pos_2025": r25.pos.reindex(paises)})
    sl["dif_pp"] = sl["part_2025_%"] - sl["part_1997_%"]
    sl = sl.sort_values("part_2025_%", ascending=False)
    sl.to_csv(TAB / "4_slope_1997_2025.csv")
    print("\n4) 1997 × 2025, PAÍSES DO TOP 10 EM UM DOS ANOS (part. no volume; dif. em p.p.; NaN = sem registro)\n", sl.round(1))

    # 5. maiores ganhos e perdas de participação, 1997→2025 (p.p.), entre todos os países
    todos = pd.DataFrame({"p97": r97["part_%"], "p25": r25["part_%"]})
    todos["dif_pp"] = todos.p25.fillna(0) - todos.p97.fillna(0)
    print("\n5) MAIORES GANHOS (p.p.):", [(p, round(v, 1)) for p, v in todos.dif_pp.nlargest(6).items()])
    print("   MAIORES PERDAS (p.p.):", [(p, round(v, 1)) for p, v in todos.dif_pp.nsmallest(6).items()])
    todos.to_csv(TAB / "5_dif_participacao_1997_2025.csv")

    # 6. série de participação dos principais, ano a ano
    foco = ["Estados Unidos", "Alemanha", "Itália", "Japão", "Bélgica", "China", "Turquia", "Colômbia"]
    tot = pa.groupby("ano").kg.sum()
    se = pa[pa.pais.isin(foco)].pivot_table(index="ano", columns="pais", values="kg", aggfunc="sum").div(tot, axis=0) * 100
    se.to_csv(TAB / "6_serie_participacao.csv")
    print("\n6) PARTICIPAÇÃO NO VOLUME, ANOS SELECIONADOS (%)\n", se.loc[[1997, 2005, 2010, 2015, 2020, 2024, 2025, ult_ano]].round(1))
    pos_ch = {a: int(ranking(pa, a).pos.get("China", 0)) for a in range(1997, ult_ano + 1)}
    print("   posição da China por ano:", pos_ch)

    # 7. jan–último mês: 2026 × 2025
    m = me[me.mes <= ult_mes]
    a = m.groupby(["ano", "pais"])[["kg", "fob"]].sum().unstack(0).fillna(0)
    k25, k26 = a["kg"][2025].sum(), a["kg"][ult_ano].sum()
    f25, f26 = a["fob"][2025].sum(), a["fob"][ult_ano].sum()
    print(f"\n7) JAN–{ult_mes:02d}: sacas 2025 {k25 / SACA / 1e6:.1f} mi × {ult_ano} {k26 / SACA / 1e6:.1f} mi ({100 * (k26 / k25 - 1):+.1f}%) | "
          f"US$ {f25 / 1e9:.2f} bi × {f26 / 1e9:.2f} bi ({100 * (f26 / f25 - 1):+.1f}%) | US$/saca {f25 / (k25 / SACA):.0f} × {f26 / (k26 / SACA):.0f}")
    j = pd.DataFrame({"kg_2025": a["kg"][2025], f"kg_{ult_ano}": a["kg"][ult_ano]})
    j["part25_%"] = 100 * j.kg_2025 / k25
    j[f"part{ult_ano % 100}_%"] = 100 * j[f"kg_{ult_ano}"] / k26
    j["var_%"] = 100 * (j[f"kg_{ult_ano}"] / j.kg_2025 - 1)
    j = j.sort_values(f"kg_{ult_ano}", ascending=False)
    j.to_csv(TAB / "7_jan_out_2025_2026.csv")
    print(j.head(10).round(1))

    # 8. café solúvel (NCM 21011110)
    so = sp[sp.ncm == "21011110"]
    st = so.groupby("ano")[["kg", "fob"]].sum()
    print(f"\n8) CAFÉ SOLÚVEL (NCM 21011110): 2025 US$ {st.fob[2025] / 1e9:.2f} bi, {st.kg[2025] / 1e6:.0f} mil t | 1997 US$ {st.fob[1997] / 1e9:.2f} bi")
    rs = ranking(so, 2025, "fob")
    print("   top 5 compradores 2025 (US$; denominador: total do solúvel):", [(p, round(v, 1)) for p, v in rs["part_%"].head(5).items()])
    print(f"   solúvel ÷ (0901 + solúvel), US$ 2025: {100 * st.fob[2025] / (st.fob[2025] + t.fob[2025]):.1f}%")
    rs.to_csv(TAB / "8_soluvel_2025.csv")


if __name__ == "__main__":
    main()
