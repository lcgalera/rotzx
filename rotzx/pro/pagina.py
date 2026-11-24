"""Páginas públicas do rotzx Pro no site (D77, D78, D79): /pro/ e /pro/privacidade/.

Geradas no build, com o molde das páginas estáticas (rotzx/mundo/paginas.py): mesmo tema do atlas (chave rotzx-tema), CSP e medição.
A página Pro tem CSS próprio (ESTILO_PRO), só nela. Sem preço (sai das conversas da Fase 0) e sem slogan. O botão de pedido aponta
para o formulário de briefing (Google Forms do dono) quando FORMULARIO estiver preenchido; senão, para o LinkedIn.
"""
import html
from pathlib import Path
from typing import Callable, List

FORMULARIO = "https://docs.google.com/forms/d/e/1FAIpQLScjz5rhGd8X_tY7Xmy04O2P9NqgBCd5dU8L-s_cuMtGcxPPMg/viewform"  # link do Google Forms do briefing (preenchido pelo dono)
LINKEDIN = "https://www.linkedin.com/in/lucasfgalera"
PAGINAS_AMOSTRA = 12                                                 # páginas do estudo-fertilizantes.pdf gerado por `rotzx pro-amostra`
e = html.escape

PERGUNTAS = [
    "Para quais países vale a pena exportar meu produto, e quem já compra do Brasil?",
    "De quem o Brasil compra o insumo que eu uso, e quanto depende de cada fornecedor?",
    "O preço do meu produto subiu porque vendemos mais caro ou porque vendemos mais?",
    "Como o meu estado se compara com o resto do Brasil no meu produto?",
    "Por quais portos sai ou entra a minha mercadoria, e como isso mudou?",
]
# o que a API mensal do Comex Stat entrega além do atlas (conferido no teste da API, D76); a dica aparece ao passar o mouse (D79)
RECORTES = [
    ("NCM 8 dígitos", "O item exato da Nomenclatura Comum do Mercosul, dentro de cada SH4 do atlas"),
    ("Por estado (UF)", "O estado informado no Comex Stat para cada operação"),
    ("Porto/aeroporto e via", "A unidade da Receita Federal por onde a mercadoria passou e o modal de transporte"),
    ("Mês a mês, com peso (kg)", "Valor e peso líquido por mês, até o último mês publicado pelo MDIC"),
    ("Preço médio (US$/t)", "Valor FOB dividido pelo peso líquido, em dólares por tonelada"),
    ("Preço × volume", "Quanto da mudança de valor veio do preço e quanto veio da quantidade"),
]
PLANOS = [
    ("Diagnóstico", "PDF + planilha + conversa opcional", True,
     ["Um estudo sobre a sua pergunta", "Cada número com a fonte e a data", "Análise separada dos fatos",
      "Escopo enxuto para perguntas pontuais"]),
    ("Acompanhamento", "Entrega mensal", False,
     ["O mesmo recorte a cada nova base mensal do Comex Stat", "O que mudou: preço, volume e participação",
      "Mercados e fornecedores que entraram e saíram"]),
    ("Sob medida", "Escopo customizado", False,
     ["Vários produtos, setores ou estados num estudo só", "Licença do atlas para o seu site, com a sua marca e recortes do seu setor ou estado"]),
]
PASSOS = [
    "Você conta a sua pergunta, os produtos, os países e o estado que interessam.",
    "Você recebe por e-mail o escopo, o prazo e o valor, em até 2 dias úteis.",
    "Com o seu ok, você recebe o estudo: cada número com a fonte e a data, e a análise separada dos fatos.",
    "Se quiser, o mesmo recorte passa a chegar todo mês.",
]

