// Esta etapa só apresenta avisos. Ainda não registra pedidos.
const aviso = document.querySelector("#aviso");
const titulo = document.querySelector("#aviso-titulo");
const texto = document.querySelector("#aviso-texto");

function mostrarAviso(novoTitulo, mensagem) {
    titulo.textContent = novoTitulo;
    texto.textContent = mensagem;
    aviso.showModal();
}

document.querySelectorAll("[data-produto]").forEach(function (botao) {
    botao.addEventListener("click", function () {
        mostrarAviso(botao.dataset.produto, "Este é o catálogo inicial. O formulário de pedido e a baixa de estoque serão implementados nas próximas etapas, com Flask e SQLite.");
    });
});

document.querySelector("#admin").addEventListener("click", function () {
    mostrarAviso("Administração", "Nas próximas etapas construiremos o cadastro dos três produtos, o controle de estoque e os relatórios com gráficos.");
});
