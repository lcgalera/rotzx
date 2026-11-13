# Formato dos arquivos de detalhamento do atlas (`rotzx.detalhe.v1`)

Contrato entre o **projeto de dados** (que coleta, limpa e gera os arquivos) e a **página**
(`prototipos/globo/index.html`), que só os lê. Decisão: D61.

## Onde ficam

```
prototipos/globo/dados/detalhe/
  indice.json              o que existe (a página lê este arquivo ao abrir)
  prod/{codigo}.json       um por produto: SH4 ("3105") ou grupo ("g-fertilizantes")
  pais/{iso3}.json         um por país ou território: ISO 3166 alfa-3 ("CHN")
```

- O build público copia a pasta inteira para o site, sem nenhum passo extra.
- A página busca `prod/` e `pais/` com `fetch` **só quando a pessoa abre** aquele produto ou país, e guarda em memória.
- Sem `indice.json`, ou com falha de rede, a página funciona como antes, com a distribuição por parceiro só em 2000, 2010 e 2025, vinda de `produtos.js` e `historia.js`.
- Um produto ou país que não aparece no índice nunca é buscado (não há 404 à toa).
- Arquivos em JSON UTF-8, sem espaços desnecessários. Recomendado: até 300 KB por arquivo.

## Regras que valem para tudo

1. **Só dado real**, com `fonte`, `consulta` e `gerado_em`. Nada estimado nem interpolado.
2. **Ano ausente = sem registro**, nunca zero. Não grave anos vazios nem valores `0`.
3. **Valores** em número (não texto), em **US$ FOB correntes**, sem arredondar. A unidade vai em `unidade`.
4. **Recorte com denominador:** cada bloco `{t, n, top}` traz
   - `t`: total do bloco, que é o **denominador** das participações;
   - `n`: quantos itens distintos a fonte registra com valor > 0;
   - `top`: os maiores, em ordem decrescente de valor.

   `t − soma(top)` aparece como "Outros", e a página nunca atribui esse resto a um item.
5. **Fluxo** sempre visto do Brasil: `"e"` = exportações brasileiras, `"i"` = importações brasileiras.
6. **Códigos de país** em `top` de parceiros: ISO 3166 **numérico com 3 dígitos, em texto** ("156"), o mesmo de `catalog/paises_mundo.csv` (`iso_num`). Para passar do nome do Comex Stat ao código, use essa tabela.
7. **`t` dos parceiros** = total **com país identificado**. A série anual nacional pode ser maior, porque inclui operações sem país, como provisões de bordo. A página já explica a diferença.

## `indice.json`

```text
{
  "schema": "rotzx.detalhe.v1",
  "gerado_em": "2026-11-20T12:00:00Z",
  "fonte": "Comex Stat (MDIC)",
  "licenca": "dados abertos (MDIC)",
  "prod": {
    "3105": { "anos_parceiros": [1997, 1998, "…", 2025], "camadas": ["parceiros", "uf", "via", "urf", "ncm"] },
    "g-fertilizantes": { "anos_parceiros": [2015, 2016, "…", 2025], "camadas": ["parceiros", "via"] }
  },
  "pais": {
    "CHN": { "anos_produtos": [1997, "…", 2025], "camadas": ["produtos", "uf", "via", "urf"] }
  }
}
```

- `anos_parceiros` e `anos_produtos`: os anos (inteiros) que o arquivo traz em `parceiros` ou `produtos`. A página usa essas listas para montar a linha do tempo antes de baixar o arquivo, e junta com 2000, 2010 e 2025.
- `camadas`: o que o arquivo contém. É informativo, e ajuda a conferir o arquivo.

## `prod/{codigo}.json`