ESTILO_PRO = """
:root{--card:#FCFBF7;--borda:rgb(34 39 33/.08);--raio:14px;--sombra:0 1px 2px rgb(34 39 33/.05),0 12px 32px -16px rgb(34 39 33/.22);--brilho:rgb(56 83 68/.22)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--card:#1D221E;--borda:rgb(233 230 222/.07);--sombra:inset 0 1px 0 rgb(255 255 255/.03),0 16px 36px -18px rgb(0 0 0/.75);--brilho:rgb(141 186 159/.25)}}
:root[data-theme="dark"]{--card:#1D221E;--borda:rgb(233 230 222/.07);--sombra:inset 0 1px 0 rgb(255 255 255/.03),0 16px 36px -18px rgb(0 0 0/.75);--brilho:rgb(141 186 159/.25)}
main.pro{max-width:1120px;padding:0 24px 40px}
footer{max-width:1120px;padding-inline:24px}
.pro p{max-width:62ch}
.pro .kicker{letter-spacing:.12em;font-size:12px}
.pro h2{font-size:clamp(28px,3vw,36px);line-height:1.12;letter-spacing:-.015em;margin:0 0 10px}
.bloco{margin-top:clamp(72px,9vw,120px)}
.pro .sub{font-size:15px;color:var(--ink-2);margin:0 0 28px}
.cartao{background:var(--card);border:1px solid var(--borda);border-radius:var(--raio);padding:26px 28px}
/* hero */
.hero{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:clamp(32px,5vw,64px);align-items:center;padding-block:clamp(40px,7vw,88px) 0}
.hero h1{font-size:clamp(38px,5.2vw,60px);line-height:1.04;letter-spacing:-.022em;margin:14px 0 20px}
.hero .lead{font-size:clamp(17px,1.5vw,19.5px);line-height:1.55;color:var(--ink-2);max-width:58ch}
.miuda{font-size:13.5px;color:var(--muted);margin-top:16px;max-width:52ch}
.resumo h3{margin:0 0 16px;font-size:21px}
.resumo .linha{display:grid;grid-template-columns:64px minmax(0,1fr);gap:14px;padding:16px 0 4px;border-top:1px solid var(--borda)}
.resumo .rot{font-size:11.5px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);padding-top:5px}
.resumo .rot.pro-r{color:var(--accent)}
.resumo .base{font-size:15px;color:var(--ink-2)}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;list-style:none}
.chips li{margin:0;font-size:13.5px;line-height:1.2;padding:7px 12px;border-radius:999px;background:var(--sel-bg);color:var(--accent-ink);border:1px solid transparent;cursor:default;transition:transform .2s,border-color .2s,background-color .2s}
.chips li:hover{border-color:var(--accent);transform:translateY(-2px)}
.resumo{transition:box-shadow .3s,border-color .3s}
.resumo:hover{border-color:var(--brilho);box-shadow:0 0 0 4px var(--brilho),var(--sombra)}
/* CTAs */
.pro .cta,.leitura .cta{display:inline-flex;align-items:center;gap:8px;border-radius:999px;padding:12px 22px;margin:6px 0 0;font-weight:500;transition:background-color .2s,box-shadow .2s,transform .2s}
.pro .cta:hover{box-shadow:0 8px 20px -10px var(--accent);transform:translateY(-1px)}
.pro .cta:focus-visible,.volta:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.seta{display:inline-block;transition:transform .2s cubic-bezier(.2,.7,.2,1)}
.cta:hover .seta,.volta:hover .seta{transform:translateX(4px)}
.volta:hover .seta{transform:translateX(-4px)}
.cta.sec{background:transparent;color:var(--accent-ink);box-shadow:inset 0 0 0 1px var(--accent)}
.cta.sec:hover{background:var(--sel-bg);box-shadow:inset 0 0 0 1px var(--accent),0 8px 20px -12px var(--accent)}
.cta.sec:hover .seta{transform:translate(2px,-2px)}
/* para quem e perguntas */
.publico{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:28px;margin:28px 0 24px}
.publico div{position:relative;padding-left:18px}
.publico div::before{content:"";position:absolute;left:0;top:9px;width:7px;height:7px;border-radius:50%;background:var(--accent)}
.publico b{display:block;font:500 19px/1.25 Newsreader,Georgia,serif;margin-bottom:6px}
.publico span{font-size:14.5px;color:var(--ink-2)}
ul.perg{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;padding:0;margin:28px 0 0;list-style:none}
ul.perg li{margin:0;max-width:none;padding:18px 22px;background:var(--card);border:1px solid var(--borda);border-radius:12px;font-size:15.5px}
/* planos */
.planos{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;align-items:stretch}
.plano{display:flex;flex-direction:column;position:relative;transition:transform .25s cubic-bezier(.2,.7,.2,1),box-shadow .25s,border-color .25s}
.plano.destaque{border-color:var(--accent);box-shadow:var(--sombra)}
.formato{font-size:11.5px;font-weight:600;letter-spacing:.11em;text-transform:uppercase;color:var(--accent-ink)}
.plano h3{margin:8px 0 16px;font-size:26px;letter-spacing:-.01em}
.etiqueta{position:absolute;top:-12px;left:24px;background:var(--accent);color:var(--on-accent);font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;padding:4px 9px;border-radius:999px}
.plano ul{padding:0;margin:0;list-style:none;flex:1}
.plano li{position:relative;padding:9px 0 9px 22px;border-top:1px solid var(--borda);font-size:15px;max-width:none;margin:0}
.plano li::before{content:"";position:absolute;left:2px;top:17px;width:8px;height:8px;border-radius:50%;background:var(--accent);opacity:.85}
.aviso{display:grid;grid-template-columns:auto minmax(0,1fr);gap:14px;align-items:start;margin-top:20px;padding:18px 22px;border-radius:12px;background:color-mix(in srgb,var(--accent) 7%,var(--bg));font-size:14.5px;color:var(--ink-2)}
.aviso .i{display:grid;place-items:center;width:22px;height:22px;border-radius:50%;background:var(--accent);color:var(--on-accent);font:600 13px/1 Newsreader,Georgia,serif}
.aviso p{margin:0;max-width:78ch}
/* como funciona */
.passos{--linha:1;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px;padding:0;margin:32px 0 0;list-style:none;position:relative}
.passos::before{content:"";position:absolute;left:26px;right:calc((100% - 72px) / 4 - 26px);top:26px;height:2px;border-radius:2px;background:var(--accent);opacity:.45;transform-origin:left;transform:scaleX(var(--linha));transition:transform .9s cubic-bezier(.4,.1,.2,1)}
.passos li{position:relative;margin:0;max-width:none;font-size:15px;color:var(--ink-2);transition:color .2s}
.passos .num{display:grid;place-items:center;width:52px;height:52px;border-radius:50%;background:var(--accent);border:1px solid var(--accent);color:var(--on-accent);font:500 18px/1 Newsreader,Georgia,serif;margin-bottom:16px;position:relative;transition:background-color .35s,color .35s,transform .25s,box-shadow .25s}
.passos li:hover{color:var(--ink)}
.passos li:hover .num{transform:scale(1.08);box-shadow:0 0 0 6px var(--brilho)}
/* estudo-amostra */
.amostra{display:grid;grid-template-columns:240px minmax(0,1fr);gap:clamp(28px,4vw,56px);align-items:center;padding:32px clamp(24px,4vw,48px)}
.previa{position:relative;width:200px;height:283px;margin:6px 0 6px 10px}
.previa img{position:absolute;inset:0;width:200px;height:auto;border-radius:4px;background:#fff;box-shadow:0 1px 2px rgb(0 0 0/.12),0 14px 30px -14px rgb(0 0 0/.45);transition:transform .45s cubic-bezier(.2,.7,.2,1)}
.previa .tras{transform:rotate(7deg) translate(36px,2px)}
.previa .selo{position:absolute;left:-10px;bottom:16px;z-index:2;background:var(--ochre);color:#fff;font-size:11px;font-weight:600;letter-spacing:.08em;padding:4px 9px;border-radius:999px}
.amostra:hover .tras{transform:rotate(11deg) translate(52px,-4px)}
.amostra:hover .frente{transform:rotate(-2deg) translateY(-4px)}
.amostra h3{margin:10px 0 10px;font-size:clamp(24px,2.4vw,30px);line-height:1.15;letter-spacing:-.01em}
.amostra .meta{font-size:13px;letter-spacing:.02em;color:var(--muted);font-variant-numeric:tabular-nums;margin-bottom:16px}
.amostra ul{display:flex;flex-wrap:wrap;gap:8px 20px;padding:0;margin:0 0 22px;list-style:none;font-size:15px}
.amostra .planilha{display:inline-block;margin:10px 0 0 16px;font-size:14.5px}
.amostra ul li{margin:0}.amostra ul li::before{content:"✓ ";color:var(--accent)}
/* faixa e cuidados */
.faixa{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:20px;margin-top:clamp(72px,9vw,120px);padding:clamp(28px,4vw,44px) clamp(24px,4vw,48px);border-radius:var(--raio);background:var(--card);border:1px solid var(--borda)}
.faixa p{margin:0;font:500 clamp(22px,2.4vw,28px)/1.2 Newsreader,Georgia,serif;letter-spacing:-.01em}
.pro .cuidados{margin-top:56px;padding-top:28px;border-top:1px solid var(--borda)}
/* privacidade */
.leitura{max-width:68ch;margin:clamp(32px,6vw,64px) auto 0;padding:clamp(28px,5vw,52px);background:var(--card);border:1px solid var(--borda);border-radius:var(--raio)}
.leitura h1{font-size:clamp(34px,4.4vw,48px);letter-spacing:-.02em;line-height:1.06}
.leitura h2{font-size:22px;margin-top:36px}
.volta{text-decoration:none;font-weight:500}
/* movimento: só para quem não pediu menos movimento */
@keyframes sobe{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes acende{0%,100%{background:var(--sel-bg)}40%{background:var(--brilho)}}
@keyframes pulso{0%{box-shadow:0 0 0 0 var(--brilho)}70%,100%{box-shadow:0 0 0 7px transparent}}
@media (prefers-reduced-motion:no-preference){
  .hero>div>*,.hero>aside{animation:sobe .6s cubic-bezier(.2,.7,.2,1) both}
  .hero>div>:nth-child(2){animation-delay:75ms}.hero>div>:nth-child(3){animation-delay:150ms}
  .hero>div>:nth-child(4){animation-delay:225ms}.hero>div>:nth-child(5){animation-delay:300ms}.hero>aside{animation-delay:300ms}
  .chips li{animation:acende .9s ease both}
  .chips li:nth-child(1){animation-delay:.75s}.chips li:nth-child(2){animation-delay:.84s}.chips li:nth-child(3){animation-delay:.93s}
  .chips li:nth-child(4){animation-delay:1.02s}.chips li:nth-child(5){animation-delay:1.11s}.chips li:nth-child(6){animation-delay:1.2s}
  .etiqueta{animation:pulso 2.8s ease-out 1.2s 3}
  .revelar{opacity:0;transform:translateY(16px);transition:opacity .7s cubic-bezier(.2,.7,.2,1),transform .7s cubic-bezier(.2,.7,.2,1)}
  .revelar.visto{opacity:1;transform:none}
  .revelar.grupo{opacity:1;transform:none}
  .revelar.grupo>*{opacity:0;transform:translateY(16px);transition:opacity .6s cubic-bezier(.2,.7,.2,1),transform .6s cubic-bezier(.2,.7,.2,1)}
  .revelar.grupo.visto>*{opacity:1;transform:none}
  .revelar.grupo>:nth-child(2){transition-delay:70ms}.revelar.grupo>:nth-child(3){transition-delay:140ms}
  .revelar.grupo>:nth-child(4){transition-delay:210ms}.revelar.grupo>:nth-child(5){transition-delay:280ms}
  .passos.revelar{--linha:0}.passos.revelar.visto{--linha:1}
  .passos.revelar .num{background:var(--bg);color:var(--accent)}
  .passos.revelar.visto .num{background:var(--accent);color:var(--on-accent)}
  .passos.revelar.visto li:nth-child(1) .num{transition-delay:.2s}.passos.revelar.visto li:nth-child(2) .num{transition-delay:.4s}
  .passos.revelar.visto li:nth-child(3) .num{transition-delay:.6s}.passos.revelar.visto li:nth-child(4) .num{transition-delay:.8s}
  @media (hover:hover){.plano:hover{transform:translateY(-4px);box-shadow:var(--sombra);border-color:var(--accent)}}
}
@media (prefers-reduced-motion:reduce){
  .chips li:hover,.pro .cta:hover,.cta:hover .seta,.volta:hover .seta,.cta.sec:hover .seta,.passos li:hover .num,.amostra:hover .tras,.amostra:hover .frente{transform:none}
  .amostra:hover .tras{transform:rotate(7deg) translate(36px,2px)}
}
@media (max-width:880px){
  .hero{grid-template-columns:minmax(0,1fr)}
  ul.perg{grid-template-columns:minmax(0,1fr)}
  .planos{grid-template-columns:minmax(0,1fr)}
  .passos{grid-template-columns:minmax(0,1fr);gap:22px}
  .passos::before{left:26px;right:auto;top:26px;bottom:26px;width:2px;height:auto;transform-origin:top;transform:scaleY(var(--linha))}
  .passos li{display:grid;grid-template-columns:52px minmax(0,1fr);gap:16px;align-items:center}.passos .num{margin:0}
  .amostra{grid-template-columns:minmax(0,1fr);justify-items:start}
}
@media (max-width:480px){main.pro{padding:0 16px 32px}.cartao{padding:22px 20px}.faixa{padding:24px 20px}.previa{width:170px;height:241px}.previa img{width:170px}}
"""

