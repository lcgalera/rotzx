"""rotzOn #1 — passo 3: CSVs para o Datawrapper e prévias em PNG (matplotlib).

    .venv/bin/python rotzon/edicao-01/graficos.py

Lê dados_brutos/ (baixar.py) e grava em rotzon/edicao-01/visuais/:
  - mapa_fornecedores_2025.csv  país em inglês + ISO3 + volume importado em 2025 (mil toneladas)
  - china_vs_russia.csv         ano, China, Rússia (mil toneladas), 2015–2025
  - mapa_fornecedores_2025.png  prévia do mapa
  - china_vs_russia.png         prévia da linha

Geometria do mapa: Natural Earth 1:110m via world-atlas@2.0.2 (domínio público), a mesma do globo do rotzx.
O arquivo é baixado uma vez para dados_brutos/geo/.
"""
import io
import json
import tarfile
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import pycountry  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402
from matplotlib.colors import BoundaryNorm, ListedColormap  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
BRUTO = AQUI / "dados_brutos"
VIS = AQUI / "visuais"
GEO_URL = "https://registry.npmjs.org/world-atlas/-/world-atlas-2.0.2.tgz"  # pacote npm (licença ISC); dados Natural Earth
FONTE = "Fonte: Comex Stat/MDIC, importações do capítulo NCM 31 (adubos ou fertilizantes), kg líquido."

# nomes do Comex Stat que não são iguais aos de catalog/paises_mundo.csv
COMEX_ISO3 = {"Países Baixos (Holanda)": "NLD", "Taiwan (Formosa)": "TWN", "Tcheca, República": "CZE"}
# nomes em inglês no padrão do mapa-múndi do Datawrapper, quando o pycountry usa o nome oficial longo
EN = {"RUS": "Russia", "USA": "United States", "GBR": "United Kingdom", "KOR": "South Korea", "PRK": "North Korea",
      "IRN": "Iran", "VNM": "Vietnam", "BOL": "Bolivia", "VEN": "Venezuela", "SYR": "Syria", "LAO": "Laos",
      "TZA": "Tanzania", "MDA": "Moldova", "TWN": "Taiwan", "CZE": "Czechia", "NLD": "Netherlands",
      "CIV": "Côte d'Ivoire", "COD": "Democratic Republic of the Congo", "COG": "Republic of the Congo",
      "TUR": "Turkey", "BRN": "Brunei", "MKD": "North Macedonia", "PSE": "Palestine"}

# paleta (skill dataviz, palette.md): sequencial azul e duas categorias
SEQ = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
COR_CHINA, COR_RUSSIA = "#2a78d6", "#eb6834"
SEM_REGISTRO = "#e4e3df"
BRASIL = "#ffffff"
TXT, TXT2, GRADE = "#0b0b0b", "#52514e", "#e4e3df"


def volumes() -> pd.DataFrame:
    df = pd.DataFrame(json.loads((BRUTO / "anual_pais_sh4.json").read_text(encoding="utf-8"))["linhas"])
    df["ano"] = df.coAno.astype(int)
    df["pais"] = df.noPaispt.str.replace("\xa0", " ").str.strip()
    df["kg"] = df.kgLiquido.astype(float)
    return df


def nome_en(iso3: str) -> str:
    if iso3 in EN:
        return EN[iso3]
    c = pycountry.countries.get(alpha_3=iso3)
    return getattr(c, "common_name", None) or c.name


