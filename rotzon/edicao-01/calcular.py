"""rotzOn #1 — passo 2: calcula as tabelas a partir de dados_brutos/ (gerados por baixar.py).

    .venv/bin/python rotzon/edicao-01/calcular.py

Grava em rotzon/edicao-01/tabelas/ e imprime um resumo. Volume = kg líquido; valor = US$ FOB (dólares correntes).
Toda participação tem denominador explícito: o total importado do capítulo NCM 31 no mesmo período e na mesma métrica.
"""
import json
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
BRUTO = AQUI / "dados_brutos"
TAB = AQUI / "tabelas"
SH4 = {"3102": "nitrogenados (N)", "3103": "fosfatados (P)", "3104": "potássicos (K)", "3105": "misturas NPK, MAP/DAP e outros"}
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)


def carregar(nome: str) -> pd.DataFrame:
    df = pd.DataFrame(json.loads((BRUTO / nome).read_text(encoding="utf-8"))["linhas"])
    df["ano"] = df["coAno"].astype(int)
    if "coMes" in df:
        df["mes"] = df["coMes"].astype(int)
    df["pais"] = df["noPaispt"].str.replace("\xa0", " ").str.strip()
    df["sh4"] = df["coSh4"]
    df["kg"] = df["kgLiquido"].astype(float)
    df["fob"] = df["vlFob"].astype(float)
    return df.drop(columns=[c for c in df if c.startswith(("co", "no", "vl", "kgL"))])


def participacao(df: pd.DataFrame, metrica: str, n: int) -> pd.DataFrame:
    t = df.groupby("pais")[metrica].sum().sort_values(ascending=False)
    out = pd.DataFrame({metrica: t, "part_%": 100 * t / t.sum()}).head(n)
    out["acum_%"] = out["part_%"].cumsum()
    return out