# D79: revelação ao rolar, uma vez só. Só marca o que está abaixo da dobra (sem flash, sem CLS); sem JS ou com menos movimento,
# tudo já aparece.
SCRIPT_PRO = """<script>(() => {
if (matchMedia("(prefers-reduced-motion: reduce)").matches || !("IntersectionObserver" in window)) return;
const io = new IntersectionObserver((es) => es.forEach((x) => { if (x.isIntersecting) { x.target.classList.add("visto"); io.unobserve(x.target); } }),
  { threshold: 0.15, rootMargin: "0px 0px -8% 0px" });
document.querySelectorAll("[data-revelar]").forEach((el) => {
  if (el.getBoundingClientRect().top < innerHeight * 0.92) return;
  el.classList.add("revelar"); if (el.dataset.revelar === "grupo") el.classList.add("grupo"); io.observe(el); });
})();</script>"""


def rodape(gerado: str) -> str:
    """Rodapé das páginas Pro (D78): a data fixa é do retrato público do atlas; os estudos usam a base mensal mais recente."""
    return (f"Fonte: Comex Stat (MDIC), dados abertos. A data {e(gerado)} se refere ao retrato público do atlas gratuito; os estudos do "
            "rotzx Pro usam a base mensal mais recente publicada pelo MDIC no Comex Stat. Valores em US$ FOB correntes; dado ausente "
            "aparece como “sem registro”, nunca como zero.")


