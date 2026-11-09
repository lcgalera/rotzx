# Calendário rotzOn: 12 semanas

**Publicação às sextas.** Lançamento sugerido: **sexta, 04/12/2026**, com as edições #1 a #3 prontas antes (meta da rotina). Daí a 12ª edição cai em 19/02/2027.

Três coisas que o calendário leva em conta:
- **25/12 e 01/01 caem numa sexta.** Pra essas semanas ficaram pautas leves, com uma consulta só. Se quiser folgar, as duas pautas de emergência (no fim) cabem ali.
- **O fechamento de 2026 sai no começo de janeiro.** O MDIC costuma divulgar o resultado anual da balança comercial na primeira semana útil do ano [conferir data no calendário de divulgação do MDIC]. Da semana 6 em diante, dá pra usar **2026 fechado** em vez de "jan–out".
- **Carnaval 2027 é em 09/02 (terça).** A semana 11 tem a terça e a quarta curtas.

Regra pra todas: nenhum número entra no título antes de ser baixado e conferido. Os títulos abaixo são provisórios e os ganchos são de calendário ou de dado, não de notícia. Notícia da semana, se houver, entra na segunda-feira, com link.

**Alcance das fontes:** Comex Stat, BCB, Banco Mundial e ANP abriram a partir do ambiente de trabalho do Claude em 09/11/2026. IBGE, UN Comtrade, Conab, USGS e Ipeadata **não abriram ali**, mas no seu computador devem abrir normalmente. Pautas que dependem delas estão marcadas com 🖐️ (download manual).

---

## Visão geral

| Sem. | Data | # | Pauta | Frente | Visual | Fonte principal |
|---|---|---|---|---|---|---|
| 1 | 04/12/2026 | 1 | Fertilizantes: China × Rússia | economia + geopolítica | linha | Comex Stat |
| 2 | 11/12/2026 | 2 | O que o Brasil vende pra China além de soja | economia | barras empilhadas / treemap | Comex Stat |
| 3 | 18/12/2026 | 3 | Café: quem compra e como mudou | história + economia | slope (1997 × 2025) | Comex Stat |
| 4 | 25/12/2026 | 4 | 🎄 Quem come a carne brasileira | economia (leve) | mapa | Comex Stat |
| 5 | 01/01/2027 | 5 | ✈️ Quanto o Brasil gasta viajando lá fora | economia (leve) | linha | BCB |
| 6 | 08/01/2027 | 6 | O Brasil na rota do petróleo | geopolítica + economia | barras divergentes | Comex Stat (+ ANP) |
| 7 | 15/01/2027 | 7 | Minerais críticos: nióbio, lítio, terras raras | geopolítica | mapa | Comex Stat (+ USGS 🖐️) |
| 8 | 22/01/2027 | 8 | Brasil–Argentina ao longo das décadas | história | linha longa | Comex Stat (+ Comtrade/IBGE 🖐️) |
| 9 | 29/01/2027 | 9 | De onde vêm os remédios do Brasil | geopolítica + economia | mapa | Comex Stat |
| 10 | 05/02/2027 | 10 | China × EUA: quem é o maior cliente do Brasil | história + geopolítica | linha | Comex Stat |
| 11 | 12/02/2027 | 11 | Quem investe no Brasil | economia | barra | BCB |
| 12 | 19/02/2027 | 12 | De onde vêm os chips e celulares do Brasil | geopolítica | mapa | Comex Stat |
| ⚡ | reserva | E1 | A virada China × Rússia continua? | atualização | linha | Comex Stat |
| ⚡ | reserva | E2 | Pra quantos países o Brasil vende? | economia | mapa | Comex Stat |

---

## As 12 edições

### Semana 1 · 04/12/2026 · #1 · O agro brasileiro depende de um navio ✅ pronta
- **Pergunta:** de quem o Brasil compra o adubo que usa, e o quanto isso está concentrado?
- **Fonte:** Comex Stat, importação, SH2 = 31, país × SH4, kg líquido e US$ FOB.
- **Visual:** linha China × Rússia 2015–2025.
- **Por que agora:** 2025 foi o primeiro ano da série em que a China passou a Rússia em toneladas.

