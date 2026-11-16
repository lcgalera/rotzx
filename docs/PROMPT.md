# Prompt para continuar o rotzx com um assistente de IA

Copie o bloco abaixo como primeira mensagem de uma conversa nova (Claude Code ou outro assistente com acesso ao repositório).
Ele resume o projeto, as regras e o estado em 16/11/2026; a documentação completa está em [`PROJETO.md`](PROJETO.md).

---

```text
Você vai trabalhar no rotzx (repositório lcgalera/rotzx, site https://lcgalera.github.io/rotzx/).
Escreva e responda em português do Brasil. O nome do produto é "rotzx", sempre em minúsculas.

## O que é
Atlas do comércio exterior brasileiro: com quem o Brasil compra e vende, o quê, e como isso mudou desde 1997.
Todos os países e territórios, produtos (SH4), concentração e comparação, com o contexto de cada relação (votos na ONU,
disputas na OMC, conflitos armados, ficha econômica do Banco Mundial). Só dados abertos.

## Leia antes de mudar qualquer coisa
- docs/PROJETO.md (visão geral, fontes, arquitetura, dados, comandos, publicação, limitações)
- docs/DECISOES.md (D1–D75: cada escolha e o motivo; registre uma decisão nova para cada mudança relevante)
- docs/SCHEMA.md (formato do detalhamento) e README.md

## Regras que não podem ser quebradas
1. Só dado real, com fonte e data. Nunca invente número, nem em exemplo de interface. Fixture de teste usa o formato
   real da fonte com valores marcados como inventados.
2. Interpretação nunca passa por fato. Nada de nota "boa/ruim" ou de risco entre países; só medidas, cada uma com a fonte.
3. Participação sempre com o denominador dito; dado ausente é "sem registro", nunca zero; mudança de participação em p.p.
4. Créditos e licenças das fontes sempre visíveis na página.
5. Comunicação sem exagero: frases de comparação dizem a direção; associação não é causalidade.

## Como trabalhar
- Python 3.9, dependências fixas em requirements.txt (pytest, pycountry, Pillow); .venv/bin/python -m rotzx <comando>;
  testes: .venv/bin/python -m pytest -q antes de cada commit.
- A página é prototipos/globo/index.html, sem build: bibliotecas por CDN com versão exata e SRI (globe.gl 2.46.2,
  topojson-client 3.1.0, ECharts 5.5.0, world-atlas 2.0.2, flag-icons 7.5.0), política de conteúdo (CSP), tema claro e escuro por tokens.
- Teste a interface no Chromium sem tela (Playwright) em 1440×900 e 390×844: sem erros de página, sem violação de CSP,
  sem rolagem horizontal, com e sem WebGL.
- Dados: rotzx mundo-atualizar (retrato), rotzx detalhe-gerar (detalhamento ano a ano), rotzx mundo-codigos (tabela de países).
  Cada fonte que falha vai para "falhas" e não apaga dados bons.
- Publicação: workflow "Publicar" (publicar.yml, à mão) gera o site e envia ao GitHub Pages; "Dados" (dados.yml, à mão)
  atualiza os dados e faz commit.
- Git: trabalhe numa branch, commits em português (o quê e por quê). PR, merge e publicação só quando o dono pedir.
- Fonte nova: confira licença, termos e se o ambiente alcança o domínio; documente na tabela de fontes e numa decisão nova.
- Escreva para pessoas comuns: frases curtas, sem jargão; números no formato brasileiro (US$ 1,2 bi; 28,7%).

Comece lendo os arquivos indicados, confirme em poucas linhas o que entendeu e proponha o próximo passo antes de codar.
```

---

## Como usar

- **Continuar o projeto:** cole o bloco como está e, logo depois, diga o que quer.
- **Tarefa pontual:** cole o bloco e troque o último parágrafo pelo pedido.
- **Atualize este arquivo** quando o estado mudar, junto com `PROJETO.md` e `DECISOES.md`.
