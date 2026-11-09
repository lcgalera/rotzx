# rotzx — documentação do projeto

Estado em 09/11/2026 (v0.13; decisões até D56). Este documento descreve o projeto inteiro: o que ele faz,
de onde vem cada dado, como as peças se encaixam e como operar. O porquê de cada escolha está em [`DECISOES.md`](DECISOES.md)
(D1–D56). Para continuar o projeto com um assistente de IA, use [`PROMPT.md`](PROMPT.md).

- Repositório: https://github.com/lcgalera/rotzx
- Site público: https://lcgalera.github.io/rotzx/ (só o atlas "Como o Brasil se conecta ao mundo", D53; `/globo/` redireciona para a raiz)

---

## 1. O que é

rotzx é um projeto pessoal de **inteligência econômica com dados abertos e rastreáveis**. Tem três frentes, construídas
nesta ordem. A frente em foco é o atlas, que é também o único conteúdo do site público (D53); as outras duas continuam no repositório
e rodam localmente.

| Frente | Para quem | O que entrega | Onde |
|---|---|---|---|
| **Radar econômico e setorial** | quem acompanha economia e a indústria de materiais elétricos | séries oficiais (BCB, IBGE, Focus), previsões registradas antes dos dados saírem, placar de acertos e erros | `rotzx/forecast`, `rotzx/analysis`, `registro/` (público no git), interface local (`rotzx servir`) |
| **Radar de oportunidades (transmissão de energia)** | fornecedores do setor elétrico (B2B) | projetos do SIGET/ANEEL com evidência por regra, score explicado, histórico de mudanças, leilões e contexto econômico | `rotzx/intelligence`, `historico/`, `docs/03`–`08` |
| **Atlas "Como o Brasil se conecta ao mundo"** | pessoas comuns que querem entender o comércio do Brasil | globo interativo: parceiros, produtos, concentração e comparação desde 1997, com contexto diplomático; notícias pausadas | `rotzx/mundo`, `prototipos/globo/`, site público (raiz) |

O nome é **rotzx**, sempre em minúsculas (D25, D35). O nome antigo, EconAtlas, ainda funciona por compatibilidade
(`python -m econatlas` redireciona; o banco `data/econatlas.sqlite` é renomeado no primeiro uso).

## 2. Princípios (valem para tudo)

1. **Só dado real, com fonte.** Cada número mostra de onde veio e de quando é. Nada de valor inventado, nem em exemplo de interface.
2. **Interpretação nunca passa por fato.** Frases geradas a partir de números só descrevem; o que for interpretação aparece marcado.
   Na relação entre países não existe nota de "boa" ou "ruim": aparecem sinais medidos (D42).
3. **Proveniência.** Cada coleta guarda o arquivo bruto com SHA-256; cada versão dos dados é uma *vintage* (D2, D3).
4. **Previsão registrada antes e imutável.** Especificação fixa antes do backtest (D9); registro só recebe acréscimos e é verificado contra o git (D10, D23).
5. **Dado privado nunca vai para o público.** Séries da Macrodados são de uso pessoal (termos proíbem redistribuição): ficam fora do git,
   e duas guardas impedem vazamento — a varredura do build e os testes do repositório (D4, D13, D20).
6. **Notícias: só título, veículo, data e link.** O texto fica no site do veículo (D38, D40).
7. **Automático pode errar, e a página avisa.** Categorias, assuntos e países citados são marcados por palavras do título.
8. **Comunicação sem exagero** (D26, D27): frases de comparação sempre dizem a direção; nada de "comprovado" quando é associação.

## 3. Arquitetura

