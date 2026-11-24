"""Páginas públicas do rotzx Pro no site (D77, D78): /pro/ e /pro/privacidade/.

Geradas no build, com o molde das páginas estáticas (rotzx/mundo/paginas.py): mesmo tema do atlas (chave rotzx-tema), CSP e medição.
A página Pro tem CSS próprio (ESTILO_PRO), só nela. Sem preço (sai das conversas da Fase 0) e sem slogan. O botão de pedido aponta
para o formulário de briefing (Google Forms do dono) quando FORMULARIO estiver preenchido; senão, para o LinkedIn.
"""
import html
from pathlib import Path
from typing import Callable, List

FORMULARIO = "https://docs.google.com/forms/d/e/1FAIpQLScjz5rhGd8X_tY7Xmy04O2P9NqgBCd5dU8L-s_cuMtGcxPPMg/viewform"  # link do Google Forms do briefing (preenchido pelo dono)
LINKEDIN = "https://www.linkedin.com/in/lucasfgalera"
PAGINAS_AMOSTRA = 9                                                  # páginas do estudo-fertilizantes.pdf gerado por `rotzx pro-amostra`
e = html.escape

PERGUNTAS = [
    "Para quais países vale a pena exportar meu produto, e quem já compra do Brasil?",
    "De quem o Brasil compra o insumo que eu uso, e quanto depende de cada fornecedor?",
    "O preço do meu produto subiu porque vendemos mais caro ou porque vendemos mais?",
    "Como o meu estado se compara com o resto do Brasil no meu produto?",
    "Por quais portos sai ou entra a minha mercadoria, e como isso mudou?",
]
# o que a API mensal do Comex Stat entrega além do atlas (conferido no teste da API, D76)
RECORTES = ["NCM 8 dígitos", "Por estado (UF)", "Porto/aeroporto e via", "Mês a mês, com peso (kg)", "Preço médio (US$/t)", "Preço × volume"]
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
main.pro{max-width:1080px}
.pro h2{margin-top:56px}
.pro .sub{font-size:14.5px;color:var(--ink-2);margin:-2px 0 18px}
.hero{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:40px;align-items:center;padding:20px 0 8px}
.hero h1{font-size:46px;margin-top:8px}
.hero .lead{font-size:18.5px;color:var(--ink-2)}
.hero .cta{margin-top:10px}
.miuda{font-size:13.5px;color:var(--muted);margin-top:10px;max-width:52ch}
.cartao{background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:22px 24px}
.resumo h3{margin:0 0 14px;font-size:20px}
.resumo .linha{display:grid;grid-template-columns:86px minmax(0,1fr);gap:12px;padding:12px 0;border-top:1px solid var(--rule)}
.resumo .rot{font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);padding-top:4px}
.resumo .rot.pro-r{color:var(--accent)}
.resumo .base{font-size:15px;color:var(--ink-2)}
.chips{display:flex;flex-wrap:wrap;gap:7px;margin:0;padding:0;list-style:none}
.chips li{margin:0;font-size:13.5px;line-height:1.2;padding:6px 10px;border-radius:999px;background:var(--sel-bg);color:var(--accent-ink);border:1px solid var(--rule)}
.publico{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:12px;margin:14px 0 10px}
.publico div{border-top:2px solid var(--accent);padding-top:10px}
.publico b{display:block;font:500 18px/1.25 Newsreader,Georgia,serif;margin-bottom:3px}
.publico span{font-size:14.5px;color:var(--ink-2)}
ul.perg{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px 28px;padding:0;list-style:none}
ul.perg li{margin:0;padding:10px 0 10px 16px;border-left:2px solid var(--rule-2);max-width:none}
.planos{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:stretch}
.plano{display:flex;flex-direction:column;position:relative}
.plano.destaque{border-color:var(--accent);box-shadow:inset 0 3px 0 var(--accent)}
.plano h3{margin:0 0 10px;font-size:23px}
.etiqueta{position:absolute;top:-11px;left:20px;background:var(--accent);color:var(--on-accent);font-size:11.5px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;padding:3px 8px;border-radius:3px}
.badge{align-self:flex-start;font-size:12.5px;font-weight:500;color:var(--accent-ink);border:1px solid var(--accent);border-radius:3px;padding:3px 8px;margin-bottom:14px}
.plano ul{padding:0;margin:0;list-style:none;flex:1}
.plano li{position:relative;padding:7px 0 7px 20px;border-top:1px solid var(--rule);font-size:15px;max-width:none;margin:0}
.plano li::before{content:"";position:absolute;left:2px;top:15px;width:8px;height:8px;border-radius:50%;background:var(--accent)}
.plano .obs{font-size:13.5px;color:var(--ink-2);margin:14px 0 0;padding-top:12px;border-top:1px dashed var(--rule-2)}
.passos{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;padding:0;margin:18px 0 0;list-style:none;position:relative}
.passos::before{content:"";position:absolute;left:24px;right:24px;top:24px;height:1px;background:var(--rule-2)}
.passos li{position:relative;margin:0;max-width:none;font-size:15px}
.passos .num{display:grid;place-items:center;width:48px;height:48px;border-radius:50%;background:var(--bg);border:1px solid var(--accent);color:var(--accent);font:500 18px/1 Newsreader,Georgia,serif;margin-bottom:12px;position:relative}
.amostra{display:grid;grid-template-columns:150px minmax(0,1fr);gap:28px;align-items:center}
.folha{aspect-ratio:210/297;background:var(--bg);border:1px solid var(--rule-2);border-radius:3px;padding:16px 14px;display:flex;flex-direction:column;gap:7px;box-shadow:6px 6px 0 var(--rule)}
.folha i{display:block;height:5px;border-radius:2px;background:var(--rule-2)}
.folha i.t{height:9px;width:80%;background:var(--accent)}.folha i.c{width:60%}
.folha .g{flex:1;border-bottom:1px solid var(--rule-2);background:linear-gradient(to top,var(--sel-bg) 0 40%,transparent 40%)}
.folha b{align-self:flex-start;font-size:11px;letter-spacing:.08em;color:var(--on-accent);background:var(--ochre);padding:2px 6px;border-radius:2px}
.amostra h3{margin:4px 0 8px;font-size:24px}
.amostra .meta{font-size:13.5px;color:var(--muted);font-variant-numeric:tabular-nums;margin-bottom:10px}
.amostra ul{display:flex;flex-wrap:wrap;gap:6px 18px;padding:0;margin:0 0 14px;list-style:none;font-size:15px}
.amostra ul li{margin:0}.amostra ul li::before{content:"✓ ";color:var(--accent)}
.cta.sec{background:transparent;color:var(--accent-ink);border:1px solid var(--accent)}
.faixa{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:16px;margin-top:56px;border-top:1px solid var(--ink);border-bottom:1px solid var(--rule);padding:24px 0}
.faixa p{margin:0;font:500 24px/1.25 Newsreader,Georgia,serif}
.pro .cuidados{margin-top:40px}
footer{max-width:1080px}
@media (max-width:860px){
  .hero{grid-template-columns:minmax(0,1fr);gap:24px}.hero h1{font-size:36px}
  ul.perg{grid-template-columns:minmax(0,1fr)}
  .planos{grid-template-columns:minmax(0,1fr);gap:24px}
  .passos{grid-template-columns:minmax(0,1fr);gap:18px}
  .passos::before{left:24px;right:auto;top:24px;bottom:24px;width:1px;height:auto}
  .passos li{display:grid;grid-template-columns:48px minmax(0,1fr);gap:14px;align-items:center}.passos .num{margin:0}
  .amostra{grid-template-columns:96px minmax(0,1fr);gap:18px;align-items:start}
  .pro h2{margin-top:44px}
}
@media (max-width:420px){.amostra{grid-template-columns:minmax(0,1fr)}.folha{width:110px}.cartao{padding:18px 16px}}
"""


def rodape(gerado: str) -> str:
    """Rodapé das páginas Pro (D78): a data fixa é do retrato público do atlas; os estudos usam a base mensal mais recente."""
    return (f"Fonte: Comex Stat (MDIC), dados abertos. A data {e(gerado)} se refere ao retrato público do atlas gratuito; os estudos do "
            "rotzx Pro usam a base mensal mais recente publicada pelo MDIC no Comex Stat. Valores em US$ FOB correntes; dado ausente "
            "aparece como “sem registro”, nunca como zero.")


def corpo_pro() -> str:
    pedido = e(FORMULARIO or LINKEDIN)
    rot = "Enviar meu pedido" if FORMULARIO else "Fale comigo no LinkedIn"
    chips = "".join(f"<li>{e(c)}</li>" for c in RECORTES)
    planos = "".join(
        f'<article class="cartao plano{" destaque" if dest else ""}">{"<span class=etiqueta>Ponto de partida</span>" if dest else ""}'
        f'<h3>{e(nome)}</h3><span class="badge">{e(badge)}</span><ul>{"".join(f"<li>{e(i)}</li>" for i in itens)}</ul>'
        + ('<p class="obs">Diferente do <b>Incorporar</b> do atlas, que é grátis e mostra o atlas público como está, com a marca rotzx: '
           'a licença traz uma versão com a sua marca no lugar da do rotzx e recortes do seu setor ou estado. Os créditos das fontes '
           '(MDIC, ONU e as demais) continuam sempre visíveis.</p>' if nome == "Sob medida" else "")
        + "</article>" for nome, badge, dest, itens in PLANOS)
    passos = "".join(f'<li><span class="num">{i:02d}</span><span>{e(p)}</span></li>' for i, p in enumerate(PASSOS, 1))
    return f"""<section class="hero">
