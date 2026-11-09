"""rotzOn — gera, para cada edição, uma página HTML pronta para copiar e colar no editor do Substack.

    .venv/bin/python rotzon/substack.py            # todas as edições
    .venv/bin/python rotzon/substack.py 2          # só a edição #2

Lê rotzon/edicao-NN/newsletter.md e grava rotzon/edicao-NN/substack.html.
Abra o HTML no navegador e use os botões "Copiar": cada um copia um campo (título, subtítulo, legenda,
texto alternativo, corpo) já formatado, pronto para colar no campo correspondente do Substack.
Precisa de: pip install markdown
"""
import html
import re
import sys
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parent

# Texto alternativo da imagem (para quem usa leitor de tela). Só números já conferidos no checklist de cada edição.
ALT = {
    1: ("Gráfico de linhas com as importações brasileiras de adubos da China e da Rússia, em milhões de toneladas, de 2015 a 2025. "
        "A Rússia fica acima da China em todos os anos até 2024. Em 2025 as linhas se cruzam: China com 12,0 milhões de toneladas "
        "e Rússia com 11,1 milhões."),
    2: ("Gráfico de barras empilhadas, de 1997 a 2025, com a participação de soja, minério de ferro, petróleo bruto e outros produtos "
        "no total exportado pelo Brasil para a China. Os três produtos somavam 24,7% em 1997 e 74,2% em 2025: soja 34,5%, "
        "petróleo bruto 20,1% e minério de ferro 19,6%. Outros produtos ficaram com 25,8%."),
    3: ("Gráfico de inclinação com a posição dos maiores compradores do café brasileiro em 1997 e em 2025. Alemanha, EUA, Itália, "
        "Japão e Bélgica ocupam do 1º ao 5º lugar nos dois anos. Argentina, Suécia, França e Grécia saem do top 10; Turquia, "
        "Holanda, Rússia e China entram, a China saindo do 55º para o 10º lugar."),
}

PAGINA = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>rotzOn #{n} · Substack</title>
<style>
  :root {{ --bg:#f6f5f2; --card:#ffffff; --ink:#1b1b1a; --ink2:#5b5a56; --line:#e2e0da; --accent:#2a78d6; --ok:#1a7f4e; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.55 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
  main {{ max-width:760px; margin:0 auto; padding:24px 16px 64px; }}
  h1.pg {{ font-size:22px; margin:0 0 4px; }}
  p.pg {{ color:var(--ink2); margin:0 0 20px; font-size:14px; }}
  ol.passos {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px 18px 14px 36px; font-size:14px; color:var(--ink2); }}
  ol.passos li {{ margin:4px 0; }}
  .campo {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px 16px; margin:14px 0; }}
  .rot {{ display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:8px; }}
  .rot span {{ font-size:12px; font-weight:600; letter-spacing:.04em; text-transform:uppercase; color:var(--ink2); }}
  button {{ font:600 13px/1 inherit; border:1px solid var(--accent); color:var(--accent); background:#fff; border-radius:8px;
           padding:8px 12px; cursor:pointer; min-height:36px; }}
  button.ok {{ border-color:var(--ok); color:var(--ok); }}
  .txt {{ font-size:15px; }}
  .img {{ border:2px dashed var(--line); border-radius:10px; padding:12px; text-align:center; color:var(--ink2); font-size:14px; }}
  .img img {{ max-width:100%; height:auto; display:block; margin:8px auto 0; border-radius:6px; }}
  #corpo {{ font-family: Georgia, "Times New Roman", serif; font-size:17px; }}
  #corpo h2 {{ font-family:inherit; font-size:22px; margin:1.4em 0 .4em; }}
  #corpo blockquote {{ border-left:3px solid var(--ink); margin:1em 0; padding:.2em 1em; }}
  #corpo a {{ color:var(--accent); }}
  #corpo hr {{ border:0; border-top:1px solid var(--line); margin:1.6em 0; }}
  footer {{ color:var(--ink2); font-size:12px; margin-top:24px; }}
