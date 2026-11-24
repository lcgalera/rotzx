"""Nomes legíveis para o relatório do rotzx Pro (D80).

A fonte (Comex Stat) manda unidades da Receita e vias em caixa alta e, em parte, sem acento ("PORTO DE PARANAGUA", "MARITIMA").
Aqui só se corrige o que está no dicionário (grafia oficial do lugar); palavra fora dele sai em caixa de título, sem chute de acento.
As NCMs ganham um nome curto escrito a partir do texto oficial; o texto oficial completo vai para o apêndice do estudo.
"""
import re

PALAVRAS = {
    "PARANAGUA": "Paranaguá", "SAO": "São", "LUIS": "Luís", "VITORIA": "Vitória", "SANTAREM": "Santarém", "MACEIO": "Maceió",
    "ITAJAI": "Itajaí", "CACERES": "Cáceres", "GUAJARA-MIRIM": "Guajará-Mirim", "JAGUARAO": "Jaguarão", "ITAGUAI": "Itaguaí",
    "BELEM": "Belém", "CORUMBA": "Corumbá", "PECEM": "Pecém", "IGUACU": "Iguaçu", "AMAPA": "Amapá", "PARANA": "Paraná",
    "MARITIMA": "Marítima", "AEREA": "Aérea", "RODOVIARIA": "Rodoviária", "FERROVIARIA": "Ferroviária", "FLUVIAL": "Fluvial",
    "LACUSTRE": "Lacustre", "POSTAL": "Postal", "BRASILIA": "Brasília", "GOIANIA": "Goiânia", "CUIABA": "Cuiabá",
    "UBERLANDIA": "Uberlândia", "JUNDIAI": "Jundiaí", "TAUBATE": "Taubaté", "SUAPE": "Suape", "IRF": "IRF", "NAO": "Não", "INFORMADO": "informado", "DECLARADA": "declarada",
}
MINUSCULAS = {"de", "do", "da", "dos", "das", "e"}


def _palavra(w: str, i: int) -> str:
    if w.upper() in PALAVRAS:
        return PALAVRAS[w.upper()]
    if i and w.lower() in MINUSCULAS:
        return w.lower()
    return "-".join(p[:1].upper() + p[1:].lower() for p in w.split("-"))


def lugar(txt: str) -> str:
    """'0917800 - PORTO DE PARANAGUA' → 'Porto de Paranaguá'; 'ALF - SALVADOR' → 'Alfândega de Salvador'; 'MARITIMA' → 'Marítima'."""
    n = re.sub(r"^\d+\s*-\s*", "", txt).strip()
    alf = bool(re.match(r"^ALF\s*-\s*", n))
    n = re.sub(r"^(ALF|IRF)\s*-?\s*", lambda m: "IRF " if m.group(1) == "IRF" else "", n)
    out = " ".join(_palavra(w, i) for i, w in enumerate(n.split()))
    return f"Alfândega de {out}" if alf else out


# nome curto das NCMs do capítulo 31 que aparecem no estudo (a partir do texto oficial da NCM)
NCM_CURTO = {
    # café (D81)
    "09011110": "Café cru em grão",
    "09011190": "Café cru, exceto em grão",
    "09011200": "Café cru descafeinado",
    "09012100": "Café torrado",
    "09012200": "Café torrado descafeinado",
    "09019000": "Cascas e películas de café; sucedâneos",
    "21011110": "Café solúvel",
    "21011190": "Extratos e concentrados de café",
    "31010000": "Adubos de origem animal ou vegetal",
    "31021010": "Ureia (mais de 45% de N)",
    "31022100": "Sulfato de amônio",
    "31023000": "Nitrato de amônio",
    "31024000": "Nitrato de amônio com carbonato de cálcio",
    "31025090": "Outros nitratos de sódio",
    "31026000": "Nitrato de cálcio com nitrato de amônio",
    "31028000": "Ureia com nitrato de amônio em solução (UAN)",
    "31029000": "Outros nitrogenados",
    "31031100": "Superfosfatos com 35% ou mais de P₂O₅",
    "31031900": "Outros superfosfatos",
    "31039090": "Outros fosfatados",
    "31042010": "Cloreto de potássio com até 60% de K₂O",
    "31042090": "Cloreto de potássio (KCl)",
    "31043010": "Sulfato de potássio (até 52% de K₂O)",
    "31049090": "Outros potássicos",
    "31051000": "Adubos em tabletes ou embalagens de até 10 kg",
    "31052000": "NPK (nitrogênio, fósforo e potássio)",
    "31053000": "DAP (fosfato diamônico)",
    "31054000": "MAP (fosfato monoamônico)",
    "31055100": "Adubos com nitratos e fosfatos",
    "31055900": "Outros adubos com nitrogênio e fósforo",
    "31056000": "Adubos com fósforo e potássio",
    "31059090": "Outros adubos com nitrogênio e potássio",
}


def ncm(codigo: str, oficial: str) -> str:
    """Nome curto da NCM; sem nome curto, o texto oficial inteiro (nunca cortado)."""
    return NCM_CURTO.get(codigo, oficial)
