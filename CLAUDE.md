# CLAUDE.md — rotzx

Responda em português do Brasil. O nome do produto é "rotzx", sempre em minúsculas.

## Modelo e esforço
- Tarefas simples (ler/explorar código, buscar arquivo, renomear, formatar):
  delegar pro subagente `explorador`.
- Mudança de tamanho médio: seguir no modelo da sessão.
- Arquitetura, debug difícil ou refatoração grande: entrar em plan mode
  e mostrar o plano antes de editar qualquer coisa.
- Se o pedido estiver vago, perguntar antes de gastar esforço.

## O projeto
Atlas do comércio exterior brasileiro (https://lcgalera.github.io/rotzx/): com quem o Brasil compra e vende, o quê, e como isso
mudou desde 1997, com o contexto de cada relação (ONU, OMC, conflitos, Banco Mundial).
- Página: `prototipos/globo/index.html`, o site inteiro, sem build.
- Dados: `prototipos/globo/dados/`.
- Código Python: `rotzx/mundo/` (coleta, retrato, detalhamento, páginas estáticas, cartões) e `rotzx/public_build.py`.
- Tabela de países: `catalog/paises_mundo.csv`.

Antes de mudar algo relevante, leia `docs/PROJETO.md` (visão completa) e `docs/DECISOES.md` (D1–D81).
Toda mudança relevante ganha uma decisão nova em `docs/DECISOES.md`.

## Regras que não podem ser quebradas
- Só dado real, com fonte e data. Nunca inventar número, nem em exemplo de interface.
- Interpretação nunca passa por fato; nada de nota "boa/ruim" ou de risco entre países, só medidas com fonte.
- Participação sempre com o denominador dito; dado ausente é "sem registro", nunca zero; mudança de participação em p.p.
- Créditos e licenças das fontes sempre visíveis.
- Nada de uso pessoal no repositório (`privado/`, `data/` e `site/` ficam fora do git).

## Como trabalhar
- Python 3.9: `.venv/bin/python -m rotzx <comando>`; testes: `.venv/bin/python -m pytest -q` antes de cada commit.
- Interface sem build, bibliotecas por CDN com versão exata e SRI; política de conteúdo (CSP) na página. Teste em Chromium sem tela,
  em 1440×900 e 390×844, sem erros e sem violação de CSP.
- Dados: `rotzx mundo-atualizar` (retrato), `rotzx detalhe-gerar` (detalhamento ano a ano), `rotzx mundo-codigos` (tabela de países);
  fonte que falha vai para `falhas`.
- Publicação: workflow `publicar.yml` (à mão); dados: `dados.yml` (à mão).
- Git: trabalhar numa branch, commits em português; PR, merge e publicação só quando o dono pedir.
- Fonte nova: conferir licença, termos e se o ambiente alcança o domínio; documentar em `docs/PROJETO.md`.
