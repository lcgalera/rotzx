# Checklist da edição #2: cada número, de onde veio e se foi confirmado

Legenda: ✅ confirmado nos dados baixados nesta sessão · ⚠️ confirmado com ressalva · ❌ [VERIFICAR]

Comex Stat = API oficial do MDIC, **exportação**, US$ FOB, carga de 06/11/2026 (dados até out/2026). Arquivos brutos em `dados_brutos/`, tabelas em `tabelas/`.
Conferências feitas pelo `calcular.py`: soma por SH4 = total por país para a China (diferença 0); para o mundo, a diferença é de US$ 6.241 sobre US$ 348 bi (arredondamento); soma mensal 2025 = anual 2025 (diferença 0).

| # | Número no texto | Valor exato | Arquivo | Status |
|---|---|---|---|---|
| 1 | China é a nº 1 desde 2009, quando passou os EUA | coluna `lider`: EUA até 2008, China de 2009 em diante | `tabelas/1_china_no_total.csv` | ✅ |
| 2 | US$ 99,9 bi exportados para a China em 2025 | US$ 99,940 bi | idem | ✅ |
| 3 | 28,7% do total exportado em 2025 | 99,94 ÷ 348,3 | idem | ✅ |
| 4 | EUA: US$ 37,7 bi, 10,8% | idem | idem | ✅ |
| 5 | "mais de 2,5 vezes" o que os EUA compraram | 99,9 ÷ 37,7 = 2,65 | idem | ✅ |
| 6 | Em 1997 a China era a 12ª | `China_pos` = 12 | idem | ✅ |
| 7 | Trio = 74,2% das exportações para a China em 2025 | 34,53 + 20,06 + 19,59 | `tabelas/2_top10_china_2025.csv`, `3_concentracao_anual.csv` | ✅ |
| 8 | Soja 34,5% · petróleo bruto 20,1% · minério 19,6% (2025) | idem | idem | ✅ |
| 9 | Para o mundo, os 3 maiores = 33,6% | `mundo_top3_%` 2025 | `3_concentracao_anual.csv`, `2b_top10_mundo_2025.csv` | ✅ (em 2025 os 3 maiores para o mundo são o mesmo trio) |
| 10 | "o peso dos três maiores é mais que o dobro" (LinkedIn) | 74,2 ÷ 33,6 = 2,21 | idem | ✅ |
| 11 | Trio era 24,7% em 1997 | 8,3 (soja) + 16,5 (minério) + 0 (petróleo) | `3_concentracao_anual.csv` | ✅ |
| 12 | Desde 2006, nunca abaixo de 68,8%; pico 82,2% em 2018 | mín. 68,8 (2007), máx. 82,2 (2018), 2006–2025 | idem | ✅ |
| 13 | Minério dominava por volta de 2011, com 44,7% | `china_2601_%` 2011 = 44,7 (máximo da série) | idem | ✅ |
| 14 | Petróleo "de quase nada" para 20,1% | 0,0% em 1997–1999 e 2002; 20,1% em 2025 | idem | ✅ |
| 15 | Jan–out/2026: US$ 93,1 bi, US$ 8,5 bi a mais que jan–out/2025 | 93,1 × 84,7 (+10,0%); diferença 8,45 | `tabelas/6_china_jan_out_2025_2026.csv` | ✅ |
| 16 | Desse aumento, US$ 7,9 bi do petróleo | 24,42 − 16,51 = 7,91 | idem | ✅ |
| 17 | 2026 "reforça a concentração" | trio jan–out: 75,6% (2025) × 77,0% (2026) | saída do `calcular.py`, seção 6 | ✅ |
| 18 | "Outros" em cerca de 1/4 do total | 25,1% (2015) e 25,8% (2025) | `visuais/china_pauta_trio.csv` | ✅ |
| 19 | "Outros": US$ 8,8 bi (2015) → US$ 25,8 bi (2025), "quase triplicou" | 8,82 → 25,81 (×2,93) | seção 5 do `calcular.py` | ✅ |
| 20 | Carne bovina congelada: US$ 0,46 bi (2015) → US$ 8,8 bi (2025), 19 vezes | 0,461 → 8,843 (×19,2) | `tabelas/5_maiores_altas_fora_do_trio.csv` | ✅ |
| 21 | Carne é "a maior responsável" pela alta dos outros | +US$ 8,38 bi, a maior alta fora do trio | idem | ✅ |
| 22 | 61% da carne bovina congelada exportada vai para a China (2025); 12% em 2015 | 61,2% e 11,7% | `tabelas/4_china_no_destino_de_cada_produto.csv` | ✅ |
| 23 | Jan–out/2026: carne bovina congelada −17,8%, US$ 7,1 → 5,8 bi | 7,06 → 5,80 | `6_china_jan_out_2025_2026.csv` | ✅ |
| 24 | Jan–out/2026: frango (0207) US$ 0,5 → 1,3 bi | 0,54 → 1,28 | idem | ✅ |
| 25 | 841 produtos (SH4) com registro em 2025; 7 acima de US$ 1 bi | saída do `calcular.py`, seção 2 | — | ✅ |
| 26 | China levou 79% da soja, 68% do minério, 45% do petróleo bruto exportados em 2025 | 79,3% · 67,6% · 45,0% | `4_china_no_destino_de_cada_produto.csv` | ✅ |
| 27 | Edição passada: China passou a Rússia no adubo, em toneladas, em 2025 | edição #1 | `../edicao-01/checklist.md` | ✅ |

## Afirmações que não são número
- **"Quando o preço da soja ou do minério muda, ou quando a China compra mais ou menos, uma fatia enorme das exportações muda junto":** é aritmética (valor = preço × quantidade), não previsão. O texto não atribui nenhuma variação a uma causa específica.
- **Queda da carne em 2026:** o texto só mostra o número e **não diz por quê**. Se for explicar, precisa de fonte com link.

## Ressalvas de método
- Valores em **US$ correntes** (sem descontar a inflação americana). Comparar 1997 com 2025 em dólar nominal exagera o crescimento. As participações (%) não têm esse problema.
- "Produtos" = posições SH4 (agrupamentos de 4 dígitos), não itens individuais. Com NCM de 8 dígitos o número seria maior.
- País de destino no Comex é o declarado na exportação. Mercadoria que passa por outro país (Hong Kong, Cingapura) pode aparecer com esse destino.
- 2026 sempre como **jan–out**, comparado com jan–out de 2025.
- Link que não abriu a partir do ambiente desta sessão: comexstat.mdic.gov.br (clicar antes de publicar).
