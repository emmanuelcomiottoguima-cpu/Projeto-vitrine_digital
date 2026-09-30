// Os valores monetários vindos do servidor estão em centavos.
const moeda = valor => (valor / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const el = id => document.getElementById(id);
let produtos = [];
let selecionado;
function texto(tag, valor, classe) {
    const node = document.createElement(tag);
    node.textContent = valor;
    if (classe) node.className = classe;
    return node;
}
async function api(url, dados) {
    const resposta = await fetch(url, dados ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(dados) } : {});
    const resultado = await resposta.json();
    if (!resposta.ok) throw new Error(resultado.erro || "Não foi possível concluir.");
    return resultado;
}
async function carregarProdutos() {
    produtos = await api("/api/produtos");
    const lista = el("catalogo") || el("lista-admin");
    lista.replaceChildren();
    if (!produtos.length) lista.append(texto("p", "Nenhum produto cadastrado. Cadastre os três produtos na Administração."));
    produtos.forEach(produto => {
        const card = document.createElement("article"); card.className = "produto";
        const img = document.createElement("img"); img.src = "/static/imagens/" + produto.imagem; img.alt = produto.nome;
        const conteudo = document.createElement("div"); conteudo.className = "conteudo";
        conteudo.append(texto("h3", produto.nome), texto("p", produto.descricao), texto("strong", moeda(produto.preco)), texto("p", "Estoque: " + produto.estoque));
        const botao = texto("button", el("catalogo") ? (produto.estoque ? "Comprar" : "Sem estoque") : "Editar");
        botao.type = "button";
        if (el("catalogo")) {
            botao.disabled = !produto.estoque;
            botao.onclick = () => abrirPedido(produto);
        } else {
            conteudo.append(texto("p", "Código: " + produto.id + " · Custo: " + moeda(produto.custo)));
            botao.onclick = () => {
                const form = el("form-produto");
                for (const campo of ["id", "nome", "descricao", "estoque", "imagem"]) form.elements[campo].value = produto[campo];
                form.elements.custo.value = (produto.custo / 100).toFixed(2);
                form.elements.preco.value = (produto.preco / 100).toFixed(2);
                form.scrollIntoView({ behavior: "smooth" });
            };
        }
        conteudo.append(botao); card.append(img, conteudo); lista.append(card);
    });
}
function abrirPedido(produto) {
    selecionado = produto;
    const form = el("form-pedido"); form.reset();
    form.elements.produto_id.value = produto.id;
    form.elements.quantidade.max = produto.estoque;
    el("produto-escolhido").textContent = produto.nome;
    el("erro-pedido").textContent = "";
    atualizarTotal(); el("pedido").showModal();
}
function atualizarTotal() { el("total").textContent = "Total: " + moeda(selecionado.preco * Number(el("form-pedido").elements.quantidade.value)); }
// Gráficos de barras em HTML/CSS: funcionam sem CDN ou internet.
function grafico(id, dados) {
    const raiz = el(id); raiz.replaceChildren();
    const max = Math.max(1, ...dados.map(d => d.quantidade));
    dados.forEach(d => {
        const linha = document.createElement("div"); linha.className = "linha-grafico";
        const trilho = document.createElement("div"); trilho.className = "trilho";
        const barra = document.createElement("div"); barra.className = "barra"; barra.style.width = (d.quantidade / max * 100) + "%";
        trilho.append(barra); linha.append(texto("span", d.nome), trilho, texto("strong", d.quantidade)); raiz.append(linha);
    });
}
async function relatorio() {
    const dados = await api("/api/relatorio?dias=" + el("periodo").value);
    el("indicadores").replaceChildren();
    [["Faturamento", moeda(dados.faturamento)], ["Unidades vendidas", dados.unidades], ["Pedidos", dados.pedidos], ["Estoque atual", dados.estoque]].forEach(([nome, valor]) => {
        const card = document.createElement("article"); card.className = "caixa";
        card.append(texto("h3", valor), texto("p", nome)); el("indicadores").append(card);
    });
    grafico("serie", dados.serie.map(d => ({ ...d, nome: d.data.slice(8) + "/" + d.data.slice(5, 7) })));
    grafico("comparacao", dados.comparacao);
    el("historico").replaceChildren();
    dados.vendas.forEach(v => {
        const tr = document.createElement("tr");
        [v.id, new Date(v.data).toLocaleString("pt-BR", { timeZone: "America/Sao_Paulo" }), v.cliente, v.produto_nome, v.quantidade, moeda(v.total)].forEach(valor => tr.append(texto("td", valor)));
        el("historico").append(tr);
    });
    if (!dados.vendas.length) { const tr = document.createElement("tr"); const td = texto("td", "Nenhuma venda neste período."); td.colSpan = 6; tr.append(td); el("historico").append(tr); }
}
async function iniciar() {
    await carregarProdutos();
    if (el("form-pedido")) {
        el("fechar").onclick = () => el("pedido").close();
        el("form-pedido").elements.quantidade.oninput = atualizarTotal;
        el("form-pedido").onsubmit = async event => {
            event.preventDefault(); const form = event.currentTarget; const botao = form.querySelector('button'); botao.disabled = true;
            try { const resultado = await api("/api/pedidos", Object.fromEntries(new FormData(form))); el("pedido").close(); el("mensagem").textContent = "Pedido #" + resultado.id + " registrado. Total: " + moeda(resultado.total); await carregarProdutos(); }
            catch (erro) { el("erro-pedido").textContent = erro.message; } finally { botao.disabled = false; }
        };
    } else {
        await relatorio();
        el("periodo").onchange = () => relatorio().catch(erro => el("mensagem").textContent = erro.message);
        el("novo").onclick = () => { el("form-produto").reset(); el("form-produto").elements.id.value = ""; };
        el("form-produto").onsubmit = async event => {
            event.preventDefault(); const form = event.currentTarget; const botao = form.querySelector('button'); botao.disabled = true;
            try { await api("/api/produtos", Object.fromEntries(new FormData(form))); form.reset(); form.elements.id.value = ""; el("erro-produto").textContent = "Produto salvo."; await carregarProdutos(); await relatorio(); }
            catch (erro) { el("erro-produto").textContent = erro.message; } finally { botao.disabled = false; }
        };
    }
}
iniciar().catch(erro => el("mensagem").textContent = erro.message);