</style>
</head>
<body>
<main>
  <h1 class="pg">rotzOn #{n}: versão para o Substack</h1>
  <p class="pg">Gerado a partir de <code>edicao-{nn}/newsletter.md</code>. Se mudar o texto, rode de novo <code>rotzon/substack.py</code>.</p>

  <ol class="passos">
    <li>No Substack: <b>New post</b>. Cole o <b>título</b> e o <b>subtítulo</b> nos campos próprios.</li>
    <li>No início do corpo, insira a imagem (botão de imagem → suba <code>{png}</code>). Cole a <b>legenda</b> no campo de legenda e o <b>texto alternativo</b> em "Alt text".</li>
    <li>Logo abaixo da imagem, cole o <b>corpo</b>. Intertítulos, negritos, citação e links vêm junto.</li>
    <li>Mande um e-mail de teste para você (<b>Send test email</b>) e confira no celular antes de agendar.</li>
  </ol>

  <div class="campo"><div class="rot"><span>Título</span><button data-alvo="titulo">Copiar</button></div>
    <div class="txt" id="titulo">{titulo}</div></div>

  <div class="campo"><div class="rot"><span>Subtítulo</span><button data-alvo="subtitulo">Copiar</button></div>
    <div class="txt" id="subtitulo">{subtitulo}</div></div>

  <div class="campo"><div class="rot"><span>Imagem (inserir no Substack)</span></div>
    <div class="img">Arquivo: <code>{png}</code><img src="{png}" alt=""></div></div>

  <div class="campo"><div class="rot"><span>Legenda da imagem</span><button data-alvo="legenda">Copiar</button></div>
    <div class="txt" id="legenda">{legenda}</div></div>

  <div class="campo"><div class="rot"><span>Texto alternativo (alt text)</span><button data-alvo="alt">Copiar</button></div>
    <div class="txt" id="alt">{alt}</div></div>

  <div class="campo"><div class="rot"><span>Corpo do post</span><button data-alvo="corpo" data-rico="1">Copiar com formatação</button></div>
    <div id="corpo">{corpo}</div></div>

  <footer>Dados: Comex Stat/MDIC. Conferência dos números: <code>edicao-{nn}/checklist.md</code>.</footer>
</main>
<script>
  document.querySelectorAll("button[data-alvo]").forEach(function (b) {{
    b.addEventListener("click", function () {{
      var el = document.getElementById(b.dataset.alvo), ok = false;
      try {{
        var r = document.createRange(); r.selectNodeContents(el);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        ok = document.execCommand("copy"); s.removeAllRanges();
      }} catch (e) {{ ok = false; }}
      if (!ok && navigator.clipboard) {{ navigator.clipboard.writeText(el.innerText); ok = true; }}
      var t = b.textContent; b.textContent = ok ? "Copiado ✓" : "Selecione e copie à mão"; b.classList.toggle("ok", ok);
      setTimeout(function () {{ b.textContent = t; b.classList.remove("ok"); }}, 1800);
    }});
  }});
</script>
</body>
</html>
"""


def inline(texto: str) -> str:
    """Markdown de uma linha (negrito, itálico, links) → HTML, sem o <p> em volta."""
    return re.sub(r"^<p>|</p>$", "", markdown.markdown(texto).strip())


def gerar(n: int) -> Path:
    pasta = RAIZ / f"edicao-{n:02d}"
    linhas = (pasta / "newsletter.md").read_text(encoding="utf-8").splitlines()
    titulo = subtitulo = png = legenda = None
    i = 0
    while i < len(linhas):  # cabeçalho: # título, **subtítulo**, ![imagem](arquivo), *legenda*, ---
        l = linhas[i].strip()
        if l.startswith("# ") and titulo is None:
            titulo = l[2:].strip()
        elif l.startswith("**") and subtitulo is None:
            subtitulo = l.strip("*").strip()
        elif l.startswith("!["):
            png = re.search(r"\((.+?)\)", l).group(1)
        elif l.startswith("*") and not l.startswith("**") and legenda is None:
            legenda = l.strip("*").strip()
        elif l == "---":
            i += 1
            break
        i += 1
    assert all([titulo, subtitulo, png, legenda]), f"cabeçalho incompleto em {pasta}/newsletter.md"
    corpo_md = "\n".join(linhas[i:]).strip()
    corpo = markdown.markdown(corpo_md)
    saida = pasta / "substack.html"
    saida.write_text(PAGINA.format(
        n=n, nn=f"{n:02d}", titulo=html.escape(titulo), subtitulo=inline(subtitulo), png=png,
        legenda=inline(legenda), alt=html.escape(ALT[n]), corpo=corpo), encoding="utf-8")
    return saida


def main() -> None:
    edicoes = [int(a) for a in sys.argv[1:]] or sorted(int(p.name[-2:]) for p in RAIZ.glob("edicao-[0-9][0-9]"))
    for n in edicoes:
        print("gerado:", gerar(n).relative_to(RAIZ.parent))


if __name__ == "__main__":
    main()
