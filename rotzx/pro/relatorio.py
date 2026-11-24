"""Relatório do rotzx Pro em HTML → PDF (D77).

Identidade do atlas (Newsreader e IBM Plex Sans, as cópias de rotzx/mundo/fontes/, cores do tema claro). Gráficos em SVG gerado
aqui, sem biblioteca. O PDF sai do Chromium sem tela (--print-to-pdf). Só formata o que recebe: nenhum número é calculado aqui.
"""
import html
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from ..mundo.paginas import nf, pct, usd

FONTES = Path(__file__).resolve().parent.parent / "mundo" / "fontes"
TINTA, TINTA2, APOIO, REGRA, VERDE, OCRE, NEG = "#222721", "#464C45", "#676B62", "#D8D4C9", "#385344", "#A16D2F", "#9A4A3A"
e = html.escape


def ton(kg: Optional[float]) -> str:
    """Peso em toneladas, com escala ("mil t", "mi t"); ausente = "sem registro"."""
    if kg is None:
        return "sem registro"
    t = kg / 1000
    if t >= 1e6:
        return f"{nf(t / 1e6, 2)} mi t"
    if t >= 1e3:
        return f"{nf(t / 1e3, 0 if t >= 1e5 else 1)} mil t"
    return f"{nf(t, 0)} t"


def usd_t(v: Optional[float]) -> str:
    return "sem registro" if v is None else f"US$ {nf(v, 0)}/t"


def sinal_pct(x: Optional[float]) -> str:
    if x is None:
        return "sem base"
    return ("+" if x > 0 else "−" if x < 0 else "") + pct(abs(x))


def sinal_pp(x: Optional[float]) -> str:
    if x is None:
        return "—"
    return ("+" if x > 0 else "−" if x < 0 else "") + nf(abs(x) * 100, 1) + " p.p."


def sinal_usd(x: Optional[float]) -> str:
    if x is None:
        return "—"
    return ("+" if x > 0 else "−" if x < 0 else "") + usd(abs(x))


def teto(v: float) -> float:
    """Arredonda para cima num número "redondo" (1, 2, 2,5, 5 × 10^k), para o eixo ter marcas legíveis."""
    import math
    if v <= 0:
        return 1
    k = 10 ** math.floor(math.log10(v))
    return next(m * k for m in (1, 2, 2.5, 4, 5, 8, 10) if m * k >= v)


def nome_urf(txt: str) -> str:
    """'0817800 - PORTO DE SANTOS' → 'Porto de Santos' (o código da Receita sai; acentos como na fonte)."""
    n = re.sub(r"^\d+\s*-\s*", "", txt).strip()
    n = re.sub(r"^ALF\s*-\s*", "Alfândega de ", n)
    palavras = [w if w in ("IRF", "ALF") or w.startswith("Alfândega") else w.capitalize() for w in n.split()]
    return " ".join(w.lower() if w.lower() in ("de", "do", "da", "dos", "das", "e") and i else w for i, w in enumerate(palavras))


# ---------- gráficos (SVG) ----------
def barras(itens: Sequence[Tuple[str, float, str]], largura: int = 640, cor: str = VERDE) -> str:
    """Barras horizontais: (rótulo, fração 0–1, texto à direita). A barra vai de 0 a 100% do denominador dito no título."""
    h, top = 26, 4
    alt = top + h * len(itens)
    linhas = []
    for i, (rot, frac, txt) in enumerate(itens):
        y = top + i * h
        w = max(1.5, (largura - 330) * max(0.0, min(1.0, frac)))
        linhas.append(f'<text x="0" y="{y + 16}" class="rot">{e(rot)}</text>'
                      f'<rect x="170" y="{y + 6}" width="{largura - 330}" height="12" fill="{REGRA}" opacity=".45"/>'
                      f'<rect x="170" y="{y + 6}" width="{w:.1f}" height="12" fill="{cor}"/>'
                      f'<text x="{largura}" y="{y + 16}" class="val" text-anchor="end">{e(txt)}</text>')
    return f'<svg class="graf" viewBox="0 0 {largura} {alt}" width="100%" role="img">{"".join(linhas)}</svg>'