def main() -> None:
    TAB.mkdir(exist_ok=True)
    an = carregar("anual_pais_sh4.json")
    me = carregar("mensal_pais_sh4.json")
    atual = json.loads((BRUTO / "atualizacao.json").read_text())
    ult_mes = int(atual["monthNumber"])

    # conferência: a soma da série mensal bate com a consulta anual?
    a = an.groupby("ano")[["kg", "fob"]].sum()
    m = me[me.ano <= 2025].groupby("ano")[["kg", "fob"]].sum()
    dif = (a - m).abs().max().max()
    print(f"conferência anual × soma mensal (2015–2025): maior diferença = {dif:,.0f}")

    # 1. total
    tot = me.groupby("ano")[["kg", "fob"]].sum()
    tot["mil_t"] = tot.kg / 1e6
    tot["fob_bi"] = tot.fob / 1e9
    tot.loc[2026, "obs"] = f"jan–{ult_mes:02d}"
    ytd = me[me.mes <= ult_mes].groupby("ano")[["kg", "fob"]].sum()
    tot["mil_t_jan_out"] = ytd.kg / 1e6
    tot.to_csv(TAB / "1_total_anual.csv")
    print("\n1) TOTAL IMPORTADO, capítulo 31\n", tot[["mil_t", "fob_bi", "mil_t_jan_out"]].round(1))
    k15, k25 = tot.loc[2015, "kg"], tot.loc[2025, "kg"]
    f15, f25 = tot.loc[2015, "fob"], tot.loc[2025, "fob"]
    print(f"2025 vs 2015: volume {100 * (k25 / k15 - 1):+.1f}% | US$ FOB {100 * (f25 / f15 - 1):+.1f}%")

    # líder e vice de cada ano (kg)
    lid = []
    for ano, g in me[me.ano <= 2025].groupby("ano"):
        t = g.groupby("pais").kg.sum().sort_values(ascending=False)
        lid.append({"ano": ano, "1º": t.index[0], "1º_%": 100 * t.iloc[0] / t.sum(), "2º": t.index[1], "2º_%": 100 * t.iloc[1] / t.sum()})
    lid = pd.DataFrame(lid)
    lid.to_csv(TAB / "2c_lider_por_ano_kg.csv", index=False)
    print("\nLÍDER E VICE POR ANO (kg)\n", lid.round(1).to_string(index=False))

    # 2 e 5. top 5 e concentração em 2025
    a25 = me[me.ano == 2025]
    for metr in ("kg", "fob"):
        t = participacao(a25, metr, 5)
        t.to_csv(TAB / f"2_top5_2025_{metr}.csv")
        print(f"\n2) TOP 5 FORNECEDORES 2025 por {metr} (denominador: total cap. 31 em 2025)\n", t.round(2))

    # 3. China × Rússia
    cr = me[me.pais.isin(["China", "Rússia"])]
    serie = cr.pivot_table(index="ano", columns="pais", values=["kg", "fob"], aggfunc="sum")
    part = 100 * cr.pivot_table(index="ano", columns="pais", values="kg", aggfunc="sum").div(tot.kg, axis=0)
    out = pd.DataFrame({
        "China_mil_t": serie["kg"]["China"] / 1e6, "Russia_mil_t": serie["kg"]["Rússia"] / 1e6,
        "China_part_kg_%": part["China"], "Russia_part_kg_%": part["Rússia"],
        "China_fob_bi": serie["fob"]["China"] / 1e9, "Russia_fob_bi": serie["fob"]["Rússia"] / 1e9,
    })
    out.to_csv(TAB / "3_china_russia_anual.csv")
    print("\n3) CHINA × RÚSSIA por ano (2026 = jan–%02d)\n" % ult_mes, out.round(2))

    mens = cr.pivot_table(index=["ano", "mes"], columns="pais", values=["kg", "fob"], aggfunc="sum").fillna(0)
    mens.columns = [f"{p}_{m}" for m, p in mens.columns]
    mens["China_maior_kg"] = mens["China_kg"] > mens["Rússia_kg"]
    mens["China_maior_fob"] = mens["China_fob"] > mens["Rússia_fob"]
    mens.to_csv(TAB / "3_china_russia_mensal.csv")
    for metr in ("kg", "fob"):
        meses = mens[mens[f"China_maior_{metr}"]].index.tolist()
        print(f"   meses com China > Rússia em {metr}: {len(meses)} de {len(mens)} ->", [f"{a}-{m:02d}" for a, m in meses])
    # acumulado no ano, mês a mês (janela que um jornal usaria: "no acumulado até X")
    acum = mens[["China_kg", "Rússia_kg", "China_fob", "Rússia_fob"]].groupby(level=0).cumsum()
    acum["China_maior_kg"] = acum.China_kg > acum["Rússia_kg"]
    acum["China_maior_fob"] = acum.China_fob > acum["Rússia_fob"]
    acum.to_csv(TAB / "3_china_russia_acumulado_no_ano.csv")
    print("   acumulado no ano com China > Rússia (kg):", [f"{a}-{m:02d}" for a, m in acum[acum.China_maior_kg].index])
    print("   acumulado no ano com China > Rússia (fob):", [f"{a}-{m:02d}" for a, m in acum[acum.China_maior_fob].index])
    # 12 meses móveis
    mov = mens[["China_kg", "Rússia_kg", "China_fob", "Rússia_fob"]].rolling(12).sum().dropna()
    print("   12 meses móveis com China > Rússia (kg):", [f"{a}-{m:02d}" for a, m in mov[mov.China_kg > mov["Rússia_kg"]].index])
    print("   12 meses móveis com China > Rússia (fob):", [f"{a}-{m:02d}" for a, m in mov[mov.China_fob > mov["Rússia_fob"]].index])
    mov.to_csv(TAB / "3_china_russia_12m_moveis.csv")

    # 4. principal fornecedor por nutriente (SH4), 2025 e 2026 jan–último mês
    linhas = []
    for ano in (2025, 2026):
        for cod, nome in SH4.items():
            sub = me[(me.ano == ano) & (me.sh4 == cod)]
            for metr in ("kg", "fob"):
                t = participacao(sub, metr, 3)
                linhas.append({"ano": ano, "sh4": cod, "nutriente": nome, "metrica": metr,
                               **{f"{i + 1}º": f"{p} ({v:.1f}%)" for i, (p, v) in enumerate(t["part_%"].items())},
                               "total_sh4": sub[metr].sum()})
    t4 = pd.DataFrame(linhas)
    t4.to_csv(TAB / "4_lider_por_nutriente.csv", index=False)
    print("\n4) LÍDER POR NUTRIENTE (participação no total do próprio SH4)\n", t4[t4.metrica == "kg"].drop(columns="metrica").to_string(index=False))
    print(t4[t4.metrica == "fob"].drop(columns="metrica").to_string(index=False))

    # peso de cada SH4 no total
    p = me[me.ano == 2025].groupby("sh4")[["kg", "fob"]].sum()
    print("\n   peso de cada SH4 no cap. 31 em 2025 (%):\n", (100 * p / p.sum()).round(1))

    # 2026 jan–último mês: top 5
    t26 = participacao(me[me.ano == 2026], "kg", 5)
    t26.to_csv(TAB / "2b_top5_2026_jan_out_kg.csv")
    print(f"\n2026 jan–{ult_mes:02d}, top 5 por kg\n", t26.round(2))
    t26f = participacao(me[me.ano == 2026], "fob", 5)
    print(f"2026 jan–{ult_mes:02d}, top 5 por fob\n", t26f.round(2))


if __name__ == "__main__":
    main()
