# rotzx Pro — plano do serviço

## Contexto
- **O que existe:** o rotzx é um atlas gratuito do comércio exterior brasileiro (v1.0.0, D74), publicado e divulgado no LinkedIn.
- **O que o dono quer:** uma camada paga, o **rotzx Pro**, para empresas e produtores.
- **Decisões dele:**
  - o público e o tema vêm da **demanda de cada cliente**: cada contratação é um estudo voltado à pergunta daquele comprador;
  - começo simples, com entrega por e-mail e cobrança por plataforma pronta;
  - ainda sem CNPJ/MEI.

O dado bruto é público e gratuito, então o Pro vende:
- **análise focada no que o cliente pediu**, que é a leitura econômica do Lucas sobre a pergunta dele;
- **tempo poupado**: dados cruzados, limpos e com denominador;
- **entrega pronta**: relatório, planilha e, se o cliente quiser, acompanhamento mensal do mesmo recorte.

O atlas grátis é a vitrine e prova a qualidade. O Pro é o serviço.

**Como escala sem virar consultoria artesanal:**
- cada estudo parte de um **kit automático** que monta a base de dados, as tabelas e os gráficos do recorte pedido; o trabalho manual é a análise;
- o mesmo recorte vira **acompanhamento mensal** quase sem trabalho extra (receita recorrente);
- temas que se repetem viram **estudos-modelo** reaproveitáveis.

---

## 1. Os serviços

| Serviço | O que o cliente recebe | Natureza |
|---|---|---|
| **Diagnóstico** | estudo sobre a pergunta do cliente (ex.: "para onde exportar meu café", "quanto dependo da China para este insumo", "como meu estado se compara no meu produto"): relatório de 8 a 15 páginas, planilha e conversa de apresentação opcional | avulso |
| **Acompanhamento** | o mesmo recorte do diagnóstico atualizado todo mês: o que mudou, preço × volume, mercados que entraram e saíram | assinatura |
| **Sob medida** | estudos maiores, vários produtos ou setores, apoio a apresentação ou pedido de financiamento; licença do atlas para portais e entidades, com a marca do cliente no lugar da do rotzx e recortes do setor ou estado (diferente do Incorporar grátis, que mostra o atlas público com a marca rotzx); créditos das fontes sempre visíveis | projeto |

Os preços saem das conversas da Fase 0, não de chute. O site mostra "a partir de" só depois de validados.

### O que o diagnóstico pode cobrir (cardápio para o briefing)
- **Mercados:** destinos e origens de cada produto, com a fatia (denominador dito); quem ganhou e quem perdeu espaço (em p.p.); mercados novos e perdidos; concentração.
- **Preço × volume:** valor, kg e US$/kg; subida por preço ou por quantidade; mês e acumulado do ano.
- **Estado (UF) e portos:** a posição do estado do cliente no total do Brasil; vias e portos usados.
- **Dependência:** fatia de cada fornecedor nas importações de um insumo; alternativas que já vendem para o Brasil.
- **Contexto dos países-chave:** o que o atlas tem (ONU, OMC, conflitos, economia), quando ajuda a responder a pergunta.
- **Conclusão do Lucas:** a leitura econômica sobre a pergunta. A interpretação aparece marcada como tal e separada dos fatos.

Regras do projeto que valem também no Pro:
- só dado real, com fonte e data;
- denominador sempre dito;
- "sem registro" nunca vira zero;
- nada de nota "bom/ruim" entre países;
- interpretação sempre marcada;
- aviso fixo: análise de dados públicos, não é recomendação de investimento ou de negócio.

---

## 2. Como funciona para o cliente
1. Conhece o rotzx (LinkedIn, atlas, Panorama do mês grátis) e clica em "rotzx Pro".
2. Preenche o **briefing**:
   - a pergunta, com as palavras dele;
   - produtos (busca por nome, que vira NCM/SH4), países, estado e período;
   - para que vai usar.
3. O Lucas responde com o **escopo e o preço** (conversa curta se precisar). O cliente paga pela plataforma: Pix, boleto ou cartão.
4. Recebe o diagnóstico no prazo combinado: relatório PDF, planilha e conversa opcional.
5. Recebe a oferta de **acompanhamento mensal** do mesmo recorte.

## 3. Como funciona por dentro
```
briefing → escopo (produtos, países, UF, período) → kit automático: coleta, tabelas, gráficos, rascunho do relatório
  → análise e conclusão do Lucas → revisão → entrega (link privado) → acompanhamento mensal reaproveita o mesmo escopo
```
**Metas de trabalho manual:**
- diagnóstico: só a análise e a revisão;
- acompanhamento: até 1 hora por cliente por mês, caindo conforme o kit amadurece.

---

## 4. Desenvolvimento por fases

