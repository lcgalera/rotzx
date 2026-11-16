"""Site público do rotzx (`python -m rotzx publicar`): o atlas na raiz, páginas estáticas e cartões.

Saída em site/ (fora do git), enviada ao GitHub Pages pelo workflow `publicar.yml`:
- o atlas (prototipos/globo) na raiz, sem os arquivos de trabalho;
- /globo/ redireciona para a raiz levando o que vem depois do # (links antigos continuam valendo, D53);
- uma página por país e por produto, sitemap.xml e robots.txt (D66) e o cartão de cada uma (D70).
"""
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from . import __version__, config

MARCA = ".rotzx-publico"  # arquivo que identifica uma pasta gerada por este build (só ela pode ser apagada)
GLOBO = config.ROOT / "prototipos" / "globo"
FORA = ("LEIAME.md", "__pycache__")                                  # arquivos de trabalho que não vão para o site
REDIRECIONA_GLOBO = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>rotzx</title>
<meta name="viewport" content="width=device-width, initial-scale=1"><link rel="canonical" href="../">
<script>location.replace("../" + location.hash);</script>
<meta http-equiv="refresh" content="0; url=../"></head>
<body style="font-family:system-ui,sans-serif;background:#F3F0E8;color:#222721;padding:24px">
<p>O atlas agora fica em <a href="../">lcgalera.github.io/rotzx/</a>.</p></body></html>
"""


def _prepare_dir(out: Path) -> None:
    if out.exists():
        if not (out / MARCA).exists() and any(out.iterdir()):
            raise RuntimeError(f"{out} existe e não foi gerada por este build; escolha outra pasta")
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / MARCA).write_text("pasta gerada por rotzx publicar; pode ser apagada e refeita\n")


def _so_atlas(out: Path, cartoes: bool = True) -> Dict:
    """Atlas na raiz; /globo/ redireciona; páginas estáticas e cartões."""
    for p in GLOBO.iterdir():
        if p.name in FORA:
            continue
        (shutil.copytree if p.is_dir() else shutil.copy2)(p, out / p.name)
    (out / "globo").mkdir()
    (out / "globo" / "index.html").write_text(REDIRECIONA_GLOBO, encoding="utf-8")
    from .mundo import paginas                     # D66: uma página estática por país e por produto (buscadores não leem o #)
    r = paginas.gerar(out, out / "dados", cartoes=cartoes)
    (out / ".nojekyll").write_text("")  # GitHub Pages: servir arquivos como estão
    return r


def build(out: Optional[Path] = None, cartoes: bool = True) -> Dict:
    out = Path(out or config.PUBLIC_SITE_DIR)
    _prepare_dir(out)
    paginas = _so_atlas(out, cartoes)
    return {"gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"), "versao_codigo": __version__, "paginas": paginas}
