"""rotzOn #2 — passo 3: CSV para o Datawrapper e prévia em PNG (matplotlib).

    .venv/bin/python rotzon/edicao-02/graficos.py

Lê dados_brutos/china_sh4_anual.json (baixar.py) e grava em rotzon/edicao-02/visuais/:
  - china_pauta_trio.csv   ano; Soja; Minério de ferro; Petróleo bruto; Outros produtos (% do total exportado para a China)
  - china_pauta_trio.png   prévia da barra 100%
Período: 1997–2025 (anos fechados).
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

AQUI = Path(__file__).resolve().parent
BRUTO = AQUI / "dados_brutos"
VIS = AQUI / "visuais"
FONTE = "Fonte: Comex Stat/MDIC, exportações brasileiras para a China, US$ FOB. Participação no total exportado para a China em cada ano."

# (código SH4, rótulo, cor) — paleta da skill dataviz: 3 primeiras cores categóricas + cinza para "outros"
SERIES = [("1201", "Soja", "#2a78d6"), ("2601", "Minério de ferro", "#eb6834"), ("2709", "Petróleo bruto", "#1baf7a")]
OUTROS = ("Outros produtos", "#c9c8c2")
TXT, TXT2 = "#0b0b0b", "#52514e"


def tabela() -> pd.DataFrame:
    df = pd.DataFrame(json.loads((BRUTO / "china_sh4_anual.json").read_text(encoding="utf-8"))["linhas"])
    df["ano"] = df.coAno.astype(int)
    df["fob"] = df.vlFob.astype(float)
    df = df[df.ano <= 2025]
    tot = df.groupby("ano").fob.sum()
    out = pd.DataFrame(index=tot.index)
    for cod, rot, _ in SERIES:
        out[rot] = 100 * df[df.coSh4 == cod].groupby("ano").fob.sum().reindex(tot.index).fillna(0) / tot
    out[OUTROS[0]] = 100 - out.sum(axis=1)
    return out.round(1)


def png(t: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    base = pd.Series(0.0, index=t.index)
    cores = [c for _, _, c in SERIES] + [OUTROS[1]]
    for col, cor in zip(t.columns, cores):
        ax.bar(t.index, t[col], bottom=base, color=cor, width=0.82, edgecolor="white", linewidth=1.0, label=col)
        base += t[col]
    # rótulos diretos só no último ano
    acum = 0.0
    for col in t.columns:
        v = t.loc[2025, col]
        ax.annotate(f"{col} {v:.1f}%".replace(".", ","), (2025.5, acum + v / 2), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=9, color=TXT)
        acum += v
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(TXT2)
    ax.set_ylim(0, 100)
    ax.set_xlim(1996.4, 2030.5)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_xticks([1997, 2000, 2005, 2010, 2015, 2020, 2025])
    ax.tick_params(colors=TXT2, labelsize=9, length=0)
    ax.grid(axis="y", color="#e4e3df", lw=0.8)
    ax.set_axisbelow(True)
    h, l = ax.get_legend_handles_labels()
    ax.legend(h, l, loc="upper center", bbox_to_anchor=(0.42, -0.07), ncol=4, frameon=False, fontsize=9, labelcolor=TXT2)
    fig.text(0.02, 0.955, "3 de cada 4 dólares que a China paga ao Brasil vêm de três produtos", fontsize=14.5, fontweight="bold", color=TXT)
    fig.text(0.02, 0.91, "Soja, minério de ferro e petróleo bruto somaram 74,2% das exportações para a China em 2025 (em 1997, eram 24,7%).\n"
             "Nas vendas do Brasil para o mundo todo, os três maiores produtos somaram 33,6%.", fontsize=9.5, color=TXT2, va="top")
    fig.text(0.02, 0.02, FONTE, fontsize=7.5, color=TXT2)
    fig.subplots_adjust(left=0.07, right=0.98, top=0.8, bottom=0.17)
    fig.savefig(VIS / "china_pauta_trio.png", facecolor="white")
    plt.close(fig)


def main() -> None:
    VIS.mkdir(exist_ok=True)
    t = tabela()
    t.to_csv(VIS / "china_pauta_trio.csv", index_label="ano")
    png(t)
    print(t.loc[[1997, 2005, 2015, 2025]])


if __name__ == "__main__":
    main()
