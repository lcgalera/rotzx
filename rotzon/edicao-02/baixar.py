"""rotzOn #2 — passo 1: baixa do Comex Stat (MDIC) as exportações brasileiras para a China e para o mundo, por produto (SH4).

Fonte: API oficial https://api-comexstat.mdic.gov.br (dados abertos, mesma base do site https://comexstat.mdic.gov.br).
Só usa a biblioteca padrão do Python. Rodar da raiz do repositório:

    .venv/bin/python rotzon/edicao-02/baixar.py

Grava em rotzon/edicao-02/dados_brutos/:
  - atualizacao.json            data da última carga do MDIC
  - china_sh4_anual.json        exportação, país = China (código 160), ano × SH4, 1997–último ano (o último vem parcial)
  - mundo_sh4_anual.json        exportação, todos os países, ano × SH4, 1997–último ano
  - china_sh4_mensal.json       exportação para a China, ano × mês × SH4, 2025–último mês (comparar períodos iguais)
  - paises_anual.json           exportação por país, ano × país, 1997–último ano (peso e posição da China)

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
CHINA = "160"  # código do país no Comex Stat (coluna `comex` de catalog/paises_mundo.csv)


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


def filtro(ano_ini: str, ano_fim: str, detalhes: list, mensal: bool = False, pais: str = None) -> dict:
    f = {
        "yearStart": ano_ini, "yearEnd": ano_fim,
        "typeForm": 1,  # 1 = exportação, 2 = importação
        "typeOrder": 2,
        "filterList": [], "filterArray": [], "rangeFilter": [],
        "detailDatabase": [{"id": d, "text": ""} for d in detalhes],
        "monthDetail": mensal,
        "metricFOB": True, "metricKG": True, "metricStatistic": False,
        "monthStart": "01", "monthEnd": "12",
        "formQueue": "general", "langDefault": "pt",
    }
    if pais:
        f["filterList"] = [{"id": "noPaispt"}]
        f["filterArray"] = [{"item": [pais], "idInput": "noPaispt"}]
    return f


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
    consulta(filtro("1997", fim, ["noSh4pt"], pais=CHINA), "china_sh4_anual.json")
    consulta(filtro("1997", fim, ["noSh4pt"]), "mundo_sh4_anual.json")
    consulta(filtro("2025", fim, ["noSh4pt"], mensal=True, pais=CHINA), "china_sh4_mensal.json")
    consulta(filtro("1997", fim, ["noPaispt"]), "paises_anual.json")


if __name__ == "__main__":
    main()
