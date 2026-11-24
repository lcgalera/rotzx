# rotzx

**Atlas do comércio exterior brasileiro:** com quem o Brasil compra e vende, o quê, e como isso mudou desde 1997.

https://lcgalera.github.io/rotzx/

- Todos os países e territórios com comércio registrado com o Brasil, de 1997 a 2025, num globo e em rankings.
- Produtos (SH4): para onde vai e de onde vem cada um, ano a ano.
- Comparação de dois parceiros, com o contexto de cada relação: votos na ONU, disputas na OMC, conflitos armados e ficha econômica.
- Cada número traz a fonte e o ano. Dado ausente aparece como "sem registro", nunca como zero.
- PNG de cada gráfico, CSV dos dados, link direto para qualquer tela e código para incorporar em outro site.

Só dados abertos: Comex Stat (MDIC), Harvard Dataverse (votos na ONU), OMC, UCDP/PRIO e Banco Mundial. Licenças e método em
"Fontes e método", na própria página.

## Como rodar

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements.txt
```

```bash
.venv/bin/python -m pytest -q
```

Para ver a página, sirva a pasta do atlas e abra http://localhost:8000:

```bash
cd prototipos/globo && python3 -m http.server 8000
```

Comandos (`.venv/bin/python -m rotzx <comando>`):

| Comando | O que faz |
|---|---|
| `mundo-atualizar` | refaz os dados do atlas a partir das fontes |
| `detalhe-gerar` | refaz o detalhamento ano a ano (Comex Stat) |
| `detalhe-validar` | confere o detalhamento antes de publicar |
| `mundo-codigos` | regera a tabela de países |
| `pro-amostra` | refaz o estudo-amostra do rotzx Pro (PDF) |
| `publicar` | gera o site em `site/` |

A publicação é feita pelo workflow **Publicar**, na aba Actions do GitHub.

## Documentação

- [`docs/PROJETO.md`](docs/PROJETO.md): visão completa (fontes, arquitetura, dados, publicação, limitações)
- [`docs/DECISOES.md`](docs/DECISOES.md): cada decisão e o motivo
- [`docs/SCHEMA.md`](docs/SCHEMA.md): formato dos arquivos de detalhamento
- [`docs/PROMPT.md`](docs/PROMPT.md): para continuar o projeto com um assistente de IA

Autor: [LinkedIn](https://www.linkedin.com/in/lucasfgalera) · [GitHub](https://github.com/lcgalera)