### Fase 0 — Validar antes de construir (2 a 3 semanas)
- **Página "rotzx Pro"** no site público:
  - o que é e para quem;
  - exemplos de perguntas que o serviço responde;
  - **formulário de briefing** externo (Tally ou Google Forms; o site continua sem backend).
- **Estudo-amostra** em PDF com dados reais, sobre uma pergunta exemplo declarada como exemplo. Ex.: "De quem o Brasil compra fertilizantes e como isso mudou".
- **Primeiros diagnósticos feitos à mão** com o que já existe, a preço de lançamento: mostram o que os clientes perguntam de verdade.
- **10 conversas** com quem mandar briefing ou comentar no LinkedIn, para descobrir:
  - quanto pagariam;
  - que formato preferem;
  - se querem acompanhamento mensal.
- **Formalização (pelo dono, com contador):**
  - ver se a atividade (análise de dados, consultoria) cabe no MEI ou pede outra forma;
  - abrir CNPJ;
  - conta PJ.
- **Critério para seguir:** 3 a 5 diagnósticos pagos e pelo menos 2 clientes interessados em acompanhamento.

### Fase 1 — O kit de análise (4 a 6 semanas depois da Fase 0)
Código em **repositório privado** `rotzx-pro` (briefings e dados de clientes nunca no repositório público).

**Dados mensais e detalhados.** `coleta.py`, reaproveitando `rotzx/mundo/comex.py`:
- `_filtro` já tem `monthDetail` e `metricKG`; `_get` já faz espera, novas tentativas e guarda a resposta bruta;
- **níveis:** NCM 8 × país × mês e SH4 × UF × mês; vias e portos;
- **ponte país → ISO:** `rotzx/mundo/detalhe_coleta.py::_ponte` e `catalog/paises_mundo.csv`;
- **cache:** em `data/`, no padrão de `detalhe_coleta.pares_do_ano`, para que recortes que se repetem entre clientes não consultem de novo;
- **primeira tarefa (spike):** confirmar na API os campos de UF, via e URF e o formato dos meses.

**Escopo.** `escopo.py`: transforma o briefing num arquivo de recorte (produtos, países, UF, período, comparações pedidas), que é a entrada única do kit.

**Indicadores.** `indicadores.py`, funções puras e testadas:
- valor, kg, US$/kg;
- variação anual e acumulado do ano;
- participação com denominador e p.p.;
- mercados novos e perdidos;
- dependência (fatia do maior fornecedor e dos 3 maiores);
- "preço × volume".

**Relatório.**
- `relatorio.py`: HTML na identidade do atlas → **PDF pelo Chromium/Playwright** (`page.pdf`), já usado nos testes.
- Blocos de análise como "módulos" que o escopo liga ou desliga.
- Espaço marcado para o texto do Lucas (resumo, conclusão).
- Gráficos em SVG gerado em Python; formatos `usd`/`pct` de `rotzx/mundo/paginas.py`.
- Planilha em CSV com BOM (como o "Baixar CSV" do atlas) ou XLSX.

**Acompanhamento.** `acompanhar.py` roda todo mês os escopos ativos depois que o Comex Stat publica o mês e gera o rascunho de cada cliente para revisão.

**Entrega.** Link privado com validade (armazenamento tipo Cloudflare R2 ou Google Drive), enviado por e-mail. Nos primeiros meses, o Lucas aprova cada envio.

**Cobrança.**
- Hotmart, Kiwify ou similar: produto avulso (diagnóstico) e assinatura (acompanhamento), com Pix e boleto.
- Lista de clientes ativos mantida à mão no começo.

**Site público:**
- sai do GitHub Pages, cujos termos não cobrem uso comercial;
- vai para **domínio próprio + Cloudflare Pages ou Netlify** (grátis);
- a medição troca o GoatCounter grátis (só uso não comercial) pelo Cloudflare Web Analytics ou pelo GoatCounter pago.

**Panorama do mês.** Público e grátis, sai do mesmo kit com o recorte "Brasil inteiro". Vai para o site e para o LinkedIn, e alimenta a procura pelo Pro.

**Testes:**
- fixtures marcadas como inventadas, como nos testes atuais;
- âncora de qualidade: a soma dos 12 meses de um ano tem de bater com o total anual que o atlas já publica.

**Critério para seguir:**
- um diagnóstico novo sai do kit com só a análise manual;
- 5 ou mais acompanhamentos ativos por 2 meses seguidos.

### Fase 2 — Escala (depois de ~20 clientes ativos)
- **Área do cliente:**
  - login e banco (Supabase, ou Cloudflare Workers + D1);
  - estudos e edições num só lugar;
  - painel do recorte reaproveitando os componentes do atlas (gráficos, tabelas, CSV, PNG).
