"""Páginas públicas do rotzx Pro no site (D77): /pro/ e /pro/privacidade/.

Geradas no build, com o mesmo molde das páginas estáticas (rotzx/mundo/paginas.py). Sem preço (sai das conversas da Fase 0) e
sem slogan. O botão de pedido aponta para o formulário de briefing (Google Forms do dono) quando FORMULARIO estiver preenchido;
até lá, para o LinkedIn.
"""
import html
from pathlib import Path
from typing import Callable, List

FORMULARIO = "https://docs.google.com/forms/d/e/1FAIpQLScjz5rhGd8X_tY7Xmy04O2P9NqgBCd5dU8L-s_cuMtGcxPPMg/viewform"  # link do Google Forms do briefing (preenchido pelo dono)
LINKEDIN = "https://www.linkedin.com/in/lucasfgalera"
e = html.escape

PERGUNTAS = [
    "Para quais países vale a pena exportar meu produto, e quem já compra do Brasil?",
    "De quem o Brasil compra o insumo que eu uso, e quanto depende de cada fornecedor?",
    "O preço do meu produto subiu porque vendemos mais caro ou porque vendemos mais?",
    "Como o meu estado se compara com o resto do Brasil no meu produto?",
    "Por quais portos sai ou entra a minha mercadoria, e como isso mudou?",
]


def gerar(out: Path, pagina: Callable[..., str], gerado: str) -> List[str]:
    """Escreve pro/index.html e pro/privacidade/index.html; devolve os caminhos para o sitemap."""
    pedido = FORMULARIO or LINKEDIN
    rot_pedido = "Enviar meu pedido" if FORMULARIO else "Fale comigo no LinkedIn"
    corpo = f"""<div class="kicker">rotzx Pro</div>
<h1>Análise sob demanda do seu comércio exterior</h1>
<p class="lead">Você traz a pergunta do seu negócio; o rotzx Pro responde com dados públicos e oficiais, cruzados, conferidos e explicados,
com uma análise focada no que você pediu.</p>
<a class="cta" href="{e(pedido)}" rel="noopener">{rot_pedido} →</a>

<h2>Para quem</h2>
<p>Empresas que exportam ou importam, produtores e cooperativas, tradings, consultorias, despachantes e entidades setoriais que precisam
entender um mercado sem montar a análise do zero.</p>

<h2>Perguntas que ele responde</h2>
<ul>{''.join(f'<li>{e(q)}</li>' for q in PERGUNTAS)}</ul>

<h2>O que você pode contratar</h2>
<div class="rolavel"><table><thead><tr><th>Serviço</th><th>O que você recebe</th></tr></thead><tbody>
<tr><td>Diagnóstico</td><td>Um estudo sobre a sua pergunta: relatório em PDF, planilha com os números e, se quiser, uma conversa para apresentar o resultado.</td></tr>
<tr><td>Acompanhamento</td><td>O mesmo recorte atualizado todo mês: o que mudou, preço e volume, mercados que entraram e saíram.</td></tr>
<tr><td>Sob medida</td><td>Estudos maiores, com vários produtos ou setores, e licença para usar o atlas no seu site.</td></tr>
</tbody></table></div>
<p class="nota">O valor depende do tamanho de cada pedido e é combinado antes de começar.</p>

<h2>Como funciona</h2>
<ol><li>Você conta a sua pergunta, os produtos, os países e o estado que interessam.</li>
<li>Eu respondo com o escopo, o prazo e o valor.</li>
<li>Você recebe o estudo: cada número com a fonte e a data, e a análise separada dos fatos.</li>
<li>Se quiser, o mesmo recorte passa a chegar todo mês.</li></ol>

<h2>Veja um exemplo</h2>
<p>Estudo-amostra com dados reais: <a href="estudo-fertilizantes.pdf">De quem o Brasil compra fertilizantes, e o que mudou em 2026 (PDF)</a>.</p>
<a class="cta" href="{e(pedido)}" rel="noopener">{rot_pedido} →</a>

<h2>Dados e cuidados</h2>
<p>Comex Stat (MDIC), com detalhe por mês, produto (NCM), país, estado, porto e via, além do contexto do atlas: votos na ONU,
disputas na OMC, conflitos (UCDP/PRIO) e Banco Mundial. Dado ausente aparece como “sem registro”, nunca como zero, e toda
participação diz sobre qual total foi calculada.</p>
<p class="nota">Análise de dados públicos; não é recomendação de investimento ou de negócio. Como os dados do seu pedido são tratados:
<a href="privacidade/">política de privacidade</a>.</p>"""
    (out / "pro").mkdir(parents=True, exist_ok=True)
    (out / "pro" / "index.html").write_text(pagina(
        titulo="rotzx Pro: análise sob demanda do comércio exterior",
        desc="Estudos sob demanda sobre exportações e importações do Brasil: mercados, fornecedores, preço e volume, estados e portos, com dados públicos e oficiais.",
        caminho="pro/", raiz="../", corpo=corpo, contar="/pro", gerado=gerado), encoding="utf-8")

    priv = f"""<div class="kicker">rotzx Pro</div><h1>Política de privacidade</h1>
<p class="lead">Como são tratados os dados que você envia ao pedir um estudo.</p>
<h2>O que é coletado</h2>
<p>Só o que você escreve no formulário de pedido: nome, empresa, cargo, e-mail e as informações do pedido (pergunta, produtos, países,
estado, período, uso e prazo).</p>
<h2>Para quê</h2>
<p>Para responder ao seu pedido, combinar o escopo e, se você contratar, preparar e entregar o estudo. Os dados não são vendidos nem
usados para outra finalidade.</p>
<h2>Onde ficam e por quanto tempo</h2>
<p>As respostas ficam numa planilha privada do responsável pelo rotzx (o formulário é do Google, que atua como operador). São guardadas
por até 12 meses depois do último contato, ou menos, se você pedir a exclusão.</p>
<h2>Seus direitos</h2>
<p>Você pode pedir acesso, correção ou exclusão dos seus dados a qualquer momento, pelo <a href="{LINKEDIN}" rel="noopener">LinkedIn do responsável</a>.</p>
<h2>Navegação no site</h2>
<p>O site conta visitas de forma agregada (GoatCounter), sem cookies e sem identificar pessoas, e respeita o pedido “não rastrear” do navegador.</p>
<p class="nota">Base legal: consentimento, dado ao marcar a caixa no formulário (Lei 13.709/2018, LGPD).</p>"""
    (out / "pro" / "privacidade").mkdir(parents=True, exist_ok=True)
    (out / "pro" / "privacidade" / "index.html").write_text(pagina(
        titulo="rotzx Pro: política de privacidade", desc="Como o rotzx Pro trata os dados enviados no pedido de estudo.",
        caminho="pro/privacidade/", raiz="../../", corpo=priv, contar="/pro/privacidade", gerado=gerado), encoding="utf-8")
    return ["pro/", "pro/privacidade/"]