def corpo_pro() -> str:
    pedido = e(FORMULARIO or LINKEDIN)
    rot = "Enviar meu pedido" if FORMULARIO else "Fale comigo no LinkedIn"
    chips = "".join(f'<li title="{e(dica)}">{e(c)}</li>' for c, dica in RECORTES)
    planos = "".join(
        f'<article class="cartao plano{" destaque" if dest else ""}">{"<span class=etiqueta>Ponto de partida</span>" if dest else ""}'
        f'<span class="formato">{e(badge)}</span><h3>{e(nome)}</h3><ul>{"".join(f"<li>{e(i)}</li>" for i in itens)}</ul></article>'
        for nome, badge, dest, itens in PLANOS)
    passos = "".join(f'<li><span class="num">{i:02d}</span><span>{e(p)}</span></li>' for i, p in enumerate(PASSOS, 1))
    seta = '<span class="seta" aria-hidden="true">→</span>'
    return f"""<section class="hero">
<div><div class="kicker">rotzx Pro</div>
<h1>Análise sob demanda do comércio exterior</h1>
<p class="lead">Do pequeno negócio e da pessoa física à empresa importadora: você traz a pergunta; o rotzx Pro responde com dados
públicos e oficiais, cruzados, conferidos e explicados.</p>
<a class="cta" href="{pedido}" rel="noopener">{rot} {seta}</a>
<p class="miuda">Pedido individual? Empresa e cargo são opcionais no formulário. Você recebe por e-mail o escopo, o prazo e o valor
antes de qualquer compromisso.</p></div>
<aside class="cartao resumo" aria-label="O que o Pro abre além do atlas gratuito"><h3>O que o Pro abre além do atlas gratuito</h3>
<div class="linha"><span class="rot">Atlas</span><span class="base">Ano a ano, por país e produto (SH4), grátis.</span></div>
<div class="linha"><span class="rot pro-r">Pro</span><ul class="chips">{chips}</ul></div></aside>
</section>

<section class="bloco"><h2>Para quem</h2>
<div class="publico" data-revelar="grupo">
<div><b>Pessoas físicas, MEIs e pequenos negócios</b><span>Uma pergunta pontual sobre o seu produto ou mercado.</span></div>
<div><b>Profissionais autônomos</b><span>Pesquisadores, jornalistas e consultores independentes.</span></div>
<div><b>Produtores e cooperativas</b><span>Para onde vai a produção e de onde vêm os insumos.</span></div>
<div><b>Empresas e entidades</b><span>Importadoras, exportadoras, tradings, despachantes e entidades setoriais.</span></div>
</div>
<p>Perguntas pontuais cabem em escopos enxutos, pensados para quem não precisa de um estudo grande.</p></section>

<section class="bloco"><h2>Perguntas que ele responde</h2>
<ul class="perg" data-revelar="grupo">{''.join(f'<li>{e(q)}</li>' for q in PERGUNTAS)}</ul></section>

<section class="bloco"><h2>O que você pode contratar</h2>
<p class="sub">Sem tabela fixa: o valor depende do tamanho do pedido e vem junto com o escopo, antes de começar.</p>
<div class="planos" data-revelar="grupo">{planos}</div>
<div class="aviso" data-revelar><span class="i" aria-hidden="true">i</span><p>Diferente do <b>Incorporar</b> do atlas, que é grátis e mostra
o atlas público como está, com a marca rotzx: a licença traz uma versão com a sua marca no lugar da do rotzx e recortes do seu setor
ou estado. Os créditos das fontes (MDIC, ONU e as demais) continuam sempre visíveis.</p></div></section>

<section class="bloco"><h2>Como funciona</h2>
<ol class="passos" data-revelar>{passos}</ol></section>

<section class="bloco"><h2>Veja um exemplo</h2>
<div class="cartao amostra" data-revelar>
<div class="previa"><img class="tras" src="estudo-p3.webp" width="480" height="680" loading="lazy" decoding="async"
alt="Página do estudo que divide a variação do valor importado em volume, preço e mix">
<img class="frente" src="estudo-p1.webp" width="480" height="680" loading="lazy" decoding="async" alt="Capa do estudo-amostra de fertilizantes">
<span class="selo">PDF · {PAGINAS_AMOSTRA} páginas</span></div>
<div><div class="kicker">Estudo-amostra com dados reais</div>
<h3>De quem o Brasil compra fertilizantes, e o que mudou em 2026</h3>
<div class="meta">SH4 3101 a 3105 · importação · 2024 a out/2026 · {PAGINAS_AMOSTRA} páginas</div>
<ul><li>Volume × preço × mix</li><li>Preço por produto e origem</li><li>Referência do Banco Mundial</li><li>Dependência por produto</li>
<li>Calendário de compra</li><li>Portos e frete</li><li>Contexto de fornecimento</li><li>Leitura por perfil</li></ul>
<a class="cta sec" href="estudo-fertilizantes.pdf" target="_blank" rel="noopener">Abrir o estudo (PDF) <span class="seta" aria-hidden="true">↗</span></a>
<a class="planilha" href="estudo-fertilizantes.xlsx" download>Baixar as tabelas (.xlsx)</a></div>
</div></section>

<div class="faixa" data-revelar><p>Tem uma pergunta sobre comércio exterior?</p><a class="cta" href="{pedido}" rel="noopener">{rot} {seta}</a></div>

<section class="cuidados"><h3>Dados e cuidados</h3>
<p>Comex Stat (MDIC), com detalhe por mês, produto (NCM), país, estado, porto e via, além do contexto do atlas: votos na ONU,
disputas na OMC, conflitos (UCDP/PRIO) e Banco Mundial. Dado ausente aparece como “sem registro”, nunca como zero, e toda
participação diz sobre qual total foi calculada.</p>
<p class="nota">Análise de dados públicos; não é recomendação de investimento ou de negócio. Como os dados do seu pedido são tratados:
<a href="privacidade/">política de privacidade</a>.</p></section>"""