def linhas_mensais(series: List[Tuple[str, List[Optional[float]], str]], rotulos: List[str], fmt, largura: int = 640, altura: int = 210, todos: bool = False) -> str:
    """Linhas mês a mês; ponto ausente = lacuna (sem registro, nunca zero)."""
    esq, dir_, top, base = 64, 30, 12, 34
    vals = [v for _, s, *_ in series for v in s if v is not None]
    mn = min(vals) if vals else 0
    mx = teto(max(vals) if vals else 1)
    n = len(rotulos)
    X = lambda i: esq + (largura - esq - dir_) * (i / max(1, n - 1))
    Y = lambda v: top + (altura - top - base) * (1 - v / mx)
    g = []
    for k in range(5):
        v = mx * k / 4
        y = Y(v)
        g.append(f'<line x1="{esq}" x2="{largura - dir_}" y1="{y:.1f}" y2="{y:.1f}" stroke="{REGRA}" stroke-dasharray="2 3"/>'
                 f'<text x="{esq - 6}" y="{y + 4:.1f}" class="eixo" text-anchor="end">{e(fmt(v))}</text>')
    for i, r in enumerate(rotulos):
        if todos or r.endswith("/01") or i == n - 1:
            g.append(f'<text x="{X(i):.1f}" y="{altura - 12}" class="eixo" text-anchor="middle">{e(r)}</text>')
    for nome, s, cor, *tr in series:
        trac = ' stroke-dasharray="5 4"' if tr and tr[0] else ""
        trechos, atual = [], []
        for i, v in enumerate(s):
            if v is None:
                if atual:
                    trechos.append(atual)
                atual = []
            else:
                atual.append(f"{X(i):.1f},{Y(v):.1f}")
        if atual:
            trechos.append(atual)
        for t in trechos:
            if len(t) == 1:                                            # mês isolado: ponto, para não sumir
                x, y = t[0].split(",")
                g.append(f'<circle cx="{x}" cy="{y}" r="2.2" fill="{cor}"/>')
            g.append(f'<polyline points="{" ".join(t)}" fill="none" stroke="{cor}" stroke-width="{1.6 if trac else 2}"{trac}/>')
    leg = "".join(f'<tspan fill="{c}">{"╌" if tr and tr[0] else "■"}</tspan> {e(nm)}   ' for nm, _, c, *tr in series)
    return (f'<svg class="graf" viewBox="0 0 {largura} {altura + 18}" width="100%" role="img">{"".join(g)}'
            f'<text x="{esq}" y="{altura + 12}" class="eixo">{leg}</text></svg>')


CORES_ANO = {2024: "#B9B3A3", 2025: OCRE, 2026: VERDE}


def linhas_ano(por_ano, fmt, largura: int = 640, altura: int = 190, titulo_eixo: str = "") -> str:
    """Uma linha por ano, de jan a dez ({ano: {mês: valor}}); mês sem registro = lacuna (nunca zero)."""
    rot = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    series = [(str(a), [m.get(i) for i in range(1, 13)], CORES_ANO.get(a, TINTA2)) for a, m in sorted(por_ano.items())]
    return linhas_mensais(series, rot, fmt, largura, altura, todos=True)


def cascata(passos, fmt, largura: int = 640, altura: int = 210) -> str:
    """Barras em cascata: [(rótulo, valor, tipo)], tipo 'total' (barra cheia desde zero) ou 'delta' (sobe/desce a partir do acumulado)."""
    esq, top, base = 10, 18, 40
    acum, barras_ = 0.0, []
    for rot, v, tipo in passos:
        if tipo == "total":
            barras_.append((rot, 0.0, v, v, tipo)); acum = v
        else:
            barras_.append((rot, acum, acum + v, v, tipo)); acum += v
    hi = max(max(a, b) for _, a, b, _, _ in barras_)
    lo = min(0.0, min(min(a, b) for _, a, b, _, _ in barras_))
    Y = lambda v: top + (altura - top - base) * (1 - (v - lo) / ((hi - lo) or 1))
    n = len(barras_); w = (largura - esq * 2) / n
    g = [f'<line x1="{esq}" x2="{largura - esq}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" stroke="{REGRA}"/>']
    for i, (rot, a, b, v, tipo) in enumerate(barras_):
        x = esq + i * w + w * 0.18
        cor = VERDE if tipo == "total" else (OCRE if v >= 0 else NEG)
        y0, y1 = sorted((Y(a), Y(b)))
        g.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{w * 0.64:.1f}" height="{max(1.2, y1 - y0):.1f}" fill="{cor}"/>')
        g.append(f'<text x="{x + w * 0.32:.1f}" y="{y0 - 5:.1f}" class="val" text-anchor="middle">{e(fmt(v, tipo))}</text>')
        g.append(f'<text x="{x + w * 0.32:.1f}" y="{altura - 22}" class="rot" text-anchor="middle">{e(rot)}</text>')
    return f'<svg class="graf" viewBox="0 0 {largura} {altura}" width="100%" role="img">{"".join(g)}</svg>'


