"""Linha de comando do rotzx: `python -m rotzx <comando>`."""
import argparse
from pathlib import Path

from . import config


def main(argv=None):
    ap = argparse.ArgumentParser(prog="rotzx", description="rotzx: atlas do comércio exterior brasileiro (dados abertos)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    mu = sub.add_parser("mundo-atualizar", help="coleta o retrato do atlas (Comex Stat, ONU, OMC, UCDP, Banco Mundial) e grava historia/produtos")
    mu.add_argument("--ano", default=None, help="último ano do comércio (padrão: o último ano completo)")
    mc = sub.add_parser("mundo-codigos", help="gera catalog/paises_mundo.csv (ISO 3166, Comex Stat, ONU, UCDP e mapa)")
    mc.add_argument("--atlas", default=None, help="cópia local do countries-110m.json (world-atlas), se o CDN não estiver ao alcance")
    dg = sub.add_parser("detalhe-gerar", help="gera o detalhamento ano a ano (parceiros de cada produto, produtos de cada país) do Comex Stat")
    dg.add_argument("--de", type=int, default=None, help="primeiro ano (padrão: 1997)")
    dg.add_argument("--ate", type=int, default=None, help="último ano (padrão: o último ano do retrato)")
    dv = sub.add_parser("detalhe-validar", help="confere os arquivos de detalhamento (docs/SCHEMA.md) antes de publicar")
    dv.add_argument("pasta", nargs="?", default=None, help="padrão: prototipos/globo/dados/detalhe")
    pb = sub.add_parser("publicar", help="gera o site público em site/ (atlas, páginas por país e produto, cartões)")
    pb.add_argument("--sem-cartoes", action="store_true", help="não desenha os cartões de compartilhamento (build mais rápido)")
    args = ap.parse_args(argv)

    if args.cmd == "mundo-atualizar":
        from .mundo import historia
        h = historia.montar(historia.SAIDA, historia.BRUTOS, args.ano)
        print(f"retrato: {len(h['paises'])} países e territórios; falhas: {h['falhas'] or 'nenhuma'}")
    elif args.cmd == "mundo-codigos":
        from .mundo import codigos, historia
        codigos.montar(historia.BRUTOS / "onu", historia.BRUTOS / "ucdp", Path(args.atlas) if args.atlas else None)
    elif args.cmd == "detalhe-gerar":
        from .mundo import detalhe, detalhe_coleta, historia
        detalhe_coleta.gerar(ano_ini=args.de or historia.ANO_COMEX, ano_fim=args.ate)
        _relatar(detalhe.validar_pasta(), 50)
    elif args.cmd == "detalhe-validar":
        from .mundo import detalhe
        _relatar(detalhe.validar_pasta(Path(args.pasta) if args.pasta else detalhe.PASTA), 200)
    elif args.cmd == "publicar":
        from . import public_build
        meta = public_build.build(cartoes=not args.sem_cartoes)
        print(f"site público em {config.PUBLIC_SITE_DIR.relative_to(config.ROOT)}/: {meta['paginas']['paises']} países, {meta['paginas']['produtos']} produtos")


def _relatar(probs, limite):
    for x in probs[:limite]:
        print("✗", x)
    print(f"{len(probs)} problema(s)" if probs else "detalhamento ok: índice e arquivos no formato rotzx.detalhe.v1")
    if probs:
        raise SystemExit(1)