PRIVACIDADE = f"""<article class="leitura"><p class="nota"><a class="volta" href="../"><span class="seta">←</span> Voltar ao rotzx Pro</a></p>
<div class="kicker">rotzx Pro</div><h1>Política de privacidade</h1>
<p class="lead">Como são tratados os dados que você envia ao pedir um estudo, seja em nome de uma empresa ou como pessoa física.</p>
<h2>O que é coletado</h2>
<p>Só o que você escreve no formulário de pedido: nome, e-mail, empresa e cargo (opcionais) e as informações do pedido (pergunta,
produtos, países, estado, período, uso e prazo).</p>
<h2>Para quê</h2>
<p>Para responder ao seu pedido, combinar o escopo e, se você contratar, preparar e entregar o estudo. Os dados não são vendidos nem
usados para outra finalidade.</p>
<h2>Onde ficam e por quanto tempo</h2>
<p>As respostas ficam numa planilha privada do responsável pelo rotzx (o formulário é do Google, que atua como operador). São guardadas
por até 12 meses depois do último contato, ou menos, se você pedir a exclusão.</p>
<h2>Seus direitos</h2>
<p>Você pode pedir acesso, correção ou exclusão dos seus dados a qualquer momento, pelo <a href="{LINKEDIN}" rel="noopener">LinkedIn do responsável</a>.</p>
<h2>Navegação no site</h2>
<p>O site conta visitas de forma agregada (GoatCounter), sem cookies e sem identificar pessoas, e respeita o pedido “não rastrear” do navegador.
A escolha de tema claro ou escuro fica só no seu navegador.</p>
<p class="nota">Base legal: consentimento, dado ao marcar a caixa no formulário (Lei 13.709/2018, LGPD).</p></article>"""


