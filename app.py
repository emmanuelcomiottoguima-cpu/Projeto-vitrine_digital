"""LatMais: rotas HTTP, validação e persistência SQLite."""
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from decimal import Decimal, InvalidOperation
import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, root_path=str(Path(__file__).resolve().parent))
DB = Path(__file__).with_name("latmais.db")
TZ = ZoneInfo("America/Sao_Paulo")

def conectar():
    conn = sqlite3.connect(DB, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def inicializar():
    with conectar() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL, descricao TEXT NOT NULL,
            custo INTEGER NOT NULL CHECK(custo >= 0),
            preco INTEGER NOT NULL CHECK(preco > 0),
            estoque INTEGER NOT NULL CHECK(estoque >= 0), imagem TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL REFERENCES produtos(id),
            produto_nome TEXT NOT NULL, cliente TEXT NOT NULL, telefone TEXT NOT NULL,
            quantidade INTEGER NOT NULL CHECK(quantidade > 0),
            preco INTEGER NOT NULL, custo INTEGER NOT NULL, total INTEGER NOT NULL,
            data TEXT NOT NULL
        );
        """)

def inteiro(valor, minimo=0):
    if isinstance(valor, bool) or not str(valor).isdigit():
        raise ValueError("Informe uma quantidade inteira válida.")
    numero = int(valor)
    if numero < minimo: raise ValueError("Quantidade abaixo do permitido.")
    return numero

def centavos(valor):
    try:
        numero = Decimal(str(valor).replace(",", "."))
        if not numero.is_finite() or numero < 0 or numero > 1000000:
            raise ValueError("Valor monetário inválido.")
        if numero != numero.quantize(Decimal("0.01")):
            raise ValueError("Use no máximo duas casas decimais.")
        return int(numero * 100)
    except InvalidOperation:
        raise ValueError("Valor monetário inválido.")

@app.errorhandler(ValueError)
def erro_validacao(erro):
    return jsonify(erro=str(erro)), 400

@app.get("/")
def loja(): return render_template("loja.html")

@app.get("/admin")
def admin(): return render_template("admin.html")

@app.get("/api/produtos")
def produtos():
    with conectar() as conn:
        return jsonify([dict(x) for x in conn.execute("SELECT * FROM produtos ORDER BY id")])

@app.post("/api/produtos")
def salvar_produto():
    dados = request.get_json() or {}
    nome = str(dados.get("nome", "")).strip()
    descricao = str(dados.get("descricao", "")).strip()
    if not nome or len(nome)>100 or not descricao or len(descricao)>1000:
        raise ValueError("Preencha nome e descrição dentro dos limites.")
    custo, preco = centavos(dados.get("custo", "")), centavos(dados.get("preco", ""))
    if preco == 0: raise ValueError("O preço precisa ser maior que zero.")
    estoque = inteiro(dados.get("estoque", ""))
    imagem = dados.get("imagem")
    if imagem not in ["leite.svg", "queijo.svg", "manteiga.svg"]:
        raise ValueError("Escolha uma das imagens disponíveis.")
    valores = (nome, descricao, custo, preco, estoque, imagem)
    with conectar() as conn:
        conn.execute("BEGIN IMMEDIATE")
        if dados.get("id"):
            cursor = conn.execute("UPDATE produtos SET nome=?,descricao=?,custo=?,preco=?,estoque=?,imagem=? WHERE id=?", valores+(inteiro(dados["id"],1),))
            if cursor.rowcount != 1: raise ValueError("Produto não encontrado.")
        else:
            if conn.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] >= 3:
                raise ValueError("O limite é de três produtos.")
            conn.execute("INSERT INTO produtos(nome,descricao,custo,preco,estoque,imagem) VALUES(?,?,?,?,?,?)", valores)
    return jsonify(mensagem="Produto salvo.")

@app.post("/api/pedidos")
def pedido():
    dados = request.get_json() or {}
    produto_id = inteiro(dados.get("produto_id", ""),1)
    quantidade = inteiro(dados.get("quantidade", ""),1)
    cliente = str(dados.get("cliente", "")).strip()
    telefone = str(dados.get("telefone", "")).strip()
    if not cliente or len(cliente)>100 or not 8<=len(telefone)<=30:
        raise ValueError("Informe nome e telefone válidos.")
    with conectar() as conn:
        # O bloqueio protege contra duas compras simultâneas do mesmo estoque.
        conn.execute("BEGIN IMMEDIATE")
        produto = conn.execute("SELECT * FROM produtos WHERE id=?",(produto_id,)).fetchone()
        if not produto: raise ValueError("Produto não encontrado.")
        if quantidade > produto["estoque"]: raise ValueError("Estoque insuficiente.")
        total = produto["preco"] * quantidade
        conn.execute("UPDATE produtos SET estoque=estoque-? WHERE id=?",(quantidade,produto_id))
        cursor = conn.execute("INSERT INTO vendas(produto_id,produto_nome,cliente,telefone,quantidade,preco,custo,total,data) VALUES(?,?,?,?,?,?,?,?,?)",(produto_id,produto["nome"],cliente,telefone,quantidade,produto["preco"],produto["custo"],total,datetime.now(TZ).isoformat()))
        venda_id = cursor.lastrowid
    return jsonify(mensagem="Pedido registrado!", id=venda_id, total=total),201

@app.get("/api/relatorio")
def relatorio():
    dias = inteiro(request.args.get("dias", "7"),1)
    if dias not in [1,7,30]: raise ValueError("Período inválido.")
    hoje = datetime.now(TZ).date()
    inicio = hoje-timedelta(days=dias-1)
    fim = hoje+timedelta(days=1)
    with conectar() as conn:
        vendas = [dict(x) for x in conn.execute("SELECT * FROM vendas WHERE data>=? AND data<? ORDER BY data DESC,id DESC",(inicio.isoformat(),fim.isoformat()))]
        produtos = [dict(x) for x in conn.execute("SELECT * FROM produtos ORDER BY id")]
    serie = [{"data":(inicio+timedelta(days=i)).isoformat(), "quantidade":0} for i in range(dias)]
    por_dia = {x["data"]:x for x in serie}
    por_produto = {x["id"]:{"nome":x["nome"],"quantidade":0} for x in produtos}
    for venda in vendas:
        por_dia[venda["data"][:10]]["quantidade"] += venda["quantidade"]
        por_produto[venda["produto_id"]]["quantidade"] += venda["quantidade"]
    return jsonify(vendas=vendas, serie=serie, comparacao=list(por_produto.values()),
        faturamento=sum(v["total"] for v in vendas), unidades=sum(v["quantidade"] for v in vendas),
        pedidos=len(vendas), estoque=sum(p["estoque"] for p in produtos))

inicializar()
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
