"""rotzOn #3 — passo 1: baixa do Comex Stat (MDIC) as exportações brasileiras de café.

Fonte: API oficial https://api-comexstat.mdic.gov.br (dados abertos, mesma base do site https://comexstat.mdic.gov.br).
Só usa a biblioteca padrão do Python. Rodar da raiz do repositório:

    .venv/bin/python rotzon/edicao-03/baixar.py

Grava em rotzon/edicao-03/dados_brutos/:
  - atualizacao.json          data da última carga do MDIC
  - cafe_pais_anual.json      exportação, SH4 0901 (café, mesmo torrado ou descafeinado), ano × país, 1997–último ano
  - cafe_ncm_anual.json       exportação, SH4 0901, ano × NCM (cru, torrado, descafeinado…), 1997–último ano
  - cafe_pais_mensal.json     exportação, SH4 0901, ano × mês × país, 2025–último mês (comparar períodos iguais)
  - extratos_ncm_anual.json   exportação, SH4 2101 (extratos de café, chá e mate), ano × NCM: separa o café solúvel
  - soluvel_pais_anual.json   exportação, SH4 2101, ano × país × NCM (o filtro de NCM do solúvel é aplicado no calcular.py)

Filtros (iguais aos do site, aba "Geral"): fluxo = exportação (typeForm 1); métricas = US$ FOB e kg líquido.
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
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
                return r.read()
        except urllib.error.HTTPError as e:  # a API devolve 429 quando recebe muitas consultas
            if e.code != 429 or t == tentativas - 1:
                raise
            time.sleep(espera)
            espera *= 2
    raise RuntimeError("sem resposta")


def filtro(ano_ini: str, ano_fim: str, sh4: str, detalhes: list, mensal: bool = False) -> dict:
    return {
        "yearStart": ano_ini, "yearEnd": ano_fim,
        "typeForm": 1,  # 1 = exportação
        "typeOrder": 2,
        "filterList": [{"id": "noSh4pt"}],
        "filterArray": [{"item": [sh4], "idInput": "noSh4pt"}],
        "rangeFilter": [],
        "detailDatabase": [{"id": d, "text": ""} for d in detalhes],
        "monthDetail": mensal,
        "metricFOB": True, "metricKG": True, "metricStatistic": False,
        "monthStart": "01", "monthEnd": "12",
        "formQueue": "general", "langDefault": "pt",
    }


def consulta(f: dict, nome: str) -> None:
    dados = json.loads(get(f"{API}/general?filter=" + urllib.parse.quote(json.dumps(f))))
    assert dados["success"], dados
    saida = {"consulta": f, "baixado_em": time.strftime("%Y-%m-%d %H:%M:%S"), "linhas": dados["data"]["list"]}
    (PASTA / nome).write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{nome}: {len(saida['linhas'])} linhas")
    time.sleep(15)


def main() -> None:
    PASTA.mkdir(parents=True, exist_ok=True)
    atual = json.loads(get(f"{API}/general/dates/updated"))["data"]
    (PASTA / "atualizacao.json").write_text(json.dumps(atual, indent=1), encoding="utf-8")
    print("última carga do MDIC:", atual)
    fim = atual["year"]
    consulta(filtro("1997", fim, "0901", ["noPaispt"]), "cafe_pais_anual.json")
    consulta(filtro("1997", fim, "0901", ["noNcmpt"]), "cafe_ncm_anual.json")
    consulta(filtro("2025", fim, "0901", ["noPaispt"], mensal=True), "cafe_pais_mensal.json")
    consulta(filtro("1997", fim, "2101", ["noNcmpt"]), "extratos_ncm_anual.json")
    consulta(filtro("1997", fim, "2101", ["noPaispt", "noNcmpt"]), "soluvel_pais_anual.json")


if __name__ == "__main__":
    main()
