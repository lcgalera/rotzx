"""Páginas estáticas do atlas, uma por país/território e uma por produto (D66).

O atlas guarda o estado depois do `#`, que buscadores e redes sociais não leem. Este módulo gera, no build
público, HTML simples com os mesmos números de `dados/historia.json` e `dados/produtos.json`:

    pais/{slug}/index.html      produto/{codigo}/index.html
    pais/index.html             produto/index.html            sitemap.xml   robots.txt

Não coleta nada e não inventa número: só reescreve o que já está nos arquivos de dados, com fonte, ano e
denominador. Cada página leva ao atlas interativo no estado correspondente.
"""
import html
import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional

BASE = "https://lcgalera.github.io/rotzx/"
FONTE = "Comex Stat (MDIC)"


def nf(v: float, c: int) -> str:
    return f"{v:,.{c}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def usd(v: Optional[float]) -> str:
    """Mesma regra da página: escala adaptada à grandeza; ausente é "sem registro", nunca zero."""
    if v is None:
        return "sem registro"
    if v == 0:
        return "US$ 0"
    a, s = abs(v), "−" if v < 0 else ""
    if a >= 1e12:
        return f"{s}US$ {nf(a / 1e12, 2)} tri"
    if a >= 1e9:
        return f"{s}US$ {nf(a / 1e9, 0 if a >= 1e11 else 1)} bi"
    if a >= 1e6:
        return f"{s}US$ {nf(a / 1e6, 0 if a >= 1e8 else 1)} mi"
    if a >= 1e3:
        return f"{s}US$ {nf(a / 1e3, 0)} mil"
    return f"{s}US$ {nf(a, 0)}"


def pct(x: Optional[float]) -> str:
    if x is None:
        return "sem registro"
    if x == 0:
        return "0%"
    if abs(x) < 0.0005:
        return "menos de 0,1%"
    return nf(x * 100, 1) + "%"


def slug(texto: str) -> str:
    t = unicodedata.normalize("NFD", texto.lower())
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def slugs_paises(paises: Dict[str, dict], ids: List[str]) -> Dict[str, str]:
    """Slug pelo nome; em caso de repetição, acrescenta o ISO3 (o endereço não pode mudar de dono)."""
    vistos: Dict[str, str] = {}
    out = {}
    for i in sorted(ids):
        s = slug(paises[i]["nome"]) or paises[i]["iso3"].lower()
        if s in vistos:
            s = f"{s}-{paises[i]['iso3'].lower()}"
        vistos[s] = i
        out[i] = s
    return out


# D78: o mesmo tema do atlas (chave rotzx-tema): o script do <head> evita o flash; o do fim liga o botão.
TEMA_CEDO = ('<script>try { const t = localStorage.getItem("rotzx-tema"); if (t === "light" || t === "dark") '
             'document.documentElement.dataset.theme = t; } catch (e) { /* sem armazenamento: tema do sistema */ }</script>')
TEMA_BOTAO = """<script>(() => {
const b = document.getElementById("tema"), R = document.documentElement, N = { light: "claro", dark: "escuro" }, I = {
  light: '<circle cx="12" cy="12" r="4.25" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
  dark: '<path d="M19.5 14.5A8 8 0 0 1 9.5 4.5a8 8 0 1 0 10 10z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>' };
const mm = matchMedia("(prefers-color-scheme: dark)"), ef = () => R.dataset.theme || (mm.matches ? "dark" : "light");
const escolhido = () => { try { return !!localStorage.getItem("rotzx-tema"); } catch (e) { return !!R.dataset.theme; } };
function pintar() { const a = ef(), o = a === "dark" ? "light" : "dark", sis = escolhido() ? "" : " (do sistema)";
  b.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">${I[a]}</svg>`;
  b.setAttribute("aria-label", `Tema ${N[a]}${sis}. Mudar para o tema ${N[o]}`); b.title = `Tema ${N[a]}${sis}. Clique para o tema ${N[o]}`; }
b.onclick = () => { const t = ef() === "dark" ? "light" : "dark"; R.dataset.theme = t;
  try { localStorage.setItem("rotzx-tema", t); } catch (e) { /* só nesta visita */ } pintar(); };
mm.addEventListener && mm.addEventListener("change", () => { if (!escolhido()) pintar(); });
pintar();
const nav = document.querySelector("header nav"), at = nav && nav.querySelector('[aria-current="page"]');   // celular: item ativo à vista
if (at && nav.scrollWidth > nav.clientWidth) nav.scrollLeft = at.offsetLeft + at.offsetWidth - nav.clientWidth + 12;
})();</script>"""

