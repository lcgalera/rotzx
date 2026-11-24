"""Estudo-amostra de fertilizantes do rotzx Pro: invólucro do motor (D81).

Mantém os nomes de antes (DESTINO, PLANILHA, MINIATURAS, CONTEXTO, calcular, html, gerar, leitura, perfis) para o comando e os testes;
o motor está em rotzx/pro/estudo.py e o recorte em rotzx/pro/amostras/fertilizantes.py.
"""
from . import estudo
from .amostras import fertilizantes as F

RECORTE = F.RECORTE
SH4, FLUXO, ANOS = F.SH4, "importacao", estudo.ANOS
DESTINO, PLANILHA, MINIATURAS = RECORTE.destino, RECORTE.planilha, RECORTE.miniaturas
CONTEXTO, PRODUTOS = F.CONTEXTO, F.PRODUTOS
leitura, perfis = F.leitura, F.perfis


def calcular(X=None, log=print) -> dict:
    return estudo.calcular(RECORTE, X, log=log)


def html(d: dict) -> str:
    return estudo.html(RECORTE, d)


def gerar(log=print) -> dict:
    return estudo.gerar(RECORTE, log=log)