```text
{
  "schema": "rotzx.detalhe.v1",
  "codigo": "3105",
  "nome": "Adubos minerais ou químicos com dois ou três elementos fertilizantes",
  "fonte": "Comex Stat (MDIC)",
  "consulta": "api-comexstat.mdic.gov.br /general; detailDatabase=[noPaispt]; filtro coSh4=3105; 1997–2025",
  "gerado_em": "2026-11-20T12:00:00Z",
  "unidade": "US$ FOB correntes",
  "parceiros": {
    "i": { "2025": { "t": <total>, "n": <n>, "top": [["643", <valor>], ["156", <valor>]] } },
    "e": { "2025": { "t": <total>, "n": <n>, "top": [["600", <valor>]] } }
  },
  "uf":  { "i": { "2025": { "t": <total>, "n": <n>, "top": [["MT", <valor>], ["PR", <valor>]] } } },
  "via": { "i": { "2025": { "t": <total>, "n": <n>,  "top": [["MARITIMA", <valor>], ["RODOVIARIA", <valor>]] } } },
  "urf": { "i": { "2025": { "t": <total>, "n": <n>, "top": [["<código URF>", "<nome da unidade>", <valor>]] } } },
  "ncm": { "i": { "2025": { "t": <total>, "n": <n>,  "top": [["<NCM, 8 dígitos>", "<descrição oficial>", <valor>]] } } }
}
```

*Os marcadores `<total>`, `<n>` e `<valor>` mostram onde vão os números reais: no arquivo, são números, nunca texto. Os nomes e códigos acima também são só exemplo de forma.*

| Camada | Item de `top` | Quantos itens | Observação |
|---|---|---|---|
| `parceiros` | `[iso_num, valor]` | até 12 (pode mandar mais) | é a "distribuição por parceiro" usada no mapa e no explorador |
| `uf` | `[sigla_uf, valor]` | todas as UFs com valor | sigla oficial (SP, MT, …); UF de origem (exportação) ou de destino (importação), como no Comex Stat |
| `via` | `[nome_via, valor]` ou `[código, nome, valor]` | todas | ex.: MARITIMA, AEREA, RODOVIARIA, FERROVIARIA |
| `urf` | `[código_urf, nome, valor]` | até 15 | unidade da Receita (porto, aeroporto, fronteira) |
| `ncm` | `[ncm_8, descrição_oficial, valor]` | até 15 | descrição oficial do ano; só para SH4 (grupos podem omitir) |

## `pais/{iso3}.json`

```text
{
  "schema": "rotzx.detalhe.v1",
  "iso3": "CHN",
  "iso_num": "156",
  "fonte": "Comex Stat (MDIC)",
  "consulta": "…",
  "gerado_em": "2026-11-20T12:00:00Z",
  "unidade": "US$ FOB correntes",
  "produtos": {
    "e": { "1997": { "t": <total>, "n": <n>, "top": [["1201", <valor>], ["2601", <valor>]] } },
    "i": { "1997": { "t": <total>, "n": <n>, "top": [["8517", <valor>]] } }
  },
  "uf":  { "e": { "2025": { "t": <total>, "n": <n>, "top": [["MT", <valor>]] } } },
  "via": { "e": { "2025": { "t": <total>, "n": <n>, "top": [["MARITIMA", <valor>]] } } },
  "urf": { "e": { "2025": { "t": <total>, "n": <n>, "top": [["<código URF>", "<nome da unidade>", <valor>]] } } }
}
```

- `produtos`: composição do comércio com o país por SH4, `top` com **pelo menos 10** itens `[sh4, valor]`. Substitui ou estende os anos de `historia.js`, que hoje tem 2000, 2010 e 2025.
- `t` de `produtos` = total trocado com o país no ano, no fluxo. É o mesmo valor de `historia.js` nos anos em que os dois existem.

## Como conferir antes de publicar

```bash
.venv/bin/python -m rotzx detalhe-validar prototipos/globo/dados/detalhe
```

O comando falha (código de saída 1) e lista os problemas encontrados:
- campo obrigatório faltando;
- `top` fora de ordem;
- soma de `top` maior que `t`;
- valor zero ou negativo;
- ano fora de 1997–(ano atual);
- código de país que não está na tabela `catalog/paises_mundo.csv`;
- produto ou país no índice sem arquivo (e vice-versa).

Os testes do repositório rodam o mesmo validador sobre a pasta, se ela existir.