ESTILO = """
:root{--hover:#ECE9E0;--bg:#F3F0E8;--surface:#FAF8F3;--ink:#222721;--ink-2:#464C45;--muted:#676B62;--rule:#D8D4C9;--rule-2:#BDB8AB;--accent:#385344;--accent-ink:#2C4436;--ochre:#A16D2F;--on-accent:#FAF8F3;--sel-bg:#E3E9E1;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#151916;--surface:#1C211D;--ink:#E9E6DE;--ink-2:#C3C2B8;--muted:#9C9D93;--rule:#343A34;--rule-2:#4A514A;--accent:#8DBA9F;--accent-ink:#A9D0B8;--ochre:#D7A465;--on-accent:#151916;--sel-bg:#26302A;--hover:#222823;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#151916;--surface:#1C211D;--ink:#E9E6DE;--ink-2:#C3C2B8;--muted:#9C9D93;--rule:#343A34;--rule-2:#4A514A;--accent:#8DBA9F;--accent-ink:#A9D0B8;--ochre:#D7A465;--on-accent:#151916;--sel-bg:#26302A;--hover:#222823;color-scheme:dark}
*{box-sizing:border-box}html,body{margin:0}
body{background:var(--bg);color:var(--ink);font:16px/1.6 "IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--accent);text-underline-offset:3px}
header{display:flex;align-items:center;gap:10px 22px;flex-wrap:wrap;padding:12px 24px;border-bottom:1px solid var(--ink);background:var(--bg)}
header .marca{display:inline-flex;align-items:center;color:var(--accent);text-decoration:none;font:600 26px/1 Newsreader,Georgia,serif}
header .logo{display:block;height:28px;aspect-ratio:1164/278;background:currentColor;-webkit-mask:var(--logo) no-repeat center/contain;mask:var(--logo) no-repeat center/contain}
header nav{display:flex;gap:2px;font-size:14.5px}
header nav a{position:relative;padding:7px 11px;border-radius:999px;color:var(--ink-2);text-decoration:none;white-space:nowrap;transition:color .2s,background-color .2s}
header nav a:hover{color:var(--ink);background:var(--hover)}
header nav a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
header nav a[aria-current="page"]{color:var(--ink);font-weight:500}
header nav a[aria-current="page"]::after{content:"";position:absolute;left:11px;right:11px;bottom:1px;height:2px;border-radius:2px;background:var(--accent);transform-origin:left;animation:traco .35s cubic-bezier(.2,.7,.2,1) both}
@keyframes traco{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@media (prefers-reduced-motion:reduce){header nav a[aria-current="page"]::after{animation:none}}
.tema{display:inline-grid;place-items:center;width:36px;height:36px;margin-left:auto;border:1px solid var(--rule-2);border-radius:50%;background:transparent;cursor:pointer;color:var(--ink-2);flex:none}
.tema:hover{color:var(--ink);border-color:var(--ink-2)}
@media (max-width:640px){header{position:relative;padding:10px 16px 6px}.tema{position:absolute;top:8px;right:16px}header nav{margin:0 -16px;padding:0 10px 4px;width:calc(100% + 32px);overflow-x:auto;scrollbar-width:none}header nav::-webkit-scrollbar{display:none}header nav a{padding:7px 9px;font-size:14px}header nav a[aria-current="page"]::after{left:9px;right:9px}}
main{max-width:860px;margin:0 auto;padding:28px 20px 60px}
.kicker{font-size:12px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:var(--accent)}
h1{font:500 40px/1.1 Newsreader,Georgia,serif;margin:6px 0 14px;letter-spacing:-.01em}
h2{font:500 24px/1.2 Newsreader,Georgia,serif;margin:34px 0 8px}
h3{font:500 19px/1.25 Newsreader,Georgia,serif;margin:26px 0 6px}
p{margin:0 0 12px;max-width:68ch}.lead{font-size:18px}
.fonte,.nota{font-size:13.5px;color:var(--muted)}
.cta{display:inline-block;margin:8px 0 4px;padding:11px 18px;border-radius:3px;background:var(--accent);color:var(--on-accent);text-decoration:none;font-weight:500}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);margin:18px 0}
.kpi{padding:12px 14px 12px 0}.kpi span{display:block;font-size:13px;color:var(--ink-2)}
.kpi b{display:block;font:500 25px/1.2 Newsreader,Georgia,serif}.kpi small{font-size:13px;color:var(--ink-2)}
table{border-collapse:collapse;width:100%;font-size:14.5px;font-variant-numeric:tabular-nums;margin:8px 0}
th,td{text-align:right;padding:7px 8px;border-bottom:1px solid var(--rule)}th:first-child,td:first-child{text-align:left}
thead th{border-bottom:1px solid var(--ink);font-weight:600}
.rolavel{overflow-x:auto}
ol,ul{padding-left:20px;margin:0 0 12px}ol li,ul li{margin-bottom:4px;max-width:68ch}
ul.cols{columns:3 200px;padding-left:18px;font-size:15px}ul.cols li{break-inside:avoid;margin-bottom:4px}
footer{max-width:860px;margin:0 auto;padding:18px 20px 40px;border-top:1px solid var(--ink);font-size:13.5px;color:var(--ink-2)}
"""


