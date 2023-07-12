from flask import Flask, request, render_template, render_template, request, redirect, url_for, make_response
import csv, psycopg2
app = Flask(__name__)
app.secret_key = "123456"

conn = psycopg2.connect(
    database="Estoque",
    user="postgres",
    password="12345"
)

def verifica_tabela():
    cur = conn.cursor()
    query = '''
    SELECT EXISTS (
    SELECT 1
    FROM information_schema.tables
    WHERE table_name = 'produto');  
    '''
    cur.execute(query)
    result = cur.fetchone()[0]
    return result


def tabelas():
    cur = conn.cursor()
    query = '''
    CREATE TABLE tipo(
	cod_tipo SERIAL PRIMARY KEY,
	nome_tipo VARCHAR(50)
    );

    CREATE TABLE fornecedor(
        cod_fornecedor SERIAL PRIMARY KEY,
        nome_fornecedor VARCHAR(50),
        cidade VARCHAR(100)
    );


    CREATE TABLE produto(
        cod_produto SERIAL PRIMARY KEY,
        nome_produto VARCHAR(50),
        cod_tipo INT,
        cod_fornecedor INT,
        FOREIGN KEY (cod_tipo) REFERENCES tipo(cod_tipo),
        FOREIGN KEY (cod_fornecedor) REFERENCES fornecedor(cod_fornecedor)
    );

    

    CREATE TABLE estoque(
        cod_estoque SERIAL PRIMARY KEY,
        cod_produto INT,
        quantidade INT,
        FOREIGN KEY (cod_produto) REFERENCES produto(cod_produto)
    )
    '''
    cur.execute(query)
    conn.commit()

def create(nome_produto, nome_tipo, nome_fornecedor, cidade_fornecedor, quantidade_estoque):
    create_produto(nome_produto, nome_tipo, nome_fornecedor,cidade_fornecedor)
    create_estoque(quantidade_estoque)
    return

def create_tipo(nome_tipo):
    cur = conn.cursor()
    query = f'''
    INSERT INTO tipo (nome_tipo) VALUES('{nome_tipo}') RETURNING cod_tipo;
    '''
    cur.execute(query)
    conn.commit()
    result = cur.fetchone()[0]
    return result

def create_fornecedor(nome_fornecedor, cidade_fornecedor):
    cur = conn.cursor()
    query = f'''
     INSERT INTO fornecedor (nome_fornecedor, cidade) VALUES('{nome_fornecedor}','{cidade_fornecedor}') RETURNING cod_fornecedor;
    '''
    cur.execute(query)
    conn.commit()
    result = cur.fetchone()[0]
    return result

def create_produto(nome_produto, nome_tipo, nome_fornecedor, cidade_fornecedor):
    cur = conn.cursor()
    nome_produto = nome_produto
    query = f"SELECT cod_tipo FROM tipo WHERE nome_tipo = '{nome_tipo}'"
    cur.execute(query)
    result = cur.fetchone()
    if result:
        cod_tipo = result[0]    
    else:
        cod_tipo = create_tipo(nome_tipo)
    query = f"SELECT cod_fornecedor FROM fornecedor WHERE nome_fornecedor = '{nome_fornecedor}'"
    cur.execute(query)
    result = cur.fetchone()
    if result:
        cod_fornecedor = result[0]
    else:
        cod_fornecedor = create_fornecedor(nome_fornecedor, cidade_fornecedor)
    query = f'''
     INSERT INTO produto (nome_produto, cod_fornecedor, cod_tipo) VALUES('{nome_produto}',{cod_fornecedor},{cod_tipo});
    '''
    cur.execute(query)
    conn.commit()

def create_estoque(quantidade):
    cur = conn.cursor()
    quantidade_estoque = quantidade
    query = '''
    SELECT COD_PRODUTO
    FROM PUBLIC.produto;
    '''
    cur.execute(query)
    cod_produto = cur.fetchall()
    query = f'''
      INSERT INTO estoque (cod_produto, quantidade) VALUES({cod_produto[-1][0]}, {quantidade_estoque})
    '''
    cur.execute(query)
    conn.commit()

def read():
    cur = conn.cursor()
    query= '''
    SELECT produto.cod_produto, nome_produto, nome_tipo, tipo.cod_tipo, nome_fornecedor, cidade, quantidade
    FROM produto
    JOIN tipo ON produto.cod_tipo = tipo.cod_tipo
    JOIN fornecedor ON produto.cod_fornecedor = fornecedor.cod_fornecedor
    JOIN estoque ON  produto.cod_produto = estoque.cod_produto
    ORDER BY cod_produto ASC;
    '''
    cur.execute(query)
    result = cur.fetchall()
    return result

def update(cod_produto, nova_quantidade):
    cur = conn.cursor()
    query = f'''
    UPDATE estoque SET quantidade = {nova_quantidade}
    WHERE cod_produto = {cod_produto}
    '''
    cur.execute(query)
    conn.commit()

def delete(cod_produto):
    cur = conn.cursor()
    query = f''' DELETE FROM estoque WHERE cod_produto= {cod_produto}; 
    DELETE FROM produto WHERE cod_produto = {cod_produto};'''
    cur.execute(query)
    conn.commit()

@app.route('/', methods=["POST","GET"])
def index():
    if verifica_tabela() == False:
        tabelas()
    data = read()
    verificar = request.form.get('verifica')
    if verificar == 'Adicionar':
        produto = request.form.get('produto')
        tipo = request.form.get('tipo')
        fornecedor = request.form.get('fornecedor')
        uf = request.form.get('uf')
        estoque = request.form.get('estoque')
        if int(estoque) < 0:
            estoque = 0
        create(str(produto).upper(), str(tipo).upper(), str(fornecedor).upper(), str(uf).upper(), estoque)
        verificar = ''
        return redirect('/')
    
    verificar = request.form.get('editar')
    if verificar:
        quantidade_estoque = request.form.get('nova_quantidade')
        if int(quantidade_estoque) >= 0:
            update(verificar, quantidade_estoque)
            verificar = ''
        else:
            pass
        return redirect('/')
    
    verificar = request.form.get('delete')
    if verificar:
        delete(verificar)
        verificar = ''
        return redirect('/')
    
    return render_template('index.html', data = data)


if __name__ == "__main__":
    app.run(debug=True)