def gerar(out: Path, pagina: Callable[..., str], gerado: str) -> List[str]:
    """Escreve pro/index.html e pro/privacidade/index.html; devolve os caminhos para o sitemap."""
    (out / "pro" / "privacidade").mkdir(parents=True, exist_ok=True)
    (out / "pro" / "index.html").write_text(pagina(
        titulo="rotzx Pro: análise sob demanda do comércio exterior",
        desc="Estudos sob demanda sobre exportações e importações do Brasil, para pessoas, pequenos negócios e empresas: mercados, "
             "fornecedores, preço e volume, estados e portos, com dados públicos e oficiais.",
        caminho="pro/", raiz="../", corpo=corpo_pro(), contar="/pro", gerado=gerado,
        estilo_extra=ESTILO_PRO, rodape=rodape(gerado), classe="pro", script_extra=SCRIPT_PRO), encoding="utf-8")
    (out / "pro" / "privacidade" / "index.html").write_text(pagina(
        titulo="rotzx Pro: política de privacidade", desc="Como o rotzx Pro trata os dados enviados no pedido de estudo.",
        caminho="pro/privacidade/", raiz="../../", corpo=PRIVACIDADE, contar="/pro/privacidade", gerado=gerado,
        estilo_extra=ESTILO_PRO, rodape=rodape(gerado), classe="pro priv"), encoding="utf-8")
    return ["pro/", "pro/privacidade/"]
