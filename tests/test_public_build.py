"""Build do site público (`rotzx publicar`): o atlas na raiz, páginas estáticas e nada além disso."""
import re

import pytest

from rotzx import public_build


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    out = tmp_path_factory.mktemp("pub") / "site"
    meta = public_build.build(out, cartoes=False)            # os cartões têm teste próprio (test_paginas)
    return out, meta


def test_atlas_na_raiz_com_tudo_o_que_a_pagina_carrega(site):
    out, meta = site
    html = (out / "index.html").read_text(encoding="utf-8")
    assert "Como o Brasil se conecta ao mundo" in html                # nome do atlas no cartão de compartilhamento
    for local in re.findall(r'<script src="([^"]+)"', html):
        if not local.startswith("http"):
            assert (out / local.split("?")[0]).exists(), local
    for arq in ("dados/historia.js", "dados/produtos.js", "dados/detalhe/indice.json", "icone.svg", "icone-180.png", "og.png", "medicao.js",
                "sitemap.xml", "robots.txt", ".nojekyll", "pais/china/index.html", "produto/1201/index.html"):
        assert (out / arq).exists(), arq
    assert meta["paginas"]["paises"] > 200 and meta["paginas"]["produtos"] > 600


def test_nada_de_trabalho_nem_de_versoes_antigas(site):
    out, _ = site
    assert not (out / "LEIAME.md").exists()
    for velho in ("dados/mundo.js", "dados/noticias.js", "app.js", "data"):
        assert not (out / velho).exists(), velho


def test_globo_antigo_redireciona_levando_o_hash(site):
    out, _ = site
    redir = (out / "globo" / "index.html").read_text(encoding="utf-8")
    assert 'location.replace("../" + location.hash)' in redir and 'href="../"' in redir


def test_scripts_de_fora_com_integridade(site):
    out, _ = site
    html = (out / "index.html").read_text(encoding="utf-8")
    externos = re.findall(r'<script src="(https://[^"]+)"([^>]*)>', html)
    assert externos and all('integrity="sha384-' in attrs and 'crossorigin="anonymous"' in attrs for _, attrs in externos)
    assert 'http-equiv="Content-Security-Policy"' in html


def test_build_nao_apaga_pasta_alheia(tmp_path):
    alheia = tmp_path / "meus-arquivos"
    alheia.mkdir()
    (alheia / "importante.txt").write_text("não apague")
    with pytest.raises(RuntimeError):
        public_build.build(alheia, cartoes=False)
    assert (alheia / "importante.txt").exists()
