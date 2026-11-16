"""Cartão de compartilhamento (1200×630) de cada página estática do atlas (D70).

Desenha, sobre `fontes/cartao-base.png` (marca, silhueta do Brasil, faixa e fonte), o rótulo, o título e até três números
que já estão na página. Usa Pillow e as fontes do atlas (Newsreader e IBM Plex Sans, SIL Open Font License, em `fontes/`).
Só escreve texto que recebe: não calcula nem inventa número.
"""
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Tuple

PASTA = Path(__file__).resolve().parent / "fontes"
TINTA, TINTA2, APOIO, VERDE = "#222721", "#464C45", "#676B62", "#385344"
ESQ, LARG = 72, 1056          # margem esquerda e largura útil (a silhueta ocupa o canto de cima à direita)


@lru_cache(maxsize=None)
def _fonte(nome: str, tam: int, peso: Optional[int] = None):
    from PIL import ImageFont
    f = ImageFont.truetype(str(PASTA / nome), tam)
    if peso:
        f.set_variation_by_axes([peso])
    return f


@lru_cache(maxsize=1)
def _base():
    from PIL import Image
    return Image.open(PASTA / "cartao-base.png").convert("RGB")


def _quebra(d, texto: str, fonte, largura: int, max_linhas: int) -> List[str]:
    """Quebra por palavra; se passar de `max_linhas`, corta com reticências."""
    linhas, atual = [], ""
    for p in texto.split():
        t = f"{atual} {p}".strip()
        if d.textlength(t, font=fonte) <= largura or not atual:
            atual = t
        else:
            linhas.append(atual)
            atual = p
    linhas.append(atual)
    if len(linhas) > max_linhas:
        linhas = linhas[:max_linhas]
        while linhas[-1] and d.textlength(linhas[-1] + "…", font=fonte) > largura:
            linhas[-1] = linhas[-1][:-1]
        linhas[-1] = linhas[-1].rstrip(" ,;(") + "…"
    return linhas


def desenhar(destino: Path, rotulo: str, titulo: str, numeros: List[Tuple[str, str, str]]) -> None:
    """`numeros`: até três (rótulo, valor, complemento). Grava um PNG com paleta, pequeno."""
    from PIL import ImageDraw
    img = _base().copy()
    d = ImageDraw.Draw(img)
    d.text((ESQ, 146), rotulo.upper(), font=_fonte("IBMPlexSans-SemiBold.ttf", 19), fill=VERDE)
    # título: o maior corpo em que cabe numa linha; se não couber, duas linhas num corpo menor (sobra espaço para os números)
    for tam, max_l in ((84, 1), (72, 1), (62, 1), (58, 2), (50, 2), (44, 2)):
        ft = _fonte("Newsreader-wght.ttf", tam, 500)
        linhas = _quebra(d, titulo, ft, LARG - 190, max_l)
        if not linhas[-1].endswith("…"):
            break
    y = 182
    for l in linhas:
        d.text((ESQ, y), l, font=ft, fill=TINTA)
        y += int(tam * 1.06)
    numeros = [n for n in numeros if n and n[1]][:3]
    if numeros:
        y0 = max(y + 26, 372)
        col = LARG // len(numeros)
        d.line([(ESQ, y0 - 14), (ESQ + LARG, y0 - 14)], fill="#D8D4C9", width=1)
        for k, (rot, val, comp) in enumerate(numeros):
            x = ESQ + k * col
            larg = col - 28
            d.text((x, y0), _quebra(d, rot, _fonte("IBMPlexSans-Regular.ttf", 20), larg, 1)[0], font=_fonte("IBMPlexSans-Regular.ttf", 20), fill=TINTA2)
            fv = _fonte("Newsreader-wght.ttf", 50, 500)
            if d.textlength(val, font=fv) > larg:
                fv = _fonte("Newsreader-wght.ttf", 38, 500)
            d.text((x, y0 + 32), _quebra(d, val, fv, larg, 1)[0], font=fv, fill=TINTA)
            fc = _fonte("IBMPlexSans-Regular.ttf", 19)
            for j, l in enumerate(_quebra(d, comp, fc, larg, 2)):
                d.text((x, y0 + 98 + j * 25), l, font=fc, fill=APOIO)
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.quantize(colors=64, dither=0).save(destino, "PNG", optimize=True)