- **Briefing e pagamento integrados:** o webhook da plataforma de pagamento libera o acesso.
- **Alertas:** e-mail quando sai o dado e algo passa de um limite combinado no escopo (ex.: queda forte num mercado, novo fornecedor).
- **Estudos-modelo:** os temas mais pedidos viram produtos de catálogo com preço fixo e entrega mais rápida.

### Fase 3 — Expansão
- Exportação em lote e **API** para consultorias e sistemas internos.
- **Licença de incorporação** do atlas (sem o selo, com a marca do cliente, atualização garantida).
- **Parcerias:** despachantes, consultorias e associações revendem diagnósticos aos clientes deles.
- **Atlas público:** atualização mensal (de anual para mensal), que dá mais motivo para voltar ao site.

---

## 5. Operação
- **Diagnóstico:**
  1. briefing;
  2. escopo e preço;
  3. pagamento;
  4. kit;
  5. análise;
  6. revisão (checklist: fonte e data em cada número, denominadores, "sem registro", interpretação marcada, aviso);
  7. entrega;
  8. oferta de acompanhamento.
- **Mês (acompanhamentos):**
  1. conferir quando o Comex Stat publica o mês (calendário oficial é tarefa da Fase 1);
  2. rodar `acompanhar.py`;
  3. conferir `falhas` e a âncora "12 meses = ano";
  4. revisar e enviar;
  5. publicar o Panorama do mês e o post do LinkedIn.

## 6. Jurídico e regras
- **Formalização:** CNPJ e enquadramento com contador antes do primeiro pagamento.
- **Contrato simples por estudo:** escopo, prazo, preço, uso permitido do relatório.
- **Termos de uso e política de privacidade (LGPD):**
  - que dados coleta (e-mail, briefing, recorte);
  - para quê;
  - por quanto tempo guarda;
  - como pedir exclusão.
- **Licenças das fontes:** Comex Stat (dados abertos); UCDP e Banco Mundial em CC BY 4.0, com crédito. Revisar os termos de cada fonte para uso comercial antes de cobrar (sem revisão jurídica feita até aqui).
- **Dados de clientes:** só no repositório privado. O repositório público continua guardado por `tests/test_repo_publico.py`.

## 7. Entrada no mercado
- **Conteúdo:** LinkedIn com um dado do mês (o Panorama vira série de posts), o vídeo do atlas e trechos dos estudos-amostra.
- **Primeiros clientes:** 5 diagnósticos de lançamento com desconto em troca de depoimento e feedback.
- **Canais:**
  - associações e federações setoriais;
  - grupos de comércio exterior;
  - cooperativas;
  - despachantes e consultorias (possíveis parceiros revendedores).

## 8. Métricas
- **Funil:** briefings recebidos, briefings que viram diagnóstico pago, diagnósticos que viram acompanhamento.
- **Retenção:** cancelamentos de acompanhamento por mês.
- **Custo de produção:** horas por diagnóstico e por acompanhamento (meta caindo mês a mês).
- **Atlas:** visitas, cliques em "rotzx Pro" e CSV baixados (GoatCounter).

## 9. Riscos
- **Virar consultoria artesanal:** cada estudo diferente consome muito tempo. Resposta: kit automático, cardápio de módulos e estudos-modelo.
- **Constância do acompanhamento:** atrasar uma edição causa cancelamento. Por isso o ciclo é automatizado antes de vender acompanhamento em volume.
- **Dado gratuito:** sem análise focada, o estudo perde para o próprio Comex Stat. A conclusão do Lucas sobre a pergunta do cliente é o diferencial.
- **Revisões do Comex:** os dados mensais podem ser revistos. O relatório diz a data da coleta e marca a revisão quando houver.

## 10. Quem faz o quê
| Lucas | Claude |
|---|---|
| conversas, escopo e preço, formalização e contador, plataforma de pagamento | página Pro e formulário de briefing, estudo-amostra |
| análise, conclusão e revisão final de cada estudo | coleta mensal e detalhada, escopo, indicadores, gerador de PDF e planilha, testes |
| LinkedIn e relacionamento | Panorama do mês, migração para domínio próprio, workflows |

## 11. Verificação (Fase 1)
- **Testes:** `pytest` com fixtures marcadas como inventadas para coleta, escopo, indicadores e relatório.
- **Âncora:** a soma dos 12 meses de 2025 por produto e país bate com os totais anuais já publicados no atlas.
- **PDF:** gerado em Chromium sem tela; conferir paginação, gráficos e textos em escopos curtos e longos.
- **Ensaio geral:** um diagnóstico e um mês de acompanhamento completos com escopos de teste, enviados só para o dono, antes de cobrar.
- **Registro:** cada passo gera uma decisão em `docs/DECISOES.md` (D76 em diante).