### Semana 2 · 11/12/2026 · #2 · "A China compra soja do Brasil. E o que mais?"
- **Pergunta:** quanto da exportação brasileira pra China é soja, minério de ferro e petróleo, e quanto sobra pro resto?
- **Fonte:** Comex Stat, **exportação**, país = China, detalhamento SH4, US$ FOB, 1997–2025 (e 2026 jan–nov se já tiver saído).
- **Filtros:** `typeForm 1`, filtro `noPaispt = China`, detalhe `noSh4pt`. A conta é a participação dos 3 maiores SH4 no total exportado pra China (denominador dito). Pra comparação, faça a mesma conta com o total exportado pro mundo.
- **Visual:** barra empilhada 100% por ano (soja 1201 / minério 2601 / petróleo 2709 / resto) ou treemap de 2025.
- **Por que agora:** emenda com a #1 (China de novo, agora do lado da venda).

### Semana 3 · 18/12/2026 · #3 · "Quem toma o café do Brasil?"
- **Pergunta:** quais países compram o café brasileiro, e como esse ranking mudou desde 1997?
- **Fonte:** Comex Stat, exportação, SH4 0901, por país, kg líquido e US$ FOB, 1997 e 2025.
- **Filtros:** `noSh4pt = 0901`, detalhe `noPaispt`, um ano por vez ou a série 1997–2025 numa consulta.
- **Visual:** gráfico de inclinação (slope), top 10 de 1997 × top 10 de 2025, em participação no volume.
- **Por que agora:** fim de ano é época de presente e de café na mesa. Edição boa pra ficar pronta antes do lançamento.