<div><div class="kicker">rotzx Pro</div>
<h1>Análise sob demanda do comércio exterior</h1>
<p class="lead">Do pequeno negócio e da pessoa física à empresa importadora: você traz a pergunta; o rotzx Pro responde com dados
públicos e oficiais, cruzados, conferidos e explicados.</p>
<a class="cta" href="{pedido}" rel="noopener">{rot} →</a>
<p class="miuda">Pedido individual? Empresa e cargo são opcionais no formulário. Você recebe por e-mail o escopo, o prazo e o valor
antes de qualquer compromisso.</p></div>
<aside class="cartao resumo" aria-label="O que o Pro abre além do atlas gratuito"><h3>O que o Pro abre além do atlas gratuito</h3>
<div class="linha"><span class="rot">Atlas</span><span class="base">Ano a ano, por país e produto (SH4), grátis.</span></div>
<div class="linha"><span class="rot pro-r">Pro</span><ul class="chips">{chips}</ul></div></aside>
</section>

<h2>Para quem</h2>
<div class="publico">
<div><b>Pessoas físicas, MEIs e pequenos negócios</b><span>Uma pergunta pontual sobre o seu produto ou mercado.</span></div>
<div><b>Profissionais autônomos</b><span>Pesquisadores, jornalistas e consultores independentes.</span></div>
<div><b>Produtores e cooperativas</b><span>Para onde vai a produção e de onde vêm os insumos.</span></div>
<div><b>Empresas e entidades</b><span>Importadoras, exportadoras, tradings, despachantes e entidades setoriais.</span></div>
</div>
<p>Perguntas pontuais cabem em escopos enxutos, pensados para quem não precisa de um estudo grande.</p>