def csv_mapa(df: pd.DataFrame) -> pd.DataFrame:
    cat = pd.read_csv(RAIZ / "catalog" / "paises_mundo.csv", dtype=str)
    iso = dict(zip(cat.nome, cat.iso3)) | COMEX_ISO3
    num = dict(zip(cat.iso3, cat.iso_num))
    t = df[df.ano == 2025].groupby("pais").kg.sum()
    out = pd.DataFrame({"pais_comex": t.index, "kg": t.values})
    out["ISO3"] = out.pais_comex.map(iso)
    assert out.ISO3.notna().all(), out[out.ISO3.isna()]
    out["Country"] = out.ISO3.map(nome_en)
    out["iso_num"] = out.ISO3.map(num)
    out["Volume (mil t)"] = (out.kg / 1e6).round(1)
    out["Participação (%)"] = (100 * out.kg / out.kg.sum()).round(2)
    out = out.sort_values("kg", ascending=False)
    # o Brasil aparece como origem por reimportação (87 t em 2025): fica na conta do total, mas fora do mapa
    out[out.ISO3 != "BRA"][["Country", "ISO3", "Volume (mil t)", "Participação (%)"]].to_csv(VIS / "mapa_fornecedores_2025.csv", index=False)
    return out


def csv_linha(df: pd.DataFrame) -> pd.DataFrame:
    s = df[df.pais.isin(["China", "Rússia"])].pivot_table(index="ano", columns="pais", values="kg", aggfunc="sum") / 1e6
    s = s.round(1).rename(columns={"Rússia": "Rússia"})[["China", "Rússia"]]
    s.index.name = "ano"
    s.to_csv(VIS / "china_vs_russia.csv")
    return s


# --- geometria: decodifica o TopoJSON do world-atlas (arcos quantizados, com deltas) ---
def geometria() -> dict:
    destino = BRUTO / "geo" / "countries-110m.json"
    if not destino.exists():
        destino.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(urllib.request.Request(GEO_URL, headers={"User-Agent": "rotzon"}), timeout=60) as r:
            with tarfile.open(fileobj=io.BytesIO(r.read()), mode="r:gz") as tar:
                destino.write_bytes(tar.extractfile("package/countries-110m.json").read())
    topo = json.loads(destino.read_text())
    (sx, sy), (tx, ty) = topo["transform"]["scale"], topo["transform"]["translate"]
    arcos = []
    for arco in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arco:
            x, y = x + dx, y + dy
            pts.append((x * sx + tx, y * sy + ty))
        arcos.append(pts)

    def anel(idx):
        pts = []
        for i in idx:
            a = arcos[i] if i >= 0 else arcos[~i][::-1]
            pts.extend(a if not pts else a[1:])
        return pts

    paises = {}
    for g in topo["objects"]["countries"]["geometries"]:
        if g.get("type") == "Polygon":
            polys = [g["arcs"]]
        elif g.get("type") == "MultiPolygon":
            polys = g["arcs"]
        else:
            continue
        for p in polys:  # só o anel externo basta na prévia
            a = anel(p[0])
            xs = [x for x, _ in a]
            if max(xs) - min(xs) > 180:  # anel que cruza 180° (Rússia, Fiji): desloca o lado oeste para +360
                a = [(x + 360 if x < 0 else x, y) for x, y in a]
            paises.setdefault(g.get("id"), []).append(a)
    return paises


