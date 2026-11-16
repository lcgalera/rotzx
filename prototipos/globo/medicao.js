// rotzx — medição de acessos (D66). Sem cookies, sem identificador de pessoa e sem script de terceiros:
// cada tela ou ação manda um pedido simples ao GoatCounter, com o caminho, o título, a origem e o tamanho da tela.
// Desligada enquanto o código abaixo estiver vazio. Para ligar: crie o site em goatcounter.com e ponha aqui
// o código dele (o "meusite" de meusite.goatcounter.com).
window.ROTZX_MEDICAO = { goatcounter: "" };

(function () {
  var ultimo = "";
  function ligado() {
    var c = window.ROTZX_MEDICAO && window.ROTZX_MEDICAO.goatcounter;
    if (!c || !/^[a-z0-9-]+$/i.test(c)) return null;
    if (navigator.doNotTrack === "1" || navigator.globalPrivacyControl) return null;     // respeita quem pediu para não ser medido
    if (/^(localhost|127\.|0\.0\.0\.0|\[::1\])/.test(location.hostname) || location.protocol === "file:") return null;
    return c;
  }
  // caminho: "/pais/CHN", "/produto/1201"...; evento = true para ações (baixar CSV, exportar imagem, copiar link, incorporar)
  window.rotzxContar = function (caminho, titulo, evento) {
    try {
      var c = ligado(); if (!c || !caminho) return;
      if (!evento) { if (caminho === ultimo) return; ultimo = caminho; }
      var q = "p=" + encodeURIComponent(caminho) + "&t=" + encodeURIComponent(titulo || document.title) +
        (evento ? "&e=true" : "&r=" + encodeURIComponent(document.referrer || "")) +
        "&s=" + encodeURIComponent([screen.width, screen.height, window.devicePixelRatio || 1].join(",")) + "&rnd=" + Math.random().toString(36).slice(2, 8);
      var u = "https://" + c + ".goatcounter.com/count?" + q;
      if (!(navigator.sendBeacon && navigator.sendBeacon(u))) { new Image().src = u; }
    } catch (e) { /* medição nunca pode quebrar a página */ }
  };
  window.rotzxMedicaoLigada = function () { return !!ligado(); };
})();
