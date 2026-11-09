# Checklist da edição #1: cada número, de onde veio e se foi confirmado

Legenda: ✅ confirmado nos dados baixados nesta sessão ou numa fonte oficial aberta · ⚠️ confirmado com ressalva · ❌ [VERIFICAR]

Comex Stat = API oficial do MDIC, importação, capítulo NCM 31, carga de 06/11/2026 (dados até out/2026). Os arquivos estão em `dados_brutos/` e as tabelas em `tabelas/`.

| # | Número no texto | Valor exato | Fonte / arquivo | Status |
|---|---|---|---|---|
| 1 | 85% do fertilizante consumido é importado | "85% do fertilizante consumido é importado" | MAPA, apresentação na Câmara, 30/09/2025, slide 4 (rodapé: "Adapted Comex Stat, 2025") | ⚠️ número oficial e arredondado; o slide não detalha a conta. O slide 3 do mesmo PDF ("produção nacional 2024: 7,21 Mton (17%)") é coerente com ele |
| 2 | 45,5 milhões de t importadas em 2025 | 45.504,6 mil t | `tabelas/1_total_anual.csv` | ✅ |
| 3 | 19,8 milhões de t em 2015 | 19.809,9 mil t | idem | ✅ |
| 4 | "mais que o dobro" (+130%) | +129,7% | idem | ✅ |
| 5 | US$ 15,5 bi FOB em 2025 | US$ 15,49 bi | idem | ✅ |
| 6 | China 12,0 mi t (26,3%) em 2025 | 11.985,6 mil t; 26,34% do total do cap. 31 em kg | `tabelas/2_top5_2025_kg.csv`, `3_china_russia_anual.csv` | ✅ |
| 7 | Rússia 11,1 mi t (24,4%) em 2025 | 11.086,7 mil t; 24,36% | idem | ✅ |
| 8 | China ×6,5 e Rússia ×3 em dez anos (volume) | 11.985,6/1.841,7 = 6,51; 11.086,7/3.743,1 = 2,96 | `3_china_russia_anual.csv` | ✅ |
| 9 | Metade das toneladas (China + Rússia) | 50,70% | `2_top5_2025_kg.csv` | ✅ |
| 10 | Canadá 11,4%; top 3 somam 62,1% | 11,35%; 62,05% | idem | ✅ |
| 11 | Rússia US$ 4,0 bi × China US$ 2,9 bi | US$ 4,003 bi × US$ 2,908 bi | `2_top5_2025_fob.csv` | ✅ |
| 12 | Dois terços do que vem da China são nitrogenados | 67,2% das t chinesas no SH4 3102 | cálculo em `calcular.py` (mix por SH4) | ✅ |
| 13 | Tonelada média China US$ 243 × Rússia US$ 361 | FOB ÷ kg, 2025 | idem | ✅ |
| 14 | Jan–out/2026: Rússia 7,1 mi t × China 6,6 mi t | 7.105,2 × 6.638,9 mil t | `3_china_russia_anual.csv` (linha 2026) | ✅ |
| 15 | Jan–out/2026: 32,7 mi t, −14,7% sobre jan–out/2025 | 32.695,7 × 38.311,9 mil t | `1_total_anual.csv` (coluna jan–out) | ✅ |
| 16 | 2026: Canadá 38,2% × Rússia 30,0% no potássio | participação no SH4 3104, kg | `4_lider_por_nutriente.csv` | ✅ |
| 17 | 2026: Marrocos 29,6% × Egito 28,0% no fósforo | participação no SH4 3103, kg | idem | ✅ |
| 18 | 2026: Turcomenistão 6,2% (top 5) | 6,16% | `2b_top5_2026_jan_out_kg.csv` | ✅ |
| 19 | Nitrogênio: China 45,9% em 2025 | participação no SH4 3102, kg | `4_lider_por_nutriente.csv` | ✅ |
| 20 | Potássio: Rússia 44,6% + Canadá 37,2% ("mais de 80%") | soma 81,8% | idem | ✅ |
| 21 | Fósforo: líderes Egito e Marrocos | Egito 31,1% (kg); Marrocos 36,2% (US$) | idem | ✅ |
| 22 | 2022: −8% em toneladas, +63% em gasto, US$ 24,7 bi | kg −8,3%; FOB +63,1%; US$ 24,73 bi | `1_total_anual.csv` | ✅ |
| 23 | Tonelada média US$ 365 (2021) → US$ 649 (2022) | FOB ÷ kg do total | idem | ✅ |
| 24 | Meta do PNF: 50% de dependência até 2050 | "Reduzir de 85% para 50%..." | MAPA, slide 2; página do PNF no gov.br | ✅ |
| 25 | "quase 1 em cada 4 t" da China e da Rússia (dado pra guardar) | 26,3% e 24,4% | itens 6 e 7 | ✅ ("quase" vale pra Rússia; a China passou um pouco de 1/4) |

## Afirmações que não são número, e como foram tratadas
- **"Por anos, a Rússia foi a maior vendedora":** ✅ a Rússia foi a nº 1 em kg em todos os anos de 2015 a 2024. O vice foi o Canadá até 2020 e a China de 2021 a 2024 (`tabelas/2c_lider_por_ano_kg.csv`).
- **"Quando acontece alguma coisa num desses países (uma guerra...)":** é exemplo genérico, sem atribuir causa a nenhum evento. O texto **não** diz que a guerra na Ucrânia causou a alta de 2022. Só mostra os números do ano.
- **Fosfatados/nitrogenados/potássicos = P/N/K:** é a definição dos SH4 3102–3104 na própria NCM.

## Ressalvas de método
- Volume = **kg líquido** declarado na importação. É peso do produto, **não** de nutriente puro (N, P₂O₅, K₂O). Por isso não dá pra comparar diretamente com estatísticas em "toneladas de nutriente".
- O Brasil aparece como "origem" em 87 t em 2025 (reimportação): fica no total, mas fora do mapa.
- 3105 inclui MAP/DAP e misturas NPK. A NCM 31 não separa adubo de uso agrícola de outros usos.
- Links que **não** abriram a partir do ambiente desta sessão e precisam de um clique antes de publicar: comexstat.mdic.gov.br e o PDF da Câmara (este o autor abriu e mandou).