NAV = [("", "Atlas interativo"), ("pais/", "Países e territórios"), ("produto/", "Produtos"), ("pro/", "rotzx Pro")]


def _nav(raiz: str, caminho: str) -> str:
    """Navegação das páginas estáticas (D79): o item da seção atual leva aria-current (traço em --accent)."""
    sec = caminho.split("/", 1)[0] + "/" if "/" in caminho else ""
    atual = ' aria-current="page"'
    return "".join(f'<a href="{raiz}{h}"{atual if h and h == sec else ""}>{n}</a>' for h, n in NAV)


def logo_svg(atlas_html: Path) -> Optional[str]:
    """O logo do atlas (ícone + texto, inline em index.html) como arquivo para máscara CSS; None se não achar."""
    m = re.search(r'<svg class="logo"[^>]*viewBox="([^"]+)"[^>]*>(.*?)</svg>', atlas_html.read_text(encoding="utf-8"), re.S)
    if not m:
        return None
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{m.group(1)}">{m.group(2).replace("currentColor", "#000")}</svg>'


def _pagina(*, titulo: str, desc: str, caminho: str, raiz: str, corpo: str, contar: str, gerado: str, cartao: bool = False,
            estilo_extra: str = "", rodape: Optional[str] = None, classe: str = "", script_extra: str = "") -> str:
    e = html.escape
    url = BASE + caminho
    img = url + "cartao.png" if cartao else BASE + "og.png"     # D70: cartão próprio de cada país e produto
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: https://rotz.goatcounter.com; connect-src https://rotz.goatcounter.com; object-src 'none'; base-uri 'self'; form-action 'none'">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{e(titulo)} — rotzx</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="rotzx">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{e(titulo)} — rotzx">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(titulo)}. {e(desc)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(titulo)} — rotzx">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{img}">
{TEMA_CEDO}
<link rel="icon" href="{raiz}icone.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap" rel="stylesheet">
<style>{ESTILO}{estilo_extra}</style>
</head>
<body>
<header><a class="marca" href="{raiz}" aria-label="rotzx, início do atlas" style="--logo:url({raiz}logo.svg)"><span class="logo"></span></a>
<nav aria-label="Seções">{_nav(raiz, caminho)}</nav>
<button class="tema" id="tema" type="button" aria-label="Mudar o tema">◐</button></header>
<main{(' class="' + classe + '"') if classe else ""}>
{corpo}
</main>
<footer><p>{rodape if rodape is not None else f'Fonte: {FONTE}, dados abertos. Valores em US$ FOB correntes, sem correção pela inflação: alta em valor não prova alta em volume. Retrato dos dados coletado em {e(gerado)}, sem atualização em tempo real. Ano sem valor aparece como “sem registro”, nunca como zero.'}</p>
<p><a href="{raiz}#ver=fontes">Fontes e método</a> · Autor: <a href="https://www.linkedin.com/in/lucasfgalera" rel="noopener">LinkedIn</a> · <a href="https://github.com/lcgalera" rel="noopener">GitHub</a></p></footer>
{TEMA_BOTAO}{script_extra}
<script src="{raiz}medicao.js"></script>
<script>window.rotzxContar && rotzxContar({json.dumps(contar)});</script>
</body>
</html>
"""


def _em(serie, ano, ini):
    k = ano - ini
    return serie[k] if serie and 0 <= k < len(serie) else None


def _det(dados: Path, tipo: str, chave: str, camada: str) -> dict:
    """Camada do detalhamento (D68), se o arquivo existir: {fluxo: {ano: {t, n, top}}}."""
    arq = dados / "detalhe" / tipo / f"{chave}.json"
    if not arq.exists():
        return {}
    try:
        return json.loads(arq.read_text(encoding="utf-8")).get(camada) or {}
    except ValueError:
        return {}


def _serie_tabela(cab: List[str], linhas: List[List[str]]) -> str:
    th = "".join(f"<th scope=\"col\">{html.escape(c)}</th>" for c in cab)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>" for l in linhas)
    return f'<div class="rolavel"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def gerar(out: Path, dados: Path, cartoes: bool = True) -> Dict[str, int]:
    """Escreve as páginas em `out` a partir de `dados/historia.json` e `dados/produtos.json`.
    `cartoes=False` pula as imagens de compartilhamento (usado nos testes que não precisam delas)."""
    from . import cartao as cartao_m
    out, dados = Path(out), Path(dados)
    out.mkdir(parents=True, exist_ok=True)
    if (dados.parent / "index.html").exists() and (svg := logo_svg(dados.parent / "index.html")):
        (out / "logo.svg").write_text(svg, encoding="utf-8")         # D79: logo do atlas no cabeçalho das páginas estáticas
    H = json.loads((dados / "historia.json").read_text(encoding="utf-8"))
    P = json.loads((dados / "produtos.json").read_text(encoding="utf-8")) if (dados / "produtos.json").exists() else {"itens": {}}
    C, paises = H["comercio"], H["paises"]
    ini, fim = C["inicio"], C["fim"]
    gerado = H["gerado_em"][:10]
    gerado = f"{gerado[8:10]}/{gerado[5:7]}/{gerado[:4]}"
    br_e = lambda a: _em(C["brasil"]["e"], a, ini)
    br_i = lambda a: _em(C["brasil"]["i"], a, ini)
    e = html.escape
    nome_prod = lambda c: C.get("curtos", {}).get(c) or (P["itens"].get(c) or {}).get("nome") or C["sh4"].get(c) or c

    def tem(d):
        return any(v for v in (d.get("e") or []) if v) or any(v for v in (d.get("i") or []) if v)

    ids = [i for i, d in C["paises"].items() if i in paises and i != "076" and tem(d)]   # sem o próprio Brasil, como no atlas
    sl = slugs_paises(paises, ids)
    urls: List[str] = [""]

    def rank(k: str, ano: int) -> Dict[str, int]:
        r = sorted(((i, _em(C["paises"][i].get(k), ano, ini)) for i in ids), key=lambda x: -(x[1] or 0))
        return {i: n + 1 for n, (i, v) in enumerate([x for x in r if x[1]])}

    rk_e, rk_i = rank("e", fim), rank("i", fim)

    # ---------------- países ----------------
    for i in ids:
        d, nome = C["paises"][i], paises[i]["nome"]
        ex, im = _em(d.get("e"), fim, ini), _em(d.get("i"), fim, ini)
        terr = paises[i].get("tipo") == "territorio"
        kp, nums = [], []
        if ex is not None:
            nums.append(("Exportações do Brasil", usd(ex), f"{pct(ex / br_e(fim))} do total exportado" + (f" · {rk_e[i]}º destino de {len(rk_e)}" if i in rk_e else "")))
        if im is not None:
            nums.append(("Importações do Brasil", usd(im), f"{pct(im / br_i(fim))} do total importado" + (f" · {rk_i[i]}ª origem de {len(rk_i)}" if i in rk_i else "")))
        if ex is not None and im is not None:
            nums.append(("Saldo", ("+" if ex - im > 0 else "") + usd(ex - im), ("superávit" if ex - im >= 0 else "déficit") + " do Brasil"))
        if ex is not None:
            kp.append(f'<div class="kpi"><span>Exportações do Brasil</span><b>{usd(ex)}</b><small>{pct(ex / br_e(fim))} do total exportado pelo Brasil em {fim}'
                      + (f" · {rk_e[i]}º destino de {len(rk_e)}" if i in rk_e else "") + "</small></div>")
        else:
            kp.append(f'<div class="kpi"><span>Exportações do Brasil</span><b>sem registro</b><small>em {fim}</small></div>')
        if im is not None:
            kp.append(f'<div class="kpi"><span>Importações do Brasil</span><b>{usd(im)}</b><small>{pct(im / br_i(fim))} do total importado pelo Brasil em {fim}'
                      + (f" · {rk_i[i]}ª origem de {len(rk_i)}" if i in rk_i else "") + "</small></div>")
        else:
            kp.append(f'<div class="kpi"><span>Importações do Brasil</span><b>sem registro</b><small>em {fim}</small></div>')
        if ex is not None and im is not None:
            s = ex - im
            kp.append(f'<div class="kpi"><span>Saldo</span><b>{"+" if s > 0 else ""}{usd(s)}</b><small>{"superávit" if s >= 0 else "déficit"} do Brasil (exportações − importações)</small></div>')
        partes = []
        dt = _det(dados, "pais", paises[i]["iso3"], "produtos")
        for k, rot, verbo in (("e", "O que o Brasil vende", "vendas do Brasil a esse parceiro"), ("i", "O que o Brasil compra", "compras do Brasil desse parceiro")):
            x = (dt.get(k) or {}).get(str(fim)) or ((d.get("p") or {}).get(str(fim)) or {}).get(k)
            if not x:
                continue
            lp = lambda c: f'<a href="../../produto/{c}/">{e(nome_prod(c))}</a>' if c in P["itens"] else e(nome_prod(c))
            linhas = [[lp(c), usd(v), pct(v / x["t"])] for c, v in x["top"] if v > 0]
            partes.append(f"<h2>{rot} · {fim}</h2><p class=\"fonte\">{usd(x['t'])} em {x['n']} produtos (SH4). Abaixo, os {len(x['top'])} maiores; participação = valor do produto ÷ total das {verbo} no ano.</p>"
                          + _serie_tabela(["Produto", "Valor", "Parte do total"], linhas))
            anos_k = sorted((int(a) for a in (dt.get(k) or {})), reverse=True)
            if len(anos_k) > 3:
                la = [[str(a), lp(dt[k][str(a)]["top"][0][0]), usd(dt[k][str(a)]["top"][0][1]), pct(dt[k][str(a)]["top"][0][1] / dt[k][str(a)]["t"])] for a in anos_k]
                partes.append(f"<h3>Principal produto {'vendido' if k == 'e' else 'comprado'} em cada ano</h3><p class=\"fonte\">Parte = valor do produto ÷ total das {verbo} no ano. Ano sem registro não aparece.</p>"
                              + _serie_tabela(["Ano", "Produto", "Valor", "Parte do total"], la))
        linhas = [[str(a), usd(_em(d.get("e"), a, ini)), usd(_em(d.get("i"), a, ini))] for a in range(fim, ini - 1, -1)]
        resumo = (f"Em {fim}, o Brasil exportou {usd(ex)} para {nome}" if ex is not None else f"Em {fim}, não há registro de exportação do Brasil para {nome}") \
            + (f" e importou {usd(im)}." if im is not None else " e não há registro de importação.")
        corpo = f"""<div class="kicker">Comércio com o Brasil · {fim}</div>
