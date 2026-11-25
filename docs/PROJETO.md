# rotzx — visão do projeto

Estado em 16/11/2026 (v1.0.0; decisões até D82). Este documento descreve o projeto inteiro: o que ele faz, de onde vêm os dados, como o
código está organizado, como publicar e o que ainda não faz. O histórico de cada escolha está em [`DECISOES.md`](DECISOES.md) (D1–D82).
Para continuar o projeto com um assistente de IA, use [`PROMPT.md`](PROMPT.md).

## 1. O que é

**rotzx** é um atlas do comércio exterior brasileiro, publicado em https://lcgalera.github.io/rotzx/.

Pergunta-guia: **com quem o Brasil compra e vende, o quê, e como isso mudou desde 1997?**

O atlas cobre todos os países e territórios com comércio registrado com o Brasil, de 1997 a 2025, e acrescenta o contexto de cada relação:
votos na ONU, disputas na OMC, conflitos armados e uma ficha econômica.

Até a v0.13 o repositório tinha outras frentes: radar econômico e previsões do IPCA, radar de transmissão de energia, newsletter rotzOn
e o nome antigo econatlas. Elas foram removidas na D74 e estão no histórico do git (último commit com elas: `081a87c`).

## 2. Princípios

- **Só dado real**, com fonte e data. Nunca inventar número, nem em exemplo de interface. Fixtures de teste são marcadas como inventadas.
- **Interpretação não passa por fato.** Nada de nota "boa/ruim" ou de risco entre países, só medidas com fonte.
- **Participação sempre com o denominador dito.** Mudança de participação em p.p.
- **Dado ausente é "sem registro", nunca zero.**
- **Créditos e licenças das fontes sempre visíveis** na página "Fontes e método".
- **A página não tem build:** um HTML com bibliotecas por CDN em versão exata e com integridade (SRI).

## 3. Arquitetura

```
prototipos/globo/          o site: index.html (a página inteira), medicao.js, og.png, ícones e dados/
  dados/historia.js|json   retrato por país (comércio, ONU, conflitos, OMC, economia)
  dados/produtos.js|json   explorador por produto (séries e maiores parceiros)
  dados/detalhe/           detalhamento ano a ano, buscado sob demanda (formato em docs/SCHEMA.md)
  pro/                     estudo-amostra do rotzx Pro em PDF e miniaturas (a página /pro/ e o logo.svg são gerados no build)
rotzx/                     código Python: coleta, retrato, detalhamento, páginas estáticas e build
  mundo/                   fontes (comex, onu, omc, conflitos, bancomundial), tabela de países, retrato,
                           detalhamento, páginas estáticas e cartões (com as fontes tipográficas em mundo/fontes/)
  pro/                     rotzx Pro: coleta mensal e cruzada (cache em data/fontes/pro/), indicadores (volume × preço × mix, HHI),
                           Pink Sheet (referencia.py), nomes legíveis (nomes.py), planilha (planilha.py), relatório em PDF,
                           motor dos estudos (estudo.py) e um recorte por estudo em amostras/ (fertilizantes, café),
                           estudo-amostra e página /pro/ (plano em docs/PRO.md)
  public_build.py          gera site/ para o GitHub Pages
  cli.py                   python -m rotzx <comando>
catalog/paises_mundo.csv   tabela de países e territórios (ISO 3166 × Comex Stat × ONU × UCDP)
tests/                     pytest
docs/                      PROJETO, DECISOES, SCHEMA, PROMPT, PRO
.github/workflows/         publicar.yml (site) e dados.yml (atualização dos dados)
```

O build copia `prototipos/globo/` para a raiz do site, menos o `LEIAME.md`. `/globo/` redireciona para a raiz levando o que vem depois do
`#`, então links antigos continuam valendo. O build também gera uma página por país e por produto, com o cartão de compartilhamento de cada
uma.

## 4. Fontes de dados