```
Fontes oficiais ──► providers/ e mundo/ (coleta, com novas tentativas e limite de ritmo)
                     │
                     ├─► storage.py  SQLite + arquivos brutos com SHA-256 (vintages)          ─┐
                     ├─► historico/*.csv  SIGET e leilões (só acréscimos, no git)              │
                     └─► prototipos/globo/dados/*.json|js  globo (comércio, relações, manchetes)│
                                                                                                ▼
prototipos/globo/ ──────────────────────────────────────────────► public_build.py ──► site/ (GitHub Pages: só o atlas, D53)
forecast/, analysis/, intelligence/ ──► registro/*.csv (previsões)  ──► api.py + web/ (uso local, FastAPI; site antigo com --completo)
```

- **Python 3.9**, monolítico (D1): FastAPI para uso local, HTML/JS sem build (ECharts e globe.gl por CDN com versão fixa).
- **SQLite** com gatilhos que impedem alterar previsões registradas (D10).
- **Dependências fixas** em `requirements.txt` (o Actions calcula com as mesmas bibliotecas do Mac).
- **Site público estático**: `rotzx publicar` gera `site/` com o atlas na raiz e um redirecionamento em `/globo/` (D53); `--completo` gera o
  site antigo com os radares. Os dois modos terminam com a varredura anti-vazamento (que lê também `.js`, D41).

### Pastas

| Pasta / arquivo | Conteúdo |
|---|---|
| `catalog/` | `series.json` (metadados conferidos nas fontes oficiais, D19), categorias de produto, perfil de demonstração, contexto do radar, contratos de leilões |
| `rotzx/providers/` | BCB/SGS, BCB/Expectativas (Focus), IBGE/SIDRA, arquivos, Macrodados (uso pessoal), CKAN/ANEEL, SIGET, leilões |
| `rotzx/forecast/` | modelos do IPCA (ingênuo, sazonal, SARIMA, Focus), backtest, faixa empírica, registro, previsão setorial |
| `rotzx/analysis/leading.py` | indicadores antecedentes fora da amostra (Clark-West + Holm, D14–D17) |
| `rotzx/intelligence/` | radar de oportunidades: evidências R1–R5, score, histórico do SIGET, leilões, contexto econômico, relatório |
| `rotzx/mundo/` | globo: Comex Stat, Banco Mundial, RSS, GDELT, ONU, OMC, UCDP, países e montagem dos dados |
| `rotzx/storage.py`, `transforms.py`, `payloads.py`, `quality.py`, `registro.py`, `public_build.py`, `api.py`, `cli.py` | núcleo |
| `web/` | interface dos radares (local; publicada só com `publicar --completo`) |
| `prototipos/globo/` | o atlas: `index.html` (página única), ícones (`icone.svg`, `icone-180.png`, D52) e `dados/` (gerados) |
| `registro/` | previsões públicas e coletas (CSV, só acréscimos) |
| `historico/` | SIGET (coletas, eventos, estado) e leilões de transmissão (CSV, só acréscimos; ODbL) |
| `avaliacoes/` | avaliação humana de relevância do SIGET (conjunto de teste das regras) |
| `tests/` | pytest: 148 testes + 1 pulado em 09/11/2026 (inclui as guardas do repositório público) |
| `docs/` | avaliações, diagnósticos, fontes, mercado, validação, motor, contexto, leilões, decisões, este documento e o prompt |
| `privado/`, `data/`, `site/`, `docs/DIARIO.md` | só locais, fora do git |

## 4. Fontes de dados