def png_mapa(tab: pd.DataFrame) -> None:
    geo = geometria()
    vol = dict(zip(tab.iso_num, tab["Volume (mil t)"]))
    limites = [0, 100, 500, 2000, 5000, 15000]
    rotulos = ["até 100", "100 a 500", "500 a 2.000", "2.000 a 5.000", "mais de 5.000"]
    norm = BoundaryNorm(limites, len(SEQ))
    cmap = ListedColormap(SEQ)
    fig, ax = plt.subplots(figsize=(12, 6.6), dpi=200)
    fig.patch.set_facecolor("white")
    polys, cores = [], []
    for iso_num, aneis in geo.items():
        if iso_num == "010":  # Antártida fora, só ocupa espaço
            continue
        if iso_num == "076":
            cor = BRASIL
        else:
            cor = cmap(norm(vol[iso_num])) if iso_num in vol else SEM_REGISTRO
        for a in aneis:
            polys.append(a)
            cores.append(cor)
    ax.add_collection(PolyCollection(polys, facecolors=cores, edgecolors="white", linewidths=0.3))
    ax.add_collection(PolyCollection(geo["076"], facecolors="none", edgecolors=TXT2, linewidths=0.8))
    ax.set_xlim(-170, 190)
    ax.set_ylim(-58, 84)
    ax.set_aspect(1.15)
    ax.axis("off")
    # rótulo direto só nos 3 maiores (o resto fica na legenda e na tabela)
    for _, r in tab.head(3).iterrows():
        pos = {"CHN": (104, 33), "RUS": (100, 62), "CAN": (-108, 60)}[r.ISO3]
        ax.annotate(f"{r.pais_comex}\n{r['Volume (mil t)']:,.0f} mil t".replace(",", "."), pos, ha="center", va="center",
                    fontsize=9, color="white", fontweight="bold")
    alca = [Patch(facecolor=c, label=l) for c, l in zip(SEQ, rotulos)] + [Patch(facecolor=SEM_REGISTRO, label="sem registro"),
                                                                Patch(facecolor=BRASIL, edgecolor=TXT2, label="Brasil (destino)")]
    ax.legend(handles=alca, title="Mil toneladas importadas em 2025", loc="lower left", frameon=False,
              fontsize=8.5, title_fontsize=9, labelcolor=TXT2)
    fig.text(0.02, 0.96, "Metade do adubo importado pelo Brasil veio de dois países", fontsize=16, fontweight="bold", color=TXT)
    fig.text(0.02, 0.915, "China (26,3%) e Rússia (24,4%) somaram 50,7% das 45,5 milhões de toneladas importadas em 2025",
             fontsize=10.5, color=TXT2)
    fig.text(0.02, 0.03, FONTE + " Mapa: Natural Earth.", fontsize=7.5, color=TXT2)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.05)
    fig.savefig(VIS / "mapa_fornecedores_2025.png", facecolor="white")
    plt.close(fig)


def png_linha(s: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 5.6), dpi=200)
    for pais, cor in (("Rússia", COR_RUSSIA), ("China", COR_CHINA)):
        ax.plot(s.index, s[pais] / 1000, color=cor, lw=2.2, marker="o", ms=4.5, label=pais)
        ult = s[pais].iloc[-1] / 1000
        ax.annotate(f"{pais} {ult:.1f} mi t".replace(".", ","), (2025, ult), xytext=(8, 7 if pais == "China" else -9),
                    textcoords="offset points", fontsize=10, color=TXT, va="center")
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(TXT2)
    ax.grid(axis="y", color=GRADE, lw=0.8)
    ax.tick_params(colors=TXT2, labelsize=9, length=0)
    ax.set_xticks(range(2015, 2026))
    ax.set_xlim(2014.6, 2027.3)
    ax.set_ylim(0, 13)
    ax.set_ylabel("milhões de toneladas", color=TXT2, fontsize=9)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=TXT2)
    fig.text(0.02, 0.95, "Em 2025, a China passou a Rússia em toneladas", fontsize=15, fontweight="bold", color=TXT)
    fig.text(0.02, 0.905, "Adubos importados pelo Brasil, por país de origem. Em dólares, a Rússia seguiu na frente\n"
             "(US\\$ 4,0 bi × US\\$ 2,9 bi), e em jan–out de 2026 voltou a liderar também em volume.", fontsize=9.5, color=TXT2,
             va="top")
    fig.text(0.02, 0.02, FONTE, fontsize=7.5, color=TXT2)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.8, bottom=0.1)
    fig.savefig(VIS / "china_vs_russia.png", facecolor="white")
    plt.close(fig)


def main() -> None:
    VIS.mkdir(exist_ok=True)
    df = volumes()
    tab = csv_mapa(df)
    s = csv_linha(df)
    png_mapa(tab)
    png_linha(s)
    print(tab.head(8)[["Country", "ISO3", "Volume (mil t)", "Participação (%)"]].to_string(index=False))
    print(s)


if __name__ == "__main__":
    main()