<h1>{e(nome)} e o Brasil</h1>
<p class="lead">{e(resumo)}{" " + e(nome) + " é tratado como território na base." if terr else ""}</p>
<a class="cta" href="../../#pais={paises[i]['iso3']}">Abrir {e(nome)} no atlas interativo →</a>
<div class="kpis">{''.join(kp)}</div>
{''.join(partes)}
<h2>Série anual, {ini}–{fim}</h2>
<p class="fonte">{FONTE} · US$ FOB correntes · exportações do Brasil para o parceiro e importações do Brasil com origem nele</p>
{_serie_tabela(["Ano", "Exportações do Brasil", "Importações do Brasil"], linhas)}
<p class="nota">No atlas interativo há gráficos, comparação com outro parceiro, votos na ONU, disputas na OMC e download em CSV.</p>"""
        cam = f"pais/{sl[i]}/"
        (out / cam).mkdir(parents=True, exist_ok=True)
        (out / cam / "index.html").write_text(_pagina(
            titulo=f"{nome} e o Brasil: exportações e importações, {ini}–{fim}",
            desc=f"{resumo} Série anual desde {ini} e principais produtos. Fonte: {FONTE}.",
            caminho=cam, raiz="../../", corpo=corpo, contar=f"/pais/{paises[i]['iso3']}", gerado=gerado, cartao=cartoes), encoding="utf-8")
        if cartoes:
            cartao_m.desenhar(out / cam / "cartao.png", f"Comércio com o Brasil · {fim}", f"{nome} e o Brasil", nums)
        urls.append(cam)

    lis = "".join(f'<li><a href="{sl[i]}/">{e(paises[i]["nome"])}</a></li>' for i in sorted(ids, key=lambda i: slug(paises[i]["nome"])))
    (out / "pais" / "index.html").write_text(_pagina(
        titulo="Comércio do Brasil com cada país e território",
        desc=f"Exportações e importações do Brasil com {len(ids)} países e territórios, de {ini} a {fim}. Fonte: {FONTE}.",
        caminho="pais/", raiz="../", contar="/pais/",  gerado=gerado,
        corpo=f'<div class="kicker">Países e territórios</div><h1>Comércio do Brasil com cada parceiro</h1><p class="lead">{len(ids)} países e territórios com comércio registrado com o Brasil entre {ini} e {fim}.</p><ul class="cols">{lis}</ul>'), encoding="utf-8")
    urls.append("pais/")

    # ---------------- produtos ----------------
    itens = P.get("itens") or {}
    anos_p = sorted(int(a) for a in (P.get("anos_parceiros") or []))
    for cod, it in itens.items():
        nome = it["nome"]
        grupo = cod.startswith("g-")
        ve, vi = _em(it.get("e"), fim, ini), _em(it.get("i"), fim, ini)
        kp = [f'<div class="kpi"><span>Exportações do Brasil</span><b>{usd(ve)}</b><small>' + (f"{pct(ve / br_e(fim))} do total exportado pelo Brasil em {fim}" if ve else f"em {fim}") + "</small></div>",
              f'<div class="kpi"><span>Importações do Brasil</span><b>{usd(vi)}</b><small>' + (f"{pct(vi / br_i(fim))} do total importado pelo Brasil em {fim}" if vi else f"em {fim}") + "</small></div>"]
        partes = []
        dt = _det(dados, "prod", cod, "parceiros")
        lider = {}
        for k, rot, papel in (("e", "Para onde o Brasil vende", "destinos"), ("i", "De onde o Brasil compra", "origens")):
            anos_k = sorted((int(a) for a in (dt.get(k) or {})), reverse=True)
            ap = anos_k[0] if anos_k else max([a for a in anos_p if k in ((it.get("p") or {}).get(str(a)) or {})], default=None)
            x = (dt.get(k) or {}).get(str(ap)) or (((it.get("p") or {}).get(str(ap)) or {}).get(k) if ap else None)
            if not x:
                continue
            lc = lambda c: f'<a href="../../pais/{sl[c]}/">{e(paises[c]["nome"])}</a>' if c in sl else e((paises.get(c) or {}).get("nome", c))
            linhas = [[lc(c), usd(v), pct(v / x["t"])] for c, v in x["top"] if v > 0]
            if x["top"] and x["top"][0][1] > 0:
                lider[k] = ((paises.get(x["top"][0][0]) or {}).get("nome", ""), pct(x["top"][0][1] / x["t"]), ap)
            resto = x["t"] - sum(v for _, v in x["top"])
            if x["n"] > len(x["top"]) and resto > 0:
                linhas.append([f"Outros {x['n'] - len(x['top'])} {papel} (sem valor individual)", usd(resto), pct(resto / x["t"])])
            partes.append(f"<h2>{rot} · {ap}</h2><p class=\"fonte\">{usd(x['t'])} para {x['n']} {papel}. Participação = valor do parceiro ÷ total do Brasil neste produto no ano (operações com país identificado).</p>"
                          + _serie_tabela(["Parceiro", "Valor", "Parte do produto"], linhas)
                          + f'<a class="cta" href="../../#ver=produto&prod={cod}&fluxo={k}&m=prod&ano={ap}">Ver no mapa interativo →</a>')
            if len(anos_k) > 3:
                la = [[str(a), lc(dt[k][str(a)]["top"][0][0]), usd(dt[k][str(a)]["top"][0][1]), pct(dt[k][str(a)]["top"][0][1] / dt[k][str(a)]["t"]), str(dt[k][str(a)]["n"])] for a in anos_k]
                partes.append(f"<h3>Principal {'destino' if k == 'e' else 'origem'} em cada ano</h3><p class=\"fonte\">Parte = valor do parceiro ÷ total do Brasil neste produto no ano. Ano sem registro não aparece.</p>"
                              + _serie_tabela(["Ano", "Parceiro", "Valor", "Parte do produto", f"Nº de {papel}"], la))
        linhas = [[str(a), usd(_em(it.get("e"), a, ini)), usd(_em(it.get("i"), a, ini))] for a in range(fim, ini - 1, -1)]
        oficial = it.get("oficial") or C["sh4"].get(cod) or ""
        ident = "Grupo de posições SH4" if grupo else f"SH4 {cod}"
        resumo = f"Em {fim}, o Brasil exportou {usd(ve)} e importou {usd(vi)} de {nome.lower()}."
        corpo = f"""<div class="kicker">Produto · {e(ident)}</div>