| Fonte | Usada em | Licença / termos | Observações |
|---|---|---|---|
| BCB/SGS e BCB/Expectativas (Focus) | radar econômico | dados abertos | câmbio e Selic mensal desde jul/1994 (D7) |
| IBGE/SIDRA | radar; PIM-PF seção 3.27 no setorial | dados abertos | 3.27 não mede investimento em transmissão |
| Macrodados | só uso pessoal, no Mac | proíbe redistribuição | importação manual, nunca automatizada (D13) |
| ANEEL SIGET (CKAN) | radar de oportunidades | ODbL | validado (D30), coleta semanal (D33) |
| ANEEL resultados de leilões | leilões de transmissão | dados abertos | planilha baixada à mão (o site tem desafio Cloudflare) (D37) |
| Comex Stat (MDIC) | globo: comércio | dados abertos | só o formato antigo `GET /general?filter=` funciona; ~12 s entre consultas |
| Banco Mundial (WDI) | globo: economia | CC BY 4.0 | PIB, crescimento, inflação, população |
| Feeds RSS (g1, Folha, BBC News Brasil, DW, Agência Brasil, RFI) | globo: manchetes | só título, veículo, data, link | fonte principal das manchetes (D40) |
| GDELT DOC 2.0 | globo: manchetes | aberto | complemento; limita IPs compartilhados |
| Votos na Assembleia Geral da ONU (Voeten, Strezhnev e Bailey, Harvard Dataverse) | globo: sinais da relação | CC0 | índice de Lijphart; sensível à pauta do ano (D42) |
| Disputas na OMC (site da OMC) | globo: sinais e visão externa | site oficial | lido como texto; países da UE aparecem pela UE (D42) |
| UCDP/PRIO Armed Conflict Dataset (Uppsala) | globo: conflitos armados | CC BY 4.0 | 25+ mortes em combate/ano; conta tropas de missões multinacionais como apoio (D43) |
| Newsreader e IBM Plex Sans (Google Fonts) | tipografia do atlas | SIL Open Font License | serifa nos títulos, sans no texto (D49) |
| ISO 3166 (pycountry / iso-codes do Debian) | tabela de países | LGPL (dados ISO) | só para gerar `catalog/paises_mundo.csv` (D46) |
| flag-icons 7.5.0 | bandeiras | MIT | bandeira atual, não a do ano (D47) |
| Itamaraty — relações bilaterais | link no painel | site oficial | desafio anti-robô: só o índice, sem conferir página por país (D46) |
| Natural Earth 1:110m (via `world-atlas@2.0.2`) | contornos dos países | domínio público (pacote ISC) | ids = ISO 3166 numérico |

Ficaram de fora, com motivo registrado: FMI (barra acesso automatizado, D39); blocos e alianças pelo Wikidata (erros
encontrados, D42); API da UCDP (pede chave; o download não pede, D43).

## 5. Frente 1 — radar econômico e setorial

- **Radar Brasil:** 18 séries públicas (inflação, juros, câmbio, atividade, renda, crédito).
- **MacroForecast (IPCA):** ingênuo, sazonal ingênuo, SARIMA e Focus; backtest desde 2016; faixa de 80% empírica (erros dos últimos 60 meses, por horizonte, D21).
- **Setorial:** indústria de máquinas e materiais elétricos (IBGE 3.27) a 3 e 6 meses, especificação `setorial_v1` com hash (D18, D22).
  As faixas cobriram 61–69% no backtest para meta de 80%: o próximo passo é uma `setorial_v2`, sem mexer na v1.
- **Indicadores antecedentes:** avaliados fora da amostra, em tempo pseudo-real, com Clark-West e correção de Holm; achado só vale se replicar (D14–D17).
- **Página "Indústria de materiais elétricos: o que os juros indicam"** em linguagem simples, com todo número calculado dos dados (D24).

## 6. Frente 2 — radar de oportunidades (transmissão)

Fases (detalhes em `docs/02`, `03`, `06`, `07`, `08`):
1. **Fonte:** exploração do portal da ANEEL e validação do SIGET (D28, D30).
2. **Histórico:** coletas que só baixam o que mudou, eventos de mudança e estado em `historico/` (D33), toda segunda-feira (`radar-siget.yml`).
3. **Motor:** regras determinísticas R1–R5 com evidência por regra e score separado da evidência (D32); precisão de 80% (IC 58–92%) numa amostra aleatória avaliada à mão (D31).
4. **Leilões:** resultado dos leilões de transmissão como sinal antecipado, com ligação lote → contrato (D37).
5. **Contexto econômico** no relatório, fora do score (D34).