## Briefing (Google Forms)
O dono cria o formulário na conta Google dele rodando [`briefing_forms.gs`](briefing_forms.gs) no Apps Script (script.google.com); a planilha de respostas fica lá, nunca no repositório. Até o link existir, o botão da página `/pro/` aponta para o LinkedIn (`FORMULARIO` em `rotzx/pro/pagina.py`).

**Título:** "rotzx Pro: conte a sua pergunta". **Descrição:** "Conte o que você quer entender. Eu respondo por e-mail com o escopo, o prazo e o valor antes de começar. Análise de dados públicos; não é recomendação de investimento ou de negócio."

| # | Pergunta | Tipo | Obrigatória |
|---|---|---|---|
| 1 | Nome | resposta curta | sim |
| 2 | Empresa e cargo | resposta curta | não |
| 3 | E-mail | resposta curta (validação de e-mail) | sim |
| 4 | Sua pergunta, com suas palavras | parágrafo | sim |
| 5 | Produtos (nome ou NCM) | parágrafo | sim |
| 6 | Países ou regiões de interesse | resposta curta | não |
| 7 | Estado (UF) | resposta curta | não |
| 8 | Período (ex.: desde 2015, últimos 12 meses) | resposta curta | não |
| 9 | Você exporta, importa ou os dois? | múltipla escolha: exporto / importo / os dois / nenhum, estou estudando o mercado | sim |
| 10 | Para que vai usar a análise? | parágrafo | não |
| 11 | Prazo | múltipla escolha: até 1 semana / até 2 semanas / sem pressa | não |
| 12 | Como conheceu o rotzx? | resposta curta | não |
| 13 | "Li a política de privacidade (link para /pro/privacidade/) e concordo com o uso destes dados para responder ao meu pedido." | caixa de seleção | sim |

Configurações: não coletar e-mail automaticamente (a pergunta 3 já pede), não exigir login, mostrar mensagem de confirmação "Recebido. Respondo por e-mail em até 2 dias úteis."

## Situação da Fase 0 (D77, D78)
- Página `/pro/` e política de privacidade `/pro/privacidade/`: prontas, geradas no build por `rotzx/pro/pagina.py`.
- Estudo-amostra de fertilizantes: `prototipos/globo/pro/estudo-fertilizantes.pdf`, gerado por `rotzx pro-amostra`. O bloco "Leitura do analista" é rascunho e precisa da revisão do dono.
- Formulário criado pelo dono (24/11/2026); o botão "Enviar meu pedido" aponta para o link público. O link de edição fica só com o dono.
- Publicada em 24/11/2026 (D77). Página refeita em D78: tema contínuo com o atlas, hero com o que o Pro abre além do atlas, planos em cards, passos numerados, card do estudo-amostra e público ampliado (pessoas físicas, MEIs, autônomos).

## Estudo-amostra v2 (D80)
O estudo de fertilizantes passou de descritivo a decisório. São 12 páginas:
- capa com 3 números;
- resumo, leitura e 3 sinais para o próximo mês;
- volume × preço × mix;
- preço por produto e origem;
- referência do Banco Mundial;
- dependência por produto (HHI);
- calendário de compra;
- portos, estados e frete;
- contexto de fornecimento com fonte;
- leitura por perfil;
- o que o diagnóstico inclui;
- fontes e método.

Junto do PDF vai a planilha com as tabelas de cada seção (`estudo-fertilizantes.xlsx`). Esse é o formato de referência para os diagnósticos.

## Escopo, amostras e "Quem faz" (D81)
- **Escopo do Diagnóstico:** sem preço na página por enquanto. Parte de tudo o que está nas amostras e vai além: seções, produtos, países e estados escolhidos a partir do pedido da empresa ou da pessoa. Escopo, prazo e valor seguem por e-mail antes de qualquer compromisso.
- **Amostras:** fertilizantes (importação, 12 páginas) e café (exportação, 11 páginas, para cooperativas e produtores), no mesmo motor (`rotzx/pro/estudo.py`). Um estudo novo é um arquivo em `rotzx/pro/amostras/`.
- **"Quem faz":** rascunho em `QUEM_FAZ` (`rotzx/pro/pagina.py`), com lacunas entre colchetes para o dono completar: nome, uma linha de apresentação, formação, experiência e o motivo de ter criado o rotzx. Enquanto houver lacuna, o bloco não aparece na página (teste garante).

## Primeiro passo depois da aprovação
**Fase 0:** a página "rotzx Pro" com o formulário de briefing e o estudo-amostra em PDF. Antes, o spike da API mensal (meses, kg, UF), que define o que os estudos conseguem mostrar. A formalização com contador corre em paralelo, com o dono.