### Semana 4 · 25/12/2026 · #4 · 🎄 "Quem come a carne brasileira?" (leve)
- **Pergunta:** pra onde vai a carne bovina que o Brasil exporta?
- **Fonte:** Comex Stat, exportação, SH4 0201 (fresca/refrigerada) + 0202 (congelada), por país, kg líquido, 2025.
- **Visual:** mapa coroplético (mesma receita do `graficos.py` da #1, trocando fluxo e SH4).
- **Por que agora:** semana de Natal, com uma consulta só e o código da #1 reaproveitado.

### Semana 5 · 01/01/2027 · #5 · ✈️ "Quanto o Brasil gasta viajando lá fora?" (leve)
- **Pergunta:** quanto os brasileiros gastam em viagens internacionais, e como isso se mexe com o dólar?
- **Fonte:** BCB, estatísticas do setor externo (conta de serviços › viagens: receitas e despesas), série mensal. Câmbio: SGS. [conferir os códigos das séries no SGS antes de puxar]
- **Visual:** linha mensal das despesas com viagens. Câmbio em gráfico separado ou em nota: **nunca dois eixos**.
- **Por que agora:** férias de janeiro.

### Semana 6 · 08/01/2027 · #6 · "O Brasil exporta petróleo e importa diesel?"
- **Pergunta:** pra onde vai o petróleo cru brasileiro, e de onde vêm os derivados que o país compra?
- **Fonte:** Comex Stat. Exportação SH4 2709 (óleo bruto) por país e importação SH4 2710 (derivados) por país, kg líquido e US$ FOB, 2026 fechado. Opcional: ANP (dados abertos de produção) pra contexto.
- **Visual:** barras divergentes por país (vende à direita, compra à esquerda).
- **Por que agora:** primeira edição com 2026 fechado.
- **Atenção:** 2710 mistura diesel, gasolina, querosene e lubrificantes. Pra falar de "diesel", filtre o NCM específico [conferir códigos de 8 dígitos do óleo diesel na tabela NCM].

### Semana 7 · 15/01/2027 · #7 · "O mundo briga por minerais críticos. Onde entra o Brasil?"
- **Pergunta:** o que o Brasil vende de nióbio, lítio e terras raras, pra quem, e onde ele fica no mapa mundial dessas reservas?
- **Fonte:** Comex Stat, exportação por país, NCM:
  - **72029300** ferro-nióbio · **2615** minérios de nióbio, tântalo, vanádio ou zircônio
  - **28252010** óxido de lítio · **28369100** carbonato de lítio · concentrado de espodumênio: **[conferir NCM]**, porque o 2530.90.90 teve valor quase nulo em 2025 e o produto deve estar em outro código
  - **2805** (inclui metais de terras raras) · **2846** compostos de terras raras
- **Contexto mundial:** USGS Mineral Commodity Summaries (governo dos EUA, domínio público) 🖐️. É fonte nova pra rotzOn: conferir licença e registrar.
- **Visual:** mapa dos compradores de ferro-nióbio (é o item com valor relevante).
- **Por que agora:** tema permanente da disputa EUA × China. Use notícia da semana, se houver, com link.

### Semana 8 · 22/01/2027 · #8 · "Brasil e Argentina: de parceiros a quê?"
- **Pergunta:** quanto a Argentina pesou no comércio brasileiro em cada década, e quando isso mudou?
- **Fonte:**
  - 1997–2026: Comex Stat, exportação e importação, país = Argentina, US$ FOB, mais o total do Brasil (pra calcular a participação, com denominador dito).
  - Antes de 1997: UN Comtrade [conferir o primeiro ano disponível pro Brasil] ou IBGE, *Estatísticas do Século XX* 🖐️. Conferir se as séries são comparáveis antes de emendar.
- **Visual:** linha longa da participação da Argentina no comércio total do Brasil. Marque o Tratado de Assunção (Mercosul, 1991) como anotação.
- **Por que agora:** pauta histórica, sem prazo. Aproveita o ano fechado.

### Semana 9 · 29/01/2027 · #9 · "De onde vêm os remédios do Brasil?"
- **Pergunta:** de que países o Brasil importa medicamentos prontos e matéria-prima de remédio?
- **Fonte:** Comex Stat, importação por país, US$ FOB, 2026:
  - **3004** medicamentos em doses · **2941** antibióticos · capítulo **29** (químicos orgânicos, onde caem muitos princípios ativos)
- **Visual:** mapa, ou barras por país, separando "remédio pronto" de "matéria-prima".
- **Por que agora:** mesma lógica da #1 (dependência), em outro setor.
- **Atenção:** o capítulo 29 tem muita coisa que não é remédio. Ou o texto diz isso, ou a pauta usa só 2941 e 3004.

### Semana 10 · 05/02/2027 · #10 · "China ou EUA: quem é o maior cliente do Brasil?"
- **Pergunta:** desde quando a China compra mais do Brasil que os EUA, e como a distância mudou?
- **Fonte:** Comex Stat, exportação, por país, US$ FOB, 1997–2026, numa consulta (série por país).
- **Visual:** linha China × EUA (participação no total exportado), com o ano da virada anotado (sai do dado).
- **Por que agora:** série completa até 2026 fechado. Fecha um arco com a #2.

### Semana 11 · 12/02/2027 · #11 · "Quem investe no Brasil?"
- **Pergunta:** de que países vem o investimento estrangeiro direto no Brasil?
- **Fonte:** BCB, estatísticas do setor externo, investimento direto no país (IDP) por país [conferir se a quebra é por país imediato ou por controlador final e dizer isso no texto, porque o critério muda o ranking].
- **Visual:** barras horizontais, top 10.
- **Por que agora:** semana de Carnaval (09/02). A pauta é de uma fonte só, com tabela pronta.

### Semana 12 · 19/02/2027 · #12 · "De onde vêm os chips e celulares do Brasil?"
- **Pergunta:** de quais países chegam os celulares e os chips que o Brasil importa?
- **Fonte:** Comex Stat, importação por país, US$ FOB, 2026: **8517** (aparelhos de telefonia, inclui celulares) · **8542** (circuitos integrados).
- **Visual:** mapa (ou duas barras lado a lado: 8517 × 8542).
- **Por que agora:** fecha o trimestre no tema da disputa tecnológica, conectando com a #7.
- **Atenção:** país de origem no Comex é onde o produto foi fabricado, não a sede da marca. O texto tem que dizer isso.

---

## ⚡ Pautas de emergência (até ~1h30 cada)

### E1 · "A virada China × Rússia continua?"
- Rodar de novo os três scripts da #1 (`baixar.py`, `calcular.py`, `graficos.py`). Eles pegam sozinhos o último mês disponível.
- Texto curto: o que mudou desde a #1 (acumulado no ano e 12 meses), e o mesmo gráfico atualizado.

### E2 · "Pra quantos países o Brasil vende?"
- Comex Stat, exportação por país, US$ FOB, último ano fechado: uma consulta.
- Contar os países com registro e mostrar quantos compram mais de US$ 1 bi. O mapa sai do `graficos.py` da #1, trocando o fluxo.
- Lembrar: país sem venda é "sem registro", não zero.