Pendente: conversas com compradores antes de construir interface (D29), nova amostra fora da amostra, janela por categoria.

## 7. Frente 3 — Atlas "Como o Brasil se conecta ao mundo" (globo)

Pergunta-guia: **de quem o Brasil depende para vender e para comprar — e como isso mudou ao longo do tempo?** (D47).
A página é `prototipos/globo/index.html`, publicada **na raiz do site** pelo build, que copia a pasta inteira, exceto o `LEIAME.md`
(D53; `/globo/` redireciona para a raiz levando o que vem depois do `#`). É uma página única, sem build: globe.gl 2.46.2, ECharts 5.5.0,
bandeiras flag-icons 7.5.0 e dados em `dados/*.js`. É um retrato fechado, coletado à mão e sem atualização automática (D45); a página
diz a data do retrato. As notícias estão pausadas (seção 7.5).

### 7.1 O que a pessoa vê

Cabeçalho: logo rotzx (D52), "Como o Brasil se conecta ao mundo", navegação (Início · Parceiros · Produtos · Comparar), busca de país ou
território, Fontes e método e o botão de tema (claro, escuro ou do sistema, D49).

- **Início, em forma de história (D54):** seis passos — o Brasil no ano, a China desde 2000, China × EUA, a soja em 2000 e agora, os
  fertilizantes e "Escolha seu caminho" (busca e quatro portas: Maiores parceiros, Quem ganhou espaço, Produtos, Comparar). Cada passo,
  ao chegar ao meio da leitura, pinta o globo (métrica, ano, produto) e o leva ao país em foco, sem mudar a URL. Todos os números dos textos
  são calculados dos dados; o "maior parceiro" de cada passo também. A entrada termina com a assinatura "Pátria amada, Brasil." e a data do
  retrato (D51).
- **Mapa e controle único (D54):**
  - métricas: exportações, importações, corrente, participação, mudança em p.p. e, em segundo plano, contexto (votos na ONU, conflitos);
  - um controle só de métrica e ano, a linha do tempo com ▶: fica no painel do mapa ou, com o mapa recolhido (sempre no celular), na barra
    da análise; em produto, encaixa nos anos do recorte (2000, 2010, 2025) como "Ano do recorte";
  - legenda com o significado das cores e da escala, fixa para todos os anos (exceto a de mudança, ajustada ao par de anos e dita);
  - o globo destaca o país escolhido, o cartão mostra a variação sobre o ano anterior quando os dois anos têm dado, e globo e listas
    realçam o mesmo país. A **Lista** é a alternativa sem 3D e assume sozinha sem WebGL.
- **Parceiros:** ranking da métrica no ano, com barra na linha e escala explicada, e o grupo recolhido dos países sem registro no ano.
- **Painel do país (248 países e territórios):**
  - abertura com bandeira, nome (com marca de território), ano e os números do topo: valor, parte (com o denominador) e posição, uma vez só;
  - frase de abertura por regras fixas, só com o que os números não dizem (produtos, mudança desde o ano-base);
  - **Relação comercial:** tabela ano-base × ano (em p.p.) e valores e participações de 1997 a 2025, com tabela alternativa aos gráficos;
  - **Produtos e concentração:** 10 maiores de cada lado em 2000, 2010 e 2025, a soma dos 5 maiores e a parte do país no total do produto;
  - **Contexto diplomático:** ONU, OMC, conflitos (cada um com tabela), link do Itamaraty e ficha econômica recolhível.
- **Explorar por produto:** busca e atalhos com rótulos curtos (D50), exportações ou importações, maiores destinos ou origens com
  participação, o texto do recorte ("12 maiores detalhados; a fonte registra N; os demais estão em Outros", D51) e a série anual do Brasil,
  identificada como "Total do Brasil — todos os parceiros".
- **País visto por um produto (D48, D50):** um fornecedor ou destino aberto pelo explorador mostra o país naquele produto, fluxo e ano
  (posição e parte no total brasileiro do produto; "fora do recorte detalhado" quando não está entre os 12 maiores), com volta à exploração
  e acesso a todo o comércio com o parceiro. A busca do topo abre sempre o painel geral.
