# rotzOn: "O mundo, explicado daqui"

Newsletter semanal sobre como o Brasil se conecta ao mundo, com **um** mapa ou gráfico por edição, só com dados abertos e oficiais.

```
rotzon/
├── README.md                 este arquivo
├── calendario-12-semanas.md  (Tarefa 2)
├── rotina-e-metas.md         (Tarefa 3)
└── edicao-01/                "O agro brasileiro depende de um navio"
    ├── baixar.py             1. baixa do Comex Stat → dados_brutos/
    ├── calcular.py           2. tabelas → tabelas/
    ├── graficos.py           3. CSVs do Datawrapper + PNGs → visuais/
    ├── dados_brutos/         respostas da API (com a consulta exata) + geometria do mapa
    ├── tabelas/              todas as contas em CSV
    ├── visuais/              mapa_fornecedores_2025.csv/.png, china_vs_russia.csv/.png
    ├── newsletter.md         texto da edição
    ├── post_linkedin.md      ≤ 1.300 caracteres
    ├── post_x.md             ≤ 280 caracteres
    └── checklist.md          cada número, de onde veio, se foi confirmado
```

## Como refazer a edição #1 do zero

Precisa de Python 3.9+ e internet (o domínio `api-comexstat.mdic.gov.br` e o registro do npm).

1. Ambiente (uma vez só):

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install pandas matplotlib pycountry
```

2. Baixar os dados (cerca de 1 min; a API às vezes devolve 429, e o script espera e tenta de novo):

```bash
.venv/bin/python rotzon/edicao-01/baixar.py
```

3. Calcular as tabelas (imprime o resumo na tela):

```bash
.venv/bin/python rotzon/edicao-01/calcular.py
```

4. Gerar os CSVs do Datawrapper e as prévias:

```bash
.venv/bin/python rotzon/edicao-01/graficos.py
```

Rode os comandos a partir da raiz do repositório (o `graficos.py` lê `catalog/paises_mundo.csv`).

### Filtros usados (iguais aos do site, pra conferir à mão)
No [Comex Stat › Geral](https://comexstat.mdic.gov.br/pt/geral):
- **Fluxo:** Importação
- **Período:** 2015 a 2025 (anual) e jan/2015 a último mês (mensal, com "Detalhar por mês")
- **Filtro:** SH2 = 31 (Adubos ou fertilizantes)
- **Detalhamento:** País + SH4
- **Valores:** US$ FOB e Quilograma líquido

O site exporta CSV com os mesmos números. Se a API falhar, baixe o CSV pelo site e adapte a função `carregar()` do `calcular.py`.

### No Datawrapper
- **Mapa:** Choropleth map › World. Na hora de casar os países, use a coluna `ISO3`. Faixas: até 100 / 100–500 / 500–2.000 / 2.000–5.000 / mais de 5.000 mil t. País sem dado = "sem registro" (nunca zero).
- **Linha:** cole `china_vs_russia.csv` (mil toneladas).

## Regras da casa
- Só dado aberto e oficial (Comex Stat, IBGE, BCB, Banco Mundial, Conab, ONU). Nada de Macrodados nem de fonte paga.
- Todo número vem de um dado baixado ou de uma fonte com link. O que não deu pra confirmar vira **[VERIFICAR]** no `checklist.md`.
- Participação sempre com o denominador dito. Dado ausente é "sem registro", nunca zero.
- Reportagem se parafraseia, não se copia.
