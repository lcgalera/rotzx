/**
 * rotzx Pro — cria o formulário de briefing no Google Forms (D77, perguntas em docs/PRO.md).
 * Como usar: abrir https://script.google.com, "Novo projeto", colar este arquivo, salvar e rodar "criarBriefing".
 * Na primeira vez o Google pede autorização para criar formulários na sua conta. O link sai no "Registro de execução".
 * As respostas ficam na sua conta Google (aba "Respostas" do formulário), nunca no repositório.
 */
function criarBriefing() {
  var PRIVACIDADE = 'https://lcgalera.github.io/rotzx/pro/privacidade/';
  var f = FormApp.create('rotzx Pro: conte a sua pergunta');
  f.setDescription('Conte o que você quer entender. Eu respondo por e-mail com o escopo, o prazo e o valor antes de começar. ' +
                   'Análise de dados públicos; não é recomendação de investimento ou de negócio.');
  f.setCollectEmail(false);
  f.setLimitOneResponsePerUser(false);   // não exige login
  f.setAllowResponseEdits(false);
  f.setConfirmationMessage('Recebido. Respondo por e-mail em até 2 dias úteis.');

  f.addTextItem().setTitle('Nome').setRequired(true);
  f.addTextItem().setTitle('Empresa e cargo');
  f.addTextItem().setTitle('E-mail').setRequired(true)
    .setValidation(FormApp.createTextValidation().requireTextIsEmail().setHelpText('Informe um e-mail válido.').build());
  f.addParagraphTextItem().setTitle('Sua pergunta, com suas palavras').setRequired(true)
    .setHelpText('Ex.: de quem compramos o insumo que usamos, e quanto dependemos de cada fornecedor.');
  f.addParagraphTextItem().setTitle('Produtos (nome ou NCM)').setRequired(true);
  f.addTextItem().setTitle('Países ou regiões de interesse');
  f.addTextItem().setTitle('Estado (UF)');
  f.addTextItem().setTitle('Período').setHelpText('Ex.: desde 2015, últimos 12 meses.');
  f.addMultipleChoiceItem().setTitle('Você exporta, importa ou os dois?').setRequired(true)
    .setChoiceValues(['Exporto', 'Importo', 'Os dois', 'Nenhum, estou estudando o mercado']);
  f.addParagraphTextItem().setTitle('Para que vai usar a análise?');
  f.addMultipleChoiceItem().setTitle('Prazo').setChoiceValues(['Até 1 semana', 'Até 2 semanas', 'Sem pressa']);
  f.addTextItem().setTitle('Como conheceu o rotzx?');
  f.addCheckboxItem().setTitle('Privacidade').setRequired(true)
    .setHelpText('Política de privacidade: ' + PRIVACIDADE)
    .setChoiceValues(['Li a política de privacidade e concordo com o uso destes dados para responder ao meu pedido.']);

  Logger.log('Link para enviar ao Claude (público): ' + f.getPublishedUrl());
  Logger.log('Editar o formulário: ' + f.getEditUrl());
}