- **Comparar dois parceiros:** duas colunas com cores de série fixas (A verde, B ocre), tabela no ano, exportações e participação no mesmo
  eixo e 5 maiores produtos lado a lado; no celular, cada valor fica junto do nome do país. Um país não pode ser comparado com ele mesmo.
- **Fontes e método:** fonte, cobertura, unidade, definições, critérios, limitações e licenças.
- **Leitura e estados:**
  - "Ampliar análise" recolhe o mapa e "Mostrar mapa" o devolve (D48); a trilha (Início › …) e o ✕ são os caminhos de volta (D54);
  - dois níveis de informação: valor, participação, ano e fonte visíveis; código SH4, descrição oficial, fórmula e limitações em
    "Detalhes" e "Sobre este dado" (D48);
  - avisos curtos para ano fora da cobertura, ano sem recorte e parâmetro inválido na URL; falha de carga com "Tentar de novo";
    carregamento com a silhueta do Brasil (D51);
  - movimento: números que contam até o novo valor, gráficos atualizados sem ser recriados, troca de tela curta; tudo some com
    "reduzir movimento" (D54).
- **URL:** `#pais=RUS&prod=g-fertilizantes&fluxo=i&ano=2025` (país visto por um produto), `#ver=comparar&a=CHN&b=USA`, `&amplo=1`,
  `&aba=produtos`, `#ver=ranking&m=mud&base=2000`. Voltar, avançar e recarregar mantêm o estado; `#China`, `vs=` e os links antigos
  em `/globo/#…` continuam funcionando.

### 7.2 Definições (o denominador muda; a tela sempre diz qual)

| Medida | Cálculo |
|---|---|
| Concentração de destinos | exportações para o país ÷ exportações totais do Brasil |
| Concentração de origens | importações do país ÷ importações totais do Brasil |
| Participação (mapa) | corrente com o país ÷ corrente total do Brasil |
| Mudança | participação no ano − participação no ano-base, em p.p. (só com comércio registrado nos dois anos) |
| Composição bilateral | produto ÷ total trocado com o país (total exato: vem da distribuição completa) |
| Fornecedores de um produto | importações do produto vindas do país ÷ importações totais do produto |

Não há nota de risco nem de dependência: participação alta indica concentração, não vulnerabilidade. Os totais do Brasil incluem operações sem
país definido.

### 7.3 Dados

- `catalog/paises_mundo.csv`: `iso_num`, `iso3`, `iso2`, `nome`, `tipo` (país ou território), `comex`, `cow`, `gw`, `no_mapa`.
  Gerado por `rotzx mundo-codigos`.
- `dados/historia.json|js` (`window.HISTORIA`), gerado por `rotzx mundo-atualizar --historico`:
  - `comercio`: séries por país de 1997 a 2025 (`e`, `i`), totais do Brasil, `anos_produtos` ([2000, 2010, 2025]);
  - por país e ano, `p[ano][e|i] = {t, n, top: [[sh4, valor] ×10]}`;
  - `sh4` (nomes oficiais) e `curtos` (nomes revisados);
  - `onu`, `conflitos`, `omc`, `economia` (D46).
- `dados/produtos.json|js` (`window.PRODUTOS`, carregado sob demanda): em `itens[código]`,
  - `nome`, `oficial` e, nos grupos, `grupo`;
  - séries `e` e `i` de 1997 a 2025;
  - `p[ano][e|i] = {t, n, top: [[iso_num, valor] ×12]}`.
- Ano sem registro = `null`.

### 7.4 Coleta

Tudo de uma vez, à mão (`workflow_dispatch` do workflow Globo, ou localmente), com cerca de 10 consultas ao Comex Stat:
- séries por país;
- séries por produto;
- pares país × produto em 2000, 2010 e 2025.
Os arquivos brutos da ONU e da UCDP ficam em `data/fontes/mundo/`, fora do git.

