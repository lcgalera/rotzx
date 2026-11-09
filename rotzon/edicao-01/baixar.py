"""rotzOn #1 — passo 1: baixa do Comex Stat (MDIC) as importações do capítulo NCM 31 (adubos ou fertilizantes).

Fonte: API oficial https://api-comexstat.mdic.gov.br (dados abertos, mesma base do site https://comexstat.mdic.gov.br).
Só usa a biblioteca padrão do Python. Rodar da raiz do repositório:

    .venv/bin/python rotzon/edicao-01/baixar.py

Grava em rotzon/edicao-01/dados_brutos/:
  - atualizacao.json          data da última carga do MDIC (ano e mês mais recentes)
  - anual_pais_sh4.json       2015–2025, ano × país × SH4, kg líquido e US$ FOB
  - mensal_pais_sh4.json      2015–último mês, ano × mês × país × SH4, kg líquido e US$ FOB

Filtros usados (iguais aos do site, aba "Geral"):
  fluxo = importação (typeForm 2); filtro SH2 = 31; detalhamento = país + SH4; métricas = FOB e kg líquido.
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PASTA = Path(__file__).resolve().parent / "dados_brutos"
API = "https://api-comexstat.mdic.gov.br"
UA = {"User-Agent": "rotzon-newsletter (dados abertos)"}


def get(url: str, tentativas: int = 5) -> bytes:
    espera = 15
    for t in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                return r.read()
        except urllib.error.HTTPError as e:  # a API devolve 429 quando recebe muitas consultas
            if e.code != 429 or t == tentativas - 1:
                raise
            time.sleep(espera)
            espera *= 2
    raise RuntimeError("sem resposta")


def filtro(ano_ini: str, ano_fim: str, mensal: bool, mes_fim: str = "12") -> dict:
    return {
        "yearStart": ano_ini, "yearEnd": ano_fim,
        "typeForm": 2,                      # 1 = exportação, 2 = importação
        "typeOrder": 2,
        "filterList": [{"id": "noSh2pt"}],  # filtra por capítulo SH2...
        "filterArray": [{"item": ["31"], "idInput": "noSh2pt"}],  # ...= 31 (adubos ou fertilizantes)
        "rangeFilter": [],
        "detailDatabase": [{"id": "noPaispt", "text": ""}, {"id": "noSh4pt", "text": ""}],  # quebra por país e SH4
        "monthDetail": mensal,
        "metricFOB": True, "metricKG": True, "metricStatistic": False,
        "monthStart": "01", "monthEnd": mes_fim,
        "formQueue": "general", "langDefault": "pt",
    }


def consulta(f: dict, nome: str) -> None:
    corpo = get(f"{API}/general?filter=" + urllib.parse.quote(json.dumps(f)))
    dados = json.loads(corpo)
    assert dados["success"], dados
    saida = {"consulta": f, "baixado_em": time.strftime("%Y-%m-%d %H:%M:%S"), "linhas": dados["data"]["list"]}
    (PASTA / nome).write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{nome}: {len(saida['linhas'])} linhas")


def main() -> None:
    PASTA.mkdir(parents=True, exist_ok=True)
    atual = json.loads(get(f"{API}/general/dates/updated"))["data"]
    (PASTA / "atualizacao.json").write_text(json.dumps(atual, indent=1), encoding="utf-8")
    print("última carga do MDIC:", atual)
    consulta(filtro("2015", "2025", mensal=False), "anual_pais_sh4.json")
    time.sleep(15)
    consulta(filtro("2015", atual["year"], mensal=True), "mensal_pais_sh4.json")


if __name__ == "__main__":
    main()