| Fonte | Usada em | Licença / termos | Observações |
|---|---|---|---|
| [Comex Stat (MDIC)](https://comexstat.mdic.gov.br) | comércio por país e produto (SH4), 1997–2025; no rotzx Pro, mês, NCM, UF, porto, via, frete, seguro e CIF | dados abertos | só o formato `GET /general?filter=` funciona; ~12 s entre consultas; frete, seguro e CIF só na importação |
| [Votos na Assembleia Geral da ONU](https://doi.org/10.7910/DVN/LEJUQZ) (Voeten, Strezhnev e Bailey, Harvard Dataverse) | concordância com o Brasil, 1946– | CC0 | índice de Lijphart; muda com a pauta do ano |
| [Disputas na OMC](https://www.wto.org/english/tratop_e/dispu_e/dispu_by_country_e.htm) | disputas com o Brasil desde 1995 | site oficial | países da UE aparecem pela UE |
| [UCDP/PRIO Armed Conflict Dataset](https://ucdp.uu.se/downloads/) | conflitos armados, 1946– | CC BY 4.0 | 25+ mortes em combate no ano; conta tropas de missões multinacionais |
| [Banco Mundial (WDI)](https://data.worldbank.org) | PIB, crescimento, inflação, população | CC BY 4.0 | valor mais recente de cada indicador |
| [Banco Mundial, Pink Sheet](https://www.worldbank.org/en/research/commodity-markets) (CMO-Historical-Data-Monthly.xlsx) | cotações mensais de ureia, DAP, TSP e cloreto de potássio (estudo-amostra do rotzx Pro) | CC BY 4.0 | arquivo em thedocs.worldbank.org (domínio liberado na rede do ambiente em 24/11/2026); fica em `data/fontes/bancomundial/`, fora do git; o link muda a cada ano |
| [Banco Central do Brasil, PTAX](https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/aplicacao) | câmbio do dólar (venda), média mensal, para R$/saca no estudo do café do rotzx Pro | dados abertos do BCB | API OData em olinda.bcb.gov.br (já na rede do ambiente); cache em `data/fontes/bcb/` |
| [Conab, safra de café](https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cafe) | produção por estado e espécie (arábica/conilon), estudo do café do rotzx Pro | dados públicos do governo federal | 3º levantamento de 2026 (setembro), números lidos do boletim e citados com a data |
| ISO 3166 (pycountry / iso-codes) | tabela de países | LGPL (dados ISO) | só para gerar `catalog/paises_mundo.csv` |
| Natural Earth 1:110m (via `world-atlas@2.0.2`) | contornos | domínio público (pacote ISC) | ids = ISO 3166 numérico |
| globe.gl 2.46.2, topojson-client 3.1.0, ECharts 5.5.0 | globo e gráficos | MIT, ISC, Apache-2.0 | jsDelivr, com SRI |
| flag-icons 7.5.0 | bandeiras | MIT | bandeira atual, não a do ano |
| Newsreader e IBM Plex Sans | tipografia (página e cartões) | SIL Open Font License | cópia em `rotzx/mundo/fontes/`, com as licenças |
| GoatCounter | medição de acessos | serviço externo | sem cookies; respeita "não rastrear" |

Ficaram de fora, com motivo registrado: FMI (barra acesso automatizado, D39); blocos e alianças pelo Wikidata (erros encontrados, D42);
API da UCDP (pede chave; o download não pede, D43).

## 5. O que a pessoa vê

Cabeçalho: logo, navegação (Início · Parceiros · Produtos · Comparar), busca de país, Fontes e método, guia (?) e tema claro/escuro.

- **Início:** uma manchete com o dado do último ano e uma história em passos (China desde 2000, China × EUA, soja, fertilizantes).
  - Cada passo pinta o globo.
  - Um guia passo a passo abre na primeira visita (D72).
- **Globo e controles:**
  - métricas: exportações, importações, corrente, participação e mudança em p.p.; em "Contexto", votos na ONU e conflitos;
  - linha do tempo com ▶;
  - "Lista" como alternativa sem 3D, que assume sozinha sem WebGL.
- **Parceiros:** ranking da métrica no ano.
- **Painel do país:**
  - **Abertura:** valores, partes com o denominador e posição.
  - **Relação comercial:** séries de 1997 a 2025.
  - **Produtos e concentração:** maiores produtos de cada lado, ano a ano, e por onde passam.
  - **Contexto diplomático:** ONU, OMC, conflitos e ficha econômica.
- **Explorar por produto:** maiores destinos ou origens ano a ano, série do Brasil e itens NCM quando houver. Um país aberto a partir de um
  produto mostra o total do produto, a fatia do país e o peso do produto no comércio com ele (D64).
- **Comparar dois parceiros:** comércio, produtos e participação lado a lado, mais diplomacia, conflitos e economia (D71).
- **Fontes e método:** fontes com links, cobertura, definições, licenças e a nota sobre a medição.
- **Exportar e compartilhar:**
  - PNG de cada gráfico e CSV dos números brutos;
  - "Copiar link" com o estado completo;
  - "Incorporar" (`<iframe>` com `embed=1`);
  - cartão de link por página (D62, D63, D70).
- **Páginas estáticas:** uma por país e por produto, com tabelas e link para o atlas no estado certo (D66).
- **URL:** `#pais=CHN`, `#ver=ranking&m=mud&base=2000`, `#ver=produto&prod=1201&fluxo=e`, `#ver=comparar&a=CHN&b=USA`, `&ano=`, `&aba=`,
  `&amplo=1`, `&embed=1`. Voltar, avançar e recarregar mantêm o estado.

### Definições (o denominador muda; a tela sempre diz qual)

| Medida | Cálculo |
|---|---|
| Concentração de destinos | exportações para o país ÷ exportações totais do Brasil |
| Concentração de origens | importações do país ÷ importações totais do Brasil |
| Participação (mapa) | corrente com o país ÷ corrente total do Brasil |
| Mudança | participação no ano − participação no ano-base, em p.p. (só com comércio registrado nos dois anos) |
| Composição bilateral | produto ÷ total trocado com o país |
| Parte no produto | valor com o país ÷ total do Brasil naquele produto (operações com país identificado) |

Participação alta indica concentração, não vulnerabilidade. Os totais do Brasil incluem operações sem país definido.

## 6. Dados

- **`catalog/paises_mundo.csv`:** `iso_num`, `iso3`, `iso2`, `nome`, `tipo` (país ou território), `comex`, `cow`, `gw`, `no_mapa`.
- **`dados/historia.json|js`** (`window.HISTORIA`):
  - `comercio`: séries por país de 1997 a 2025 (`e`, `i`) e totais do Brasil;
  - `p[ano][e|i] = {t, n, top}` em 2000, 2010 e 2025;
  - nomes de produtos;
  - `onu`, `conflitos`, `omc` e `economia`.
- **`dados/produtos.json|js`** (`window.PRODUTOS`): por produto (SH4 ou grupo), séries de 1997 a 2025 e os 12 maiores parceiros em 2000,
  2010 e 2025.
- **`dados/detalhe/`:**
  - parceiros de cada produto e produtos de cada país em todos os anos;
  - formato `rotzx.detalhe.v1` em [`SCHEMA.md`](SCHEMA.md).
- Ano sem registro = `null`. Valores em US$ FOB correntes.

## 7. Comandos

`.venv/bin/python -m rotzx <comando>`:

| Comando | O que faz |
|---|---|
| `mundo-atualizar [--ano A]` | baixa a versão mais recente da ONU e da UCDP e refaz `historia` e `produtos` (Comex Stat, OMC, Banco Mundial); fonte que falha vai para `falhas` |
| `detalhe-gerar [--de A] [--ate A]` | refaz `dados/detalhe/` (58 consultas ao Comex Stat, com cache em `data/fontes/mundo/detalhe/`) |
| `detalhe-validar [pasta]` | confere o detalhamento contra o formato (sai com erro se houver problema) |
| `mundo-codigos` | regera `catalog/paises_mundo.csv` |
| `pro-amostra [--estudo fertilizantes\|cafe\|todos]` | refaz os estudos-amostra do rotzx Pro (`prototipos/globo/pro/estudo-<slug>.pdf`, a planilha `.xlsx` e as miniaturas `estudo-<slug>-p1/p3.webp`); consultas cruzadas ao Comex Stat com cache em `data/fontes/pro/`; precisa do Chromium e do `pdftoppm`; baixa o Pink Sheet se faltar |
| `publicar [--sem-cartoes]` | gera `site/` (atlas, páginas estáticas, cartões, sitemap) |

Para ver a página localmente: `cd prototipos/globo && python3 -m http.server 8000` e abrir http://localhost:8000.

## 8. Publicação e automação (GitHub Actions)

- **Publicar** (`publicar.yml`, à mão): testes, `detalhe-validar` e `rotzx publicar`; depois envia `site/` ao GitHub Pages.
- **Dados** (`dados.yml`, à mão): testes, `mundo-atualizar` e, se marcado, `detalhe-gerar`; faz commit dos dados novos. Depois é preciso
  rodar "Publicar".
- Os dois rodam em `ubuntu-24.04`, fixo porque o 26.04 não tem Python 3.9 (D58).
- O cache do GitHub Pages leva cerca de 10 minutos; para conferir, use uma aba anônima.
- **Falhas conhecidas do Pages:**
  - "try again later" no deploy: rodar de novo só o job `site`;
  - deploy travado em "updating_pages": um commit novo destrava.

## 9. Testes e guardas

- `.venv/bin/python -m pytest -q`: fontes e retrato com fixtures marcadas, detalhamento, páginas estáticas, cartões, build e repositório.
  - O teste do repositório confere que `privado/`, `data/` e `site/` nunca são versionados.
- **Interface:** testar no Chromium sem tela em 1440×900 e 390×844, nos temas claro e escuro, com e sem WebGL, sem erros de console e sem
  violações da política de conteúdo (CSP). Hoje os scripts de Playwright ficam fora da suíte.
- **Segurança (D73):**
  - SRI nos scripts de fora e no contorno dos países;
  - CSP no atlas e nas páginas estáticas;
  - texto vindo da URL sempre escapado e `#prod=` só com códigos da base;
  - CSV sem injeção de fórmula.

## 10. Limitações conhecidas

- **Retrato fechado:** sem atualização automática. A data aparece na página.
- **Mapa e bandeiras:** fronteiras atuais para países que não existem mais; bandeira atual, não a do ano.
- **Detalhes por produto:**
  - o explorador detalha os 12 maiores parceiros de cada produto e o país, os 10 maiores produtos;
  - o resto fica em "Outros", sem valor individual;
  - UF, via, porto e NCM ainda não estão no detalhamento.
- **Valores em dólares correntes:** alta em valor não prova alta em volume. Os códigos SH4 mudaram nas revisões do Sistema Harmonizado.
- **ONU:** o índice muda com a pauta do ano, e concordância não equivale a aliança.
- **UCDP:** conta tropas de missões de paz como apoio.
- **OMC:** não dá encerramento formal a muitos casos antigos.
- **Compartilhamento:** as redes não leem o `#`. O cartão próprio aparece só ao compartilhar a página estática do país ou do produto.

## 11. Próximos passos sugeridos

- Atualização mensal com "o que mudou este mês" (o Comex Stat sai todo mês).
- Volume (kg) além de valor, para separar preço de quantidade.
- Visão por estado (UF) no detalhamento.
- Domínio próprio e cadastro no Google Search Console (o `sitemap.xml` já existe).
- Carregar `produtos.js` só quando a história chegar à soja (alivia a primeira carga no celular).