### 7.5 Notícias (pausadas)

Coletores e testes em `rotzx/mundo/` (`rss.py`, `gdelt.py`, `paises.py`: `MENCOES` e `citados`). A interface antiga das manchetes (assuntos,
linha do tempo, mapa de calor) está no histórico do git: `prototipos/globo/index.html` no commit `d193691`. Regras que continuam valendo: só
título, veículo, data e link; país citado com acento e palavra inteira.

## 8. Automação (GitHub Actions)

| Workflow | Quando | O que faz |
|---|---|---|
| `rotina-mensal.yml` | dias 12 e 20, ou à mão | testes, registro, dados abertos, previsões, backtest, calibração, verificação do registro, build do site, commit e deploy no Pages |
| `radar-siget.yml` | toda segunda, ou à mão | histórico do SIGET, eventos, contexto, relatório (artefato 90 dias), commit de `historico/` |
| `globo.yml` | só à mão (agendamentos pausados, D45) | testes; retrato histórico (`--historico`) e commit dos dados |

Actions em Node 24 (D36). Python 3.9 no Actions e no Mac; não atualizar `setup-python` para v7 sem migrar o Python.
O site só muda quando a rotina mensal roda: ela publica o que estiver na `main` (inclusive os dados do atlas em `prototipos/globo/dados/`).
Para publicar uma mudança antes do dia 12, rode a rotina à mão (*Actions › Rotina mensal › Run workflow*).

Se o deploy no Pages falhar:
- **"Deployment failed, try again later"** (o pedido fica em `deployment_queued` e é recusado): repetir só o job `site` resolveu (06/11/2026).
- **Travado em "updating_pages" até o tempo limite** (três vezes em 06/11/2026, com o site e o pacote corretos): repetir o job não resolve,
  porque o Pages identifica a publicação pelo commit, e a do commit cancelado não volta. Publique a partir de um commit novo na `main`.
- Depois de publicar, confira a página ao vivo numa aba anônima: o Pages e o navegador guardam a versão anterior por até cerca de 10 minutos.

## 9. Linha de comando

`.venv/bin/python -m rotzx <comando>`:

| Comando | O que faz |
|---|---|
| `atualizar [séries]` | baixa as séries do catálogo (vintages com SHA-256) |
| `prever` / `prever-setor [--pessoal]` | registra as previsões do IPCA / setoriais |
| `backtest`, `calibrar-setorial`, `analisar-setor` | backtest do IPCA, cobertura das faixas setoriais, indicadores antecedentes |
| `publicar [--saida pasta] [--completo]` | gera o site público (só o atlas na raiz; `--completo` = site antigo com os radares) com a varredura anti-vazamento |
| `registro-exportar` / `registro-importar` / `registro-verificar [--contra REF]` | registro público em CSV |
| `importar-macrodados arquivo.csv` | só no Mac, uso pessoal |
| `qualidade` | verificações de consistência |
| `fonte-explorar`, `siget-atualizar`, `siget-amostra`, `siget-historico-exportar/importar` | radar de oportunidades |
| `leiloes-importar arquivo.xlsx`, `contexto-atualizar`, `oportunidades [--perfil] [--top]` | leilões, contexto, relatório |
| `mundo-atualizar [--ano A] [--historico] [--sem-noticias] [--so-noticias] [--so-relacoes]` | dados do globo (`--historico`: retrato de todos os países) |
| `mundo-codigos [--atlas arquivo]` | gera `catalog/paises_mundo.csv` |
| `servir` | interface local dos radares em http://127.0.0.1:8000 (o atlas fica em `/globo`) |

