"""Caminhos do projeto. Tudo relativo à raiz do repositório."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"                 # arquivos brutos das fontes e caches de coleta (fora do git)
PUBLIC_SITE_DIR = ROOT / "site"          # saída do build público (rotzx publicar), fora do git
USER_AGENT = "rotzx/0.1 (pesquisa pessoal)"     # o mesmo de sempre: as fontes já conhecem este cliente
