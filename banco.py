import sqlite3

DB = "cantina.db"

PRODUTOS_INICIAIS = [
    ("Croissant de Apresentado e queijo", "Salgados", 7.00),
    ("Risole de 4 queijos", "Salgados", 5.50),
    ("Risole de carne", "Salgados", 5.50),
    ("Croissant 3 queijos", "Salgados", 6.50),
    ("Hambúrguer com cheddar", "Salgados", 7.00),
    ("Enroladinho de bauru", "Salgados", 7.00),
    ("Pão de batata com calabresa", "Salgados", 6.50),
    ("Pão de batata de frango", "Salgados", 6.50),
    ("Esfiha de carne", "Salgados", 7.00),
    ("Coxinha", "Salgados", 5.50),
    ("Pão de queijo", "Salgados", 3.50),
    ("Caldo (mandioca, abóbora, verde, feijão)", "Salgados", 20.00),
    ("Espeto de carne/medalhão/coração (quarta)", "Salgados", 9.00),
    ("Guaraná 350ml", "Bebidas", 5.50),
    ("Fanta uva 350ml", "Bebidas", 5.50),
    ("Fanta Laranja 350ml", "Bebidas", 5.50),
    ("Coca cola zero açúcar 350ml", "Bebidas", 5.50),
    ("Coca cola 350ml", "Bebidas", 5.50),
    ("Suco tropical (uva, manga, abacaxi, açaí, goiaba) 480ml", "Bebidas", 8.00),
    ("Suco Kmais (goiaba, laranja, uva, maracujá) 300ml", "Bebidas", 7.50),
    ("Refrigerante caçula 200ml (coca cola, Pepsi, Fanta uva, coca cola zero)", "Bebidas", 3.50),
]

DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

def conectar():
    return sqlite3.connect(DB)

def criar_banco():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            ativo INTEGER NOT NULL DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cliente TEXT NOT NULL,
            total REAL NOT NULL,
            pagamento TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Recebido',
            data_hora TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            produto_id INTEGER,
            nome_produto TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS caixa_movimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            data_hora TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS almocos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dia TEXT UNIQUE NOT NULL,
            descricao TEXT NOT NULL,
            preco REAL NOT NULL DEFAULT 20.00,
            ativo INTEGER NOT NULL DEFAULT 1
        )
    """)

    cur.execute("SELECT COUNT(*) FROM produtos")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO produtos (nome, categoria, preco, ativo) VALUES (?, ?, ?, 1)",
            PRODUTOS_INICIAIS
        )

    cur.execute("SELECT COUNT(*) FROM almocos")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO almocos (dia, descricao, preco, ativo) VALUES (?, ?, ?, 1)",
            [(dia, "Não definido", 20.00) for dia in DIAS]
        )

    conn.commit()
    conn.close()

def itens_do_pedido(pedido_id):
    conn = conectar()
    dados = conn.execute("""
        SELECT nome_produto, quantidade, preco
        FROM itens_pedido
        WHERE pedido_id = ?
    """, (pedido_id,)).fetchall()
    conn.close()
    return dados