## 10. Como rodar

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m rotzx atualizar
.venv/bin/python -m rotzx servir                 # http://127.0.0.1:8000
.venv/bin/python -m pytest -q                    # 148 passam, 1 pulado (09/11/2026)
```

Só o globo: `python3 -m http.server 8000 --directory prototipos/globo` e abrir http://localhost:8000 (precisa de internet para as bibliotecas e de WebGL;
sem WebGL, a lista de países assume).

## 11. Testes e guardas

- 148 testes (`tests/`), com fixtures sintéticas **no formato real** das fontes e valores inventados, marcados como tal.
- Guardas do repositório público: falham se um arquivo versionado estiver em pastas privadas ou citar um código do catálogo da Macrodados.
- Varredura do build: falha se o site tiver id, código, nome ou sequência de valores (inclusive derivados) de série pessoal.
- Build público: um teste confere que o site é só o atlas na raiz, com os scripts e dados que a página carrega, e que `/globo/` redireciona (D53).
- Globo: testes de marcação de países (inclusive falsos positivos), categorias, hora de Brasília, ONU, OMC, UCDP, isolamento de falhas entre fontes.
- A interface do globo foi verificada em Chromium sem tela (WebGL por software), em 1440×900 e 390×844.

## 12. Limitações conhecidas

- Atlas: retrato fechado (sem atualização automática); fronteiras atuais para países que não existem mais; bandeira atual, não a do ano.
- Composição por produto só em 2000, 2010 e 2025, e o explorador detalha só os 12 maiores parceiros de cada produto (os demais ficam em
  "Outros", sem valor individual, D51). Ano sem recorte cai no recorte anterior, com aviso.
- Valores em dólares correntes: alta em valor não prova alta em volume. Códigos SH4 mudaram nas revisões do Sistema Harmonizado.
- O índice de votos na ONU muda com a pauta do ano; a página mostra a série com a mediana dos países, e concordância não equivale a aliança.
- A OMC não dá encerramento formal a muitos casos antigos; a página lista as disputas com o Brasil desde 1995, com a situação informada pela OMC.
- Notícias (pausadas): agrupamento de assuntos, categorias e países citados são automáticos e podem errar; a página avisa quando voltarem.
- A UCDP conta tropas de missões de paz como apoio: o Brasil aparece na República Centro-Africana ao lado de 38 países.
- Nomes de lados em conflitos e títulos de disputas na OMC ficam em inglês, como nas fontes.
- Faixas setoriais estreitas (61–69% de cobertura para meta de 80%).
- O registro é auditável, não impossível de reescrever: quem controla o repositório poderia reescrever o histórico do git (D27).

## 13. Próximos passos sugeridos

**Atlas**
- Mais anos de composição por produto (a consulta do Comex é uma por ano e fluxo).
- Séries em valores reais ou em volume (kg), para separar preço de quantidade.
- "Por que importa para o Brasil": texto curto por país, com a fonte de cada número e a interpretação marcada.
- Blocos e alianças de fonte oficial (os sites de cada bloco), em vez do Wikidata.
- Testes de interface (hoje feitos com Playwright fora do pytest) dentro da suíte.

**Radar**
- `setorial_v2` com janela recente de erros; primeiras avaliações do IPCA (nov/2026) e da indústria (dez/2026).
- Validação com compradores (5 conversas) antes da interface do radar de oportunidades.

## 14. Índice das decisões

| Faixa | Assunto |
|---|---|
| D1–D13 | arquitetura, dados, previsões, identidade visual, Macrodados |
| D14–D24 | indicadores antecedentes, previsão setorial, metadados, site público, rotina mensal, página do setor |
| D25–D27, D35 | nome rotzx e comunicação sem exagero |
| D28–D34, D37 | radar de oportunidades (SIGET, avaliação, motor, histórico, contexto, leilões) |
| D36 | Actions em Node 24 |
| D38–D55 | o globo: fontes, publicação, relações, conflitos, manchetes (pausadas), retrato histórico, atlas comercial, refinamento da leitura, identidade editorial, acabamento, versão estável, logo, atlas como site público e fluxo enxuto e dinâmico |
