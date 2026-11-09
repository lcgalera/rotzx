# Rotina e metas da rotzOn

## A meta dos 3 primeiros meses
**12 edições, 12 sextas, sem falhar.** O que conta é a consistência, não o número de assinantes.

- Edição curta e no dia vale mais que edição perfeita atrasada. Se a semana apertar, use uma pauta de emergência (E1 ou E2 do calendário).
- **Sempre 1 edição de folga:** as #1 a #3 ficam prontas antes do lançamento. Depois disso, a regra é ter sempre a edição da semana seguinte com os dados já puxados.
- Uma edição só conta como feita se cumprir o molde e o checklist: todo número com fonte, nada de [VERIFICAR] sobrando no texto publicado.

## Antes do lançamento (de 09/11 a 04/12/2026)

| Semana | O que fazer |
|---|---|
| 09–13/11 | ✅ Edição #1 pronta (dados, gráficos, texto, posts). Escolher a plataforma (Substack ou Beehiiv) e criar a conta, o nome, a descrição e a página "sobre". |
| 16–20/11 | Edição #2 (China além da soja): dados + visual + texto. Montar o gráfico da #1 no Datawrapper. |
| 23–27/11 | Edição #3 (café): dados + visual + texto. Revisar #1–#3 em voz alta. Agendar a #1. |
| 30/11–04/12 | Divulgar que vai lançar (LinkedIn e X), puxar os dados da #4. **Sexta 04/12: publica a #1.** |

## A rotina semanal (~4h)

| Dia | Tempo | O que fazer | Pronto quando… |
|---|---|---|---|
| **Segunda** | 30 min | Escolher a pauta do calendário. Ler as notícias da semana pra ver se tem gancho (guardar o link). Escrever a pergunta central numa frase. | A pergunta cabe numa linha e dá pra responder com uma consulta. |
| **Terça** | 60 min | Puxar os dados (copiar o `baixar.py` da edição anterior e trocar fluxo, filtro e período). Rodar o cálculo. Anotar os 5–8 números que importam. | Tabelas em `tabelas/` e os números conferidos com o site da fonte. |
| **Quarta** | 45 min | Fazer o visual: CSV pro Datawrapper + prévia em PNG. Escrever o título-conclusão do gráfico. | O gráfico se explica sozinho, com título, linha fina e fonte. |
| **Quinta** | 60 min | Escrever no molde: título, visual, contexto, "pro Brasil", "dado pra guardar", fontes. Escrever os posts de LinkedIn e X. | Texto dentro de 3–5 min e posts dentro do limite de caracteres. |
| **Sexta** | 45 min | Preencher o `checklist.md` (cada número → fonte). Ler em voz alta. Publicar de manhã. Postar no LinkedIn e no X com o gráfico. Responder comentários. Anotar as métricas da semana anterior. | Publicado, divulgado e `registro-edicoes.csv` atualizado. |

**Total: ~4h.** Se a terça estourar (fonte fora do ar, por exemplo), corte na quarta: troque o gráfico por uma tabela simples, mas não pule a sexta.

### Pra economizar tempo toda semana
- **Reaproveite o código.** Cada edição nova começa copiando a pasta da anterior. A maioria das pautas do calendário usa o Comex Stat, então muda só o filtro.
- **Uma pasta por edição**, sempre igual: `dados_brutos/`, `tabelas/`, `visuais/`, `newsletter.md`, `post_linkedin.md`, `post_x.md`, `checklist.md`.
- **O checklist é o filtro final.** Se um número não tem linha no checklist, ele sai do texto.

## O que medir

### Toda semana (5 min, na sexta)
Anote no `registro-edicoes.csv`, sempre **7 dias depois** de publicar, pra comparar edições no mesmo prazo:

| Métrica | Por quê |
|---|---|
| Taxa de cliques (cliques únicos ÷ e-mails entregues) | Mais confiável que a abertura, porque alguns programas de e-mail marcam a mensagem como aberta sozinhos, por privacidade. |
| Taxa de abertura | Serve pra ver tendência, não pra comparar com outras newsletters. |
| Assinantes novos na semana e cancelamentos na semana | Mostra se a pauta atrai ou afasta gente. |
| Respostas e comentários | Sinal forte de interesse. Anote também *do que* falaram. |
| LinkedIn: impressões, reações, comentários, compartilhamentos | O alcance de cada tema fora da lista. |
| X: impressões, reposts, respostas | Idem. |
| Cliques no link de assinatura vindos de cada post | Mostra qual rede traz assinante, não só curtida. |
| Horas gastas na edição | Pra saber quais pautas cabem nas 4h. |

E marque em cada edição: **frente** (economia / geopolítica / história), **tipo de visual** (mapa / linha / barra…), **fonte** e se teve gancho de notícia (sim/não).

### Depois de 3 meses: como decidir o que aprofundar
Com 12 edições, a amostra é pequena. Leia os números como pistas, não como prova.

1. **Ordene as 12 edições pela taxa de cliques** e veja as 3 do topo e as 3 do fim.
2. **Agrupe por frente e por tipo de visual** e compare a mediana (não a média, que um viral sozinho distorce). Exemplo: "as de geopolítica tiveram mediana de cliques X; as de história, Y".
3. **Cruze com os assinantes novos e os cancelamentos.** Um tema que dá muito clique mas faz gente cancelar não é um bom tema.
4. **Leia as respostas.** Pergunta repetida de leitor é pauta pronta.
5. **Olhe as horas gastas.** Tema que funciona e cabe em 4h vira série. Tema que funciona mas estoura o tempo vira especial mensal.

**Decisão:** escolha 2 ou 3 temas pra virar série (por exemplo, "dependências do Brasil": fertilizantes → remédios → chips) e 1 tema pra tirar do calendário. Registre a decisão e o motivo, igual se faz no `docs/DECISOES.md` do rotzx.

### Perguntas que vale fazer aos leitores (1 pergunta só, na edição #12)
- "Qual edição você mais gostou e por quê?"
- "Que país ou produto você quer ver aqui?"
