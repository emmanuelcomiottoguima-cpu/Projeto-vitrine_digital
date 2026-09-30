# LatMais — sistema escolar completo

## Executar no Windows / VS Code
1. Extraia o ZIP e abra a pasta latmais-completo no VS Code.
2. Abra Terminal → Novo terminal.
3. Execute `py -m venv .venv`.
4. Execute `.venv\Scripts\python.exe -m pip install -r requirements.txt`.
5. Execute `.venv\Scripts\python.exe app.py`.
6. Abra http://127.0.0.1:5000 no navegador. Não abra HTML com dois cliques.
7. Administração: http://127.0.0.1:5000/admin .
8. Para parar: Ctrl+C. Para voltar: repita o comando do passo 5.

## Primeira utilização
O banco começa vazio para você testar o cadastro de verdade. Cadastre:
- Leite Integral Artesanal: custo 4,50; preço 7,90; estoque 30; imagem leite.
- Queijo Colonial: custo 20,00; preço 34,90; estoque 15; imagem queijo.
- Manteiga Artesanal: custo 9,00; preço 16,90; estoque 20; imagem manteiga.
As descrições podem ser escritas pelo grupo. São preços ilustrativos.
Depois volte à loja e faça um pedido. O estoque e os relatórios são atualizados.
O banco latmais.db é criado automaticamente ao iniciar, ao lado de app.py.

## Como entender o projeto
- templates/: HTML. Flask entrega as páginas e Jinja reutiliza base.html.
- static/css/: CSS. Layout, responsividade e barras dos gráficos.
- static/app.js: fetch envia e recebe JSON; eventos respondem a formulários.
- app.py: valida os pedidos, consulta o banco e define as rotas.
- SQLite: duas tabelas, produtos e vendas; vendas guarda preço e custo históricos.
- Dinheiro é armazenado em centavos inteiros, evitando erro de arredondamento.
- BEGIN IMMEDIATE e a transação mantêm venda e estoque consistentes.

## Gráficos e escopo
Os gráficos são barras HTML/CSS, sem Chart.js, para funcionar offline após instalar as dependências. Hoje / 7 / 30 dias incluindo hoje, horário de Brasília.
O estoque mostrado é atual; faturamento e vendas respeitam o período.
Imagens são selecionadas entre três SVG locais; upload de fotos não foi incluído.
Não há pagamento online, autenticação, exclusão de produtos ou atualização ao vivo entre abas. Atualize a página para consultar alterações externas.
O painel não tem login: utilize esta versão para demonstração local.

## Git — histórico verdadeiro
Execute `git init`, depois `git add .` e `git commit -m "adiciona versão funcional da LatMais"`.
Não invente commits anteriores. Faça os próximos commits conforme estudar e alterar o projeto. O banco não entra no Git.

## Verificação manual
1. Cadastre os 3 produtos e tente um quarto (deve ser bloqueado).
2. Compre 2 queijos: estoque 15 → 13, total R$ 69,80.
3. Tente comprar acima do estoque (deve ser bloqueado).
4. Edite o preço: vendas antigas devem manter o preço original.
5. Compare histórico, indicadores e gráficos nos três períodos.
6. Feche e abra o programa: dados devem continuar salvos.

## Próximas atividades do grupo
Estudar os arquivos por partes, personalizar textos, testar no computador da apresentação, registrar commits reais, preparar pitch e evidências do funcionamento.
