"""rotzOn #3 — passo 3: CSV para o Datawrapper e prévia em PNG (matplotlib).

    .venv/bin/python rotzon/edicao-03/graficos.py

Lê dados_brutos/cafe_pais_anual.json (baixar.py) e grava em rotzon/edicao-03/visuais/:
  - cafe_compradores_1997_2025.csv   país; grupo; 1997; 2025 (% do volume exportado de café, SH4 0901); pos_1997; pos_2025
  - cafe_compradores_1997_2025.png   prévia do gráfico de inclinação (slope)
Países: os que estiveram no top 10 por volume em 1997 ou em 2025.
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
FONTE = ("Fonte: Comex Stat/MDIC, exportações de café (SH4 0901), kg líquido. Participação no volume total exportado de café no ano. "
         "Países que estiveram no top 10 em 1997 ou em 2025.")
TXT, TXT2 = "#0b0b0b", "#52514e"
GRUPOS = {  # rótulo, cor da linha, cor do texto, espessura
    "mesmos no topo": ("Os mesmos 5 do topo", "#3d3c39", TXT, 2.2),
    "entrou no top 10": ("Entraram no top 10", "#2a78d6", TXT, 2.2),
    "saiu do top 10": ("Saíram do top 10", "#eb6834", TXT, 2.2),
    "ficou": ("No top 10 nos dois anos", "#b5b4ad", TXT2, 1.4),
}
NOMES = {"Países Baixos (Holanda)": "Holanda", "Estados Unidos": "EUA"}


def tabela() -> pd.DataFrame:
    df = pd.DataFrame(json.loads((BRUTO / "cafe_pais_anual.json").read_text(encoding="utf-8"))["linhas"])
    df["ano"] = df.coAno.astype(int)
    df["pais"] = df.noPaispt.str.replace("\xa0", " ").str.strip()
    df["kg"] = df.kgLiquido.astype(float)
    part = {}
    for ano in (1997, 2025):
        s = df[df.ano == ano].groupby("pais").kg.sum()
        part[ano] = (100 * s / s.sum()).sort_values(ascending=False)
    top97, top25 = list(part[1997].index[:10]), list(part[2025].index[:10])
    paises = list(dict.fromkeys(top97 + top25))
    pos = {ano: pd.Series(range(1, len(part[ano]) + 1), index=part[ano].index) for ano in (1997, 2025)}
    out = pd.DataFrame({"1997": part[1997].reindex(paises), "2025": part[2025].reindex(paises),
                        "pos_1997": pos[1997].reindex(paises), "pos_2025": pos[2025].reindex(paises)})

    def grupo(p):
        if p in top97[:5] and p in top25[:5]:
            return "mesmos no topo"
        if p in top25 and p not in top97:
            return "entrou no top 10"
        if p in top97 and p not in top25:
            return "saiu do top 10"
        return "ficou"
    out.insert(0, "grupo", [grupo(p) for p in paises])
    out.index.name = "país"
    return out.sort_values("2025", ascending=False)


def fmt(v: float) -> str:
    return "<0,1%" if v < 0.05 else f"{v:.1f}%".replace(".", ",")


def y_de(posicoes: pd.Series) -> dict:
    """Top 10 nas linhas 1–10; quem ficou fora do top 10 vai para a faixa de baixo, na ordem da posição real."""
    y = {p: float(v) for p, v in posicoes.items() if v <= 10}
    for k, (p, v) in enumerate(posicoes[posicoes > 10].sort_values().items()):
        y[p] = 11.6 + k
    return y


def png(t: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 8.6), dpi=200)
    x0, x1 = 0, 1
    ye, yd = y_de(t.pos_1997), y_de(t.pos_2025)
    ordem = sorted(t.index, key=lambda p: list(GRUPOS).index(t.grupo[p]), reverse=True)  # cinzas por baixo
    for p in ordem:
        g = t.grupo[p]
        _, cor, cortxt, lw = GRUPOS[g]
        a, b = ye[p], yd[p]
        ax.plot([x0, x1], [a, b], color=cor, lw=lw, solid_capstyle="round", zorder=3 if g != "ficou" else 2)
        ax.scatter([x0, x1], [a, b], s=30, color=cor, zorder=4, edgecolors="white", linewidths=1.2)
        nome = NOMES.get(p, p)
        peso = "bold" if g != "ficou" else "normal"
        ax.text(x0 - 0.05, a, f"{int(t.pos_1997[p])}º  {nome}  {fmt(t['1997'][p])}", ha="right", va="center", fontsize=9.5,
                color=cortxt, fontweight=peso)
        ax.text(x1 + 0.05, b, f"{fmt(t['2025'][p])}  {nome}  {int(t.pos_2025[p])}º", ha="left", va="center", fontsize=9.5,
                color=cortxt, fontweight=peso)
    ax.axhline(10.8, color="#d6d5cf", lw=0.8, ls=(0, (3, 3)), xmin=0.05, xmax=0.95)
    ax.text(0.5, 10.8, "fora do top 10", ha="center", va="center", fontsize=8.5, color=TXT2, style="italic", zorder=6,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none"))
    for x, ano in ((x0, "1997"), (x1, "2025")):
        ax.text(x, 0.1, ano, ha="center", va="bottom", fontsize=12, fontweight="bold", color=TXT)
    ax.set_xlim(-0.95, 1.95)
    ax.set_ylim(15.2, -0.3)
    ax.axis("off")
    alca = [plt.Line2D([0], [0], color=c, lw=2.4, label=l) for l, c, _, _ in GRUPOS.values()]
    ax.legend(handles=alca, loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=2, frameon=False, fontsize=9, labelcolor=TXT2)
    fig.text(0.03, 0.965, "Os 5 maiores compradores do café brasileiro\nsão os mesmos de 1997", fontsize=15, fontweight="bold",
             color=TXT, va="top")
    fig.text(0.03, 0.885, "Posição no ranking e participação no volume exportado de café. Alemanha, EUA, Itália, Japão e\n"
             "Bélgica somaram 49,6% em 2025. Turquia, Holanda, Rússia e China entraram no top 10.", fontsize=9.5, color=TXT2, va="top")
    fig.text(0.03, 0.015, FONTE, fontsize=7, color=TXT2, wrap=True)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.82, bottom=0.1)
    fig.savefig(VIS / "cafe_compradores_1997_2025.png", facecolor="white")
    plt.close(fig)


def main() -> None:
    VIS.mkdir(exist_ok=True)
    t = tabela()
    t.round(3).to_csv(VIS / "cafe_compradores_1997_2025.csv")
    png(t)
    print(t.round(2))


if __name__ == "__main__":
    main()