<h1>{e(nome)}</h1>
<p class="lead">{e(resumo)}</p>
{f'<p class="fonte">Descrição oficial: {e(oficial)}</p>' if oficial and oficial != nome else ''}
<div class="kpis">{''.join(kp)}</div>
{''.join(partes)}
<h2>Série anual do Brasil, {ini}–{fim}</h2>
<p class="fonte">{FONTE} · US$ FOB correntes · total do Brasil, todos os parceiros</p>
{_serie_tabela(["Ano", "Exportações do Brasil", "Importações do Brasil"], linhas)}
<p class="nota">Os códigos SH4 mudaram nas revisões do Sistema Harmonizado: compare anos distantes com cuidado.</p>"""
        cam = f"produto/{cod}/"
        (out / cam).mkdir(parents=True, exist_ok=True)
        (out / cam / "index.html").write_text(_pagina(
            titulo=f"{nome}: exportações e importações do Brasil, {ini}–{fim}",
            desc=f"{resumo} Principais destinos e origens e série anual desde {ini}. Fonte: {FONTE}.",
            caminho=cam, raiz="../../", corpo=corpo, contar=f"/produto/{cod}", gerado=gerado, cartao=cartoes), encoding="utf-8")
        if cartoes:
            nums = []
            maior = "e" if (ve or 0) >= (vi or 0) else "i"                      # o fluxo mais relevante do produto vem primeiro
            for k in (maior, "i" if maior == "e" else "e"):
                v, tot = (ve, br_e(fim)) if k == "e" else (vi, br_i(fim))
                if v:
                    nums.append((f"{'Exportações' if k == 'e' else 'Importações'} do Brasil · {fim}", usd(v), f"{pct(v / tot)} do total {'exportado' if k == 'e' else 'importado'} pelo Brasil"))
            if lider.get(maior) and lider[maior][0]:
                nm, parte, ano_l = lider[maior]
                nums.insert(1, (f"Principal {'destino' if maior == 'e' else 'origem'} · {ano_l}", nm, f"{parte} das {'vendas' if maior == 'e' else 'compras'} brasileiras do produto"))
            cartao_m.desenhar(out / cam / "cartao.png", f"Produto · {ident}", nome, nums[:3])
        urls.append(cam)

    if itens:
        ordem = sorted(itens, key=lambda c: -((_em(itens[c].get("e"), fim, ini) or 0) + (_em(itens[c].get("i"), fim, ini) or 0)))
        lis = "".join(f'<li><a href="{c}/">{e(itens[c]["nome"])}</a></li>' for c in ordem)
        (out / "produto" / "index.html").write_text(_pagina(
            titulo="Produtos do comércio exterior do Brasil",
            desc=f"Exportações e importações do Brasil por produto (SH4), de {ini} a {fim}, com destinos e origens. Fonte: {FONTE}.",
            caminho="produto/", raiz="../", contar="/produto/", gerado=gerado,
            corpo=f'<div class="kicker">Produtos</div><h1>Produtos do comércio exterior do Brasil</h1><p class="lead">{len(itens)} produtos e grupos, em ordem de valor comercializado em {fim} (exportações + importações).</p><ul class="cols">{lis}</ul>'), encoding="utf-8")
        urls.append("produto/")

    from ..pro import pagina as pro_pagina                    # D77: páginas públicas do rotzx Pro
    urls += pro_pagina.gerar(out, _pagina, gerado)

    data = H["gerado_em"][:10]
    (out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     + "".join(f"<url><loc>{BASE}{u}</loc><lastmod>{data}</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n", encoding="utf-8")
    return {"paises": len(ids), "produtos": len(itens), "urls": len(urls)}
