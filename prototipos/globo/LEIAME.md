# Atlas rotzx (prototipos/globo)

Esta pasta é o site público inteiro, publicado na raiz de https://lcgalera.github.io/rotzx/ pelo workflow **Publicar**
(`/globo/` redireciona para a raiz). O build copia tudo, menos este arquivo, e acrescenta as páginas por país e por produto.

- `index.html`: a página inteira (HTML, CSS e JS, sem build; bibliotecas por CDN com versão exata e SRI).
- `dados/historia.js|json`, `dados/produtos.js|json`: o retrato (`rotzx mundo-atualizar`).
- `dados/detalhe/`: o detalhamento ano a ano, buscado sob demanda (`rotzx detalhe-gerar`; formato em `docs/SCHEMA.md`).
- `medicao.js`: medição de acessos sem cookies (GoatCounter).
- `og.png`, `icone.svg`, `icone-180.png`: cartão de compartilhamento e ícones.

Para ver localmente: `python3 -m http.server 8000` nesta pasta. Precisa de internet para as bibliotecas e de WebGL para o globo
(sem WebGL, a lista assume).

A descrição completa está em `docs/PROJETO.md`, e o histórico das versões em `docs/DECISOES.md`.