<h2>Perguntas que ele responde</h2>
<ul class="perg">{''.join(f'<li>{e(q)}</li>' for q in PERGUNTAS)}</ul>

<h2>O que você pode contratar</h2>
<p class="sub">Sem tabela fixa: o valor depende do tamanho do pedido e vem junto com o escopo, antes de começar.</p>
<div class="planos">{planos}</div>

<h2>Como funciona</h2>
<ol class="passos">{passos}</ol>

<h2>Veja um exemplo</h2>
<div class="cartao amostra">
<div class="folha" aria-hidden="true"><b>PDF</b><i class="t"></i><i></i><i class="c"></i><span class="g"></span><i></i><i class="c"></i></div>
<div><div class="kicker">Estudo-amostra com dados reais</div>
<h3>De quem o Brasil compra fertilizantes, e o que mudou em 2026</h3>
<div class="meta">SH4 3101 a 3105 · importação · 2024 a out/2026 · {PAGINAS_AMOSTRA} páginas</div>
<ul><li>De onde vem</li><li>Preço × volume</li><li>Concentração dos fornecedores</li><li>Portos e estados</li><li>Mês a mês</li></ul>
<a class="cta sec" href="estudo-fertilizantes.pdf" target="_blank" rel="noopener">Abrir o estudo (PDF) ↗</a></div>
</div>

<div class="faixa"><p>Tem uma pergunta sobre comércio exterior?</p><a class="cta" href="{pedido}" rel="noopener">{rot} →</a></div>

<section class="cuidados"><h3>Dados e cuidados</h3>
<p>Comex Stat (MDIC), com detalhe por mês, produto (NCM), país, estado, porto e via, além do contexto do atlas: votos na ONU,
disputas na OMC, conflitos (UCDP/PRIO) e Banco Mundial. Dado ausente aparece como “sem registro”, nunca como zero, e toda
participação diz sobre qual total foi calculada.</p>
<p class="nota">Análise de dados públicos; não é recomendação de investimento ou de negócio. Como os dados do seu pedido são tratados:
<a href="privacidade/">política de privacidade</a>.</p></section>"""


PRIVACIDADE = f"""<p class="nota"><a href="../">← Voltar ao rotzx Pro</a></p>
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
<p class="nota">Base legal: consentimento, dado ao marcar a caixa no formulário (Lei 13.709/2018, LGPD).</p>"""


def gerar(out: Path, pagina: Callable[..., str], gerado: str) -> List[str]:
    """Escreve pro/index.html e pro/privacidade/index.html; devolve os caminhos para o sitemap."""
    (out / "pro" / "privacidade").mkdir(parents=True, exist_ok=True)
    (out / "pro" / "index.html").write_text(pagina(
        titulo="rotzx Pro: análise sob demanda do comércio exterior",
        desc="Estudos sob demanda sobre exportações e importações do Brasil, para pessoas, pequenos negócios e empresas: mercados, "
             "fornecedores, preço e volume, estados e portos, com dados públicos e oficiais.",
        caminho="pro/", raiz="../", corpo=corpo_pro(), contar="/pro", gerado=gerado,
        estilo_extra=ESTILO_PRO, rodape=rodape(gerado), classe="pro"), encoding="utf-8")
    (out / "pro" / "privacidade" / "index.html").write_text(pagina(
        titulo="rotzx Pro: política de privacidade", desc="Como o rotzx Pro trata os dados enviados no pedido de estudo.",
        caminho="pro/privacidade/", raiz="../../", corpo=PRIVACIDADE, contar="/pro/privacidade", gerado=gerado,
        rodape=rodape(gerado)), encoding="utf-8")
    return ["pro/", "pro/privacidade/"]
