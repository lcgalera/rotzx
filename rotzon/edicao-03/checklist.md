# Checklist da edição #3: cada número, de onde veio e se foi confirmado

Legenda: ✅ confirmado nos dados baixados nesta sessão · ⚠️ confirmado com ressalva · ❌ [VERIFICAR]

Comex Stat = API oficial do MDIC, **exportação**, SH4 0901, carga de 06/11/2026 (dados até out/2026). Arquivos brutos em `dados_brutos/`, tabelas em `tabelas/`.
Conferências feitas pelo `calcular.py`: soma por país = soma por NCM (diferença 0); soma mensal 2025 = anual 2025 (diferença 0).
Participação = kg do país ÷ kg total exportado de café no mesmo ano.

| # | Número no texto | Valor exato | Arquivo | Status |
|---|---|---|---|---|
| 1 | Top 5 de 1997 = top 5 de 2025, os 4 primeiros na mesma ordem | 1997: Alemanha, EUA, Itália, Japão, Bélgica; 2025: idem | `tabelas/3a_ranking_1997_kg.csv`, `3b_ranking_2025_kg.csv` | ✅ |
| 2 | Os cinco somaram 49,6% do volume em 2025 | 14,97 + 12,90 + 8,58 + 6,58 + 6,57 | `3b_ranking_2025_kg.csv` | ✅ |
| 3 | Líder: Alemanha em 16 anos e EUA em 13 (1997–2025); EUA na frente em jan–out/2026 | contagem da coluna `kg` | `tabelas/3c_lider_por_ano.csv` | ✅ |
| 4 | "Desde 1997, o maior comprador foi sempre Alemanha ou EUA" (dado pra guardar) | 1997–2025 + jan–out/2026 | idem | ✅ (em US$ também: 17 × 13 com 2026) |
| 5 | Argentina, Suécia, França e Grécia saíram do top 10 | posições em 2025: 20ª, 17ª, 11ª, 18ª | `tabelas/4_slope_1997_2025.csv` | ✅ |
| 6 | Argentina: 6ª em 1997 → 20ª em 2025 | idem | idem | ✅ |
| 7 | Entraram Turquia, Holanda, Rússia e China | posições em 1997: 19ª, 13ª, 62ª, 55ª; em 2025: 6ª, 7ª, 9ª, 10ª | idem | ✅ |
| 8 | Colômbia: sem registro em 1997, 16ª em 2025 (1,9%) | ausente do ranking de 1997; pos 16, 1,89% | `3a_…`, `3b_…` | ✅ |
| 9 | 139 países em 2025, 73 em 1997 | países com kg > 0 | `tabelas/1_total_anual.csv` (`n_paises`) | ✅ |
| 10 | Top 10: 75,8% (1997) → 66,8% (2025) | saída do `calcular.py`, seção 3 | — | ✅ |
| 11 | 37,9 milhões de sacas em 2025 | 37,90 mi (kg ÷ 60) | `1_total_anual.csv` | ✅ |
| 12 | −18% contra 2024; recorde de 2024 = 46,2 milhões de sacas | −18,0%; 46,21 mi (maior da série 1997–2025) | idem | ✅ |
| 13 | US$ 14,9 bi FOB em 2025, +31% sobre 2024 | 14,92; +31,2% | idem | ✅ |
| 14 | Maior valor desde 1997 | máximo da série 1997–2025 = 2025 | idem | ✅ (a série do Comex Stat começa em 1997; antes disso não foi checado) |
| 15 | Saca média: US$ 394 (2025), 246 (2024), 190 (1997), 46 (2002) | 393,7 · 246,1 · 189,7 · 46,3 | idem (`us$_por_saca` = FOB ÷ sacas) | ✅ |
| 16 | Jan–out/2026: volume −1,8%, valor −8,9%, saca US$ 357 | 30,8 → 30,3 mi sacas; US$ 11,88 → 10,81 bi | seção 7 do `calcular.py` | ✅ |
| 17 | Nenhum país passa de 15% do volume (2025) | maior = Alemanha, 14,97% | `3b_ranking_2025_kg.csv` | ✅ |
| 18 | China: 10ª, 3,0% do volume em 2025 | pos 10; 2,97% | idem | ✅ |
| 19 | China: 18ª em jan–out/2026 | seção 6 do `calcular.py` (posição por ano) | — | ✅ |
| 20 | China leva 79% da soja (edição #2) | 79,3% | `../edicao-02/tabelas/4_china_no_destino_de_cada_produto.csv` | ✅ |
| 21 | China é a maior compradora do Brasil no geral (edição #2) | nº 1 desde 2009 | `../edicao-02/tabelas/1_china_no_total.csv` | ✅ |
| 22 | 99,6% do valor do 0901 em 2025 é café cru em grão | NCM 09011110 = 99,63% | `tabelas/2_composicao_ncm_2025.csv` | ✅ |
| 23 | 1 saca = 60 kg | convenção do setor, usada só como unidade | — | ✅ (definição, não dado) |

## Afirmações que não são número
- **"A clientela ficou mais espalhada":** é a leitura direta de dois números (países 73 → 139; top 10 75,8% → 66,8%).
- **Preço:** o texto mostra a alta e **não diz por quê** (clima, safra, bolsa). Para explicar a causa, precisa de fonte com link.
- **Colômbia como produtora de café:** foi tirado do texto por não ter sido checado com dado nesta edição. Se quiser voltar com isso, use uma fonte de produção por país (FAOSTAT ou Organização Internacional do Café), depois de conferir a licença.

## Ressalvas de método
- Volume em **kg líquido** de café cru em grão, na maior parte. Sacas = kg ÷ 60.
- Valores em **US$ correntes**: comparar 1997 com 2025 sem descontar a inflação exagera a alta.
- O país de destino é o declarado na exportação. ❌ [VERIFICAR] Hipótese não checada: parte do café enviado a países com grandes portos (como Bélgica e Holanda) pode seguir para outros países. Isso **não está no texto**; se for citar, precisa de fonte.
- O café solúvel (NCM 21011110, US$ 1,09 bi em 2025) ficou de fora das contas, e o texto avisa nas fontes.
- Link que não abriu a partir do ambiente desta sessão: comexstat.mdic.gov.br (clicar antes de publicar).