# ---------- página ----------
def documento(titulo: str, corpo: str, css_extra: str = "") -> str:
    f = FONTES.as_uri()
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{e(titulo)}</title><style>
@font-face{{font-family:"Newsreader";src:url("{f}/Newsreader-wght.ttf");font-weight:200 800}}
@font-face{{font-family:"IBM Plex Sans";src:url("{f}/IBMPlexSans-Regular.ttf");font-weight:400}}
@font-face{{font-family:"IBM Plex Sans";src:url("{f}/IBMPlexSans-SemiBold.ttf");font-weight:600}}
@page{{size:A4;margin:18mm 17mm 18mm 17mm;@bottom-right{{content:counter(page)}}}}
*{{box-sizing:border-box}}
body{{margin:0;font:10.5pt/1.5 "IBM Plex Sans",sans-serif;color:{TINTA};background:#fff}}
h1{{font:500 30pt/1.08 Newsreader,serif;margin:0 0 10pt;letter-spacing:-.01em}}
h2{{font:500 17pt/1.2 Newsreader,serif;margin:0 0 4pt}}
h3{{font:600 10.5pt/1.3 "IBM Plex Sans",sans-serif;margin:12pt 0 4pt}}
p{{margin:0 0 7pt}}
.kicker{{font-size:8.5pt;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:{VERDE};margin-bottom:4pt}}
.fonte,.nota{{font-size:8.5pt;color:{APOIO}}}
.sec{{break-inside:avoid;margin:0 0 16pt}}
.quebra{{break-before:page}}
.capa{{height:250mm;display:flex;flex-direction:column;justify-content:space-between;border-top:4pt solid {VERDE};padding-top:18mm}}
.capa .marca{{font:600 22pt Newsreader,serif;color:{VERDE}}}
.capa .sub{{font-size:13pt;color:{TINTA2};max-width:140mm}}
.selo{{display:inline-block;border:1px solid {VERDE};color:{VERDE};font-size:8.5pt;font-weight:600;letter-spacing:.06em;text-transform:uppercase;padding:3pt 7pt;border-radius:3pt}}
.kpis{{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid {REGRA};border-bottom:1px solid {REGRA};margin:8pt 0}}
.kpi{{padding:7pt 8pt 7pt 0}}.kpi span{{display:block;font-size:8.5pt;color:{TINTA2}}}
.kpi b{{display:block;font:500 15pt/1.2 Newsreader,serif}}.kpi small{{font-size:8.5pt;color:{APOIO}}}
table{{width:100%;border-collapse:collapse;font-size:9pt;font-variant-numeric:tabular-nums;margin:4pt 0 6pt}}
th,td{{text-align:right;padding:3.5pt 5pt;border-bottom:1px solid {REGRA};white-space:nowrap}}th:first-child,td:first-child{{text-align:left}}
td.txt,th.txt{{text-align:left;white-space:normal}}
thead th{{border-bottom:1px solid {TINTA};font-weight:600}}
.leitura{{border-left:3pt solid {OCRE};background:#FAF6EE;padding:8pt 11pt;margin:8pt 0}}
.leitura .kicker{{color:{OCRE}}}
.graf .rot{{font:9pt "IBM Plex Sans";fill:{TINTA}}}.graf .val{{font:9pt "IBM Plex Sans";fill:{TINTA2}}}.graf .eixo{{font:8pt "IBM Plex Sans";fill:{APOIO}}}
.aviso{{font-size:8.5pt;color:{APOIO};border-top:1px solid {REGRA};padding-top:6pt}}
{css_extra}
</style></head><body>{corpo}</body></html>"""


def chrome() -> Optional[str]:
    """Chromium para o PDF: ROTZX_CHROME, um do sistema ou o que o Playwright instala."""
    if os.environ.get("ROTZX_CHROME"):
        return os.environ["ROTZX_CHROME"]
    for nome in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        if shutil.which(nome):
            return shutil.which(nome)
    for p in sorted(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux*/chrome"), reverse=True):
        return str(p)
    return None


def pdf(html_txt: str, destino: Path) -> Path:
    exe = chrome()
    if not exe:
        raise RuntimeError("Chromium não encontrado: defina ROTZX_CHROME com o caminho do navegador")
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        fonte = Path(tmp) / "relatorio.html"
        fonte.write_text(html_txt, encoding="utf-8")
        subprocess.run([exe, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                        f"--print-to-pdf={destino}", fonte.as_uri()], check=True, capture_output=True, timeout=180)
    return destino


def miniaturas(pdf_arq: Path, paginas: Sequence[int], largura: int = 480, log=print) -> List[Path]:
    """Miniaturas WebP de páginas do PDF (D79), para a prévia na página /pro/: `<nome do PDF>-p{n}.webp` ao lado do PDF (D81).

    Usa o pdftoppm (poppler); sem ele, avisa e mantém as miniaturas que já existem.
    """
    exe = shutil.which("pdftoppm")
    if not exe:
        log("  pdftoppm não encontrado: miniaturas mantidas como estão")
        return []
    from PIL import Image
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        for n in paginas:
            base = Path(tmp) / f"p{n}"
            subprocess.run([exe, "-png", "-r", "110", "-f", str(n), "-l", str(n), "-singlefile", str(pdf_arq), str(base)],
                           check=True, capture_output=True, timeout=120)
            img = Image.open(f"{base}.png").convert("RGB")
            img = img.resize((largura, round(img.height * largura / img.width)), Image.LANCZOS)
            dest = pdf_arq.with_name(f"{pdf_arq.stem}-p{n}.webp")
            img.save(dest, "WEBP", quality=80, method=6)
            out.append(dest)
    return out
