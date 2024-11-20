import mysql.connector

def conectar():
    """Lembre de atualizar de acordo com seu MySQL"""
    return mysql.connector.connect(
        host="localhost",
        user="root",  
        password="10688159818",  
        database="Voltz"
    )

# Inserir um novo cliente
def inserir_cliente(nome, email, telefone, login, senha, saldo):
    """Cadastra um novo cliente no banco de dados."""
    conexao = conectar()
    cursor = conexao.cursor()
    query = """
        INSERT INTO clientes (nome, email, telefone, login, senha, saldo, data_cadastro)
        VALUES (%s, %s, %s, %s, %s, %s, CURDATE())
    """
    valores = (nome, email, telefone, login, senha, saldo)
    cursor.execute(query, valores)
    conexao.commit()
    print(f"Cliente inserido com ID: {cursor.lastrowid}")
    cursor.close()
    conexao.close()

# Buscar cliente por login e senha
def buscar_cliente_por_login(login, senha):
    """Busca um cliente no banco utilizando login e senha."""
    conexao = conectar()
    cursor = conexao.cursor()
    query = "SELECT * FROM clientes WHERE login = %s AND senha = %s"
    cursor.execute(query, (login, senha))
    resultado = cursor.fetchone()
    cursor.close()
    conexao.close()
    return resultado

def buscar_cliente_por_login(login, senha):
    conexao = conectar()
    cursor = conexao.cursor()
    query = "SELECT * FROM clientes WHERE login = %s AND senha = %s"
    cursor.execute(query, (login, senha))
    resultado = cursor.fetchone()
    cursor.close()
    conexao.close()
    return resultado

def buscar_saldo_por_cliente(id_cliente):
    conexao = conectar()
    cursor = conexao.cursor()
    query = "SELECT saldo FROM clientes WHERE id_cliente = %s"
    cursor.execute(query, (id_cliente,))
    resultado = cursor.fetchone()
    cursor.close()
    conexao.close()
    return resultado[0] if resultado else None

# Buscar saldo do cliente
def buscar_saldo_por_cliente(id_cliente):
    """Retorna o saldo atual do cliente."""
    conexao = conectar()
    cursor = conexao.cursor()
    query = "SELECT saldo FROM clientes WHERE id_cliente = %s"
    cursor.execute(query, (id_cliente,))
    resultado = cursor.fetchone()
    cursor.close()
    conexao.close()
    return resultado[0] if resultado else None

# Adicionar ou debitar saldo do cliente
def registrar_transacao(id_cliente, tipo, valor, id_base=None):
    """Registra uma transação de débito ou crédito no banco de dados."""
    conexao = conectar()
    cursor = conexao.cursor()
    # Atualizar saldo do cliente
    if tipo == "credito":
        atualizar_query = "UPDATE clientes SET saldo = saldo + %s WHERE id_cliente = %s"
    elif tipo == "debito":
        atualizar_query = "UPDATE clientes SET saldo = saldo + %s WHERE id_cliente = %s"
    else:
        print("Tipo de transação inválido.")
        return

    cursor.execute(atualizar_query, (valor, id_cliente))
    conexao.commit()

    # Registrar transação
    transacao_query = """
        INSERT INTO transacoes (id_cliente, tipo, valor, data, id_base)
        VALUES (%s, %s, %s, CURDATE(), %s)
    """
    cursor.execute(transacao_query, (id_cliente, tipo, valor, id_base))
    conexao.commit()
    print(f"Transação registrada com ID: {cursor.lastrowid}")
    cursor.close()
    conexao.close()

# Listar transações por cliente
def listar_transacoes_por_cliente(id_cliente):
    """Lista todas as transações realizadas por um cliente."""
    conexao = conectar()
    cursor = conexao.cursor()
    query = "SELECT * FROM transacoes WHERE id_cliente = %s"
    cursor.execute(query, (id_cliente,))
    resultados = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultados


# Registrar recarga no histórico de uso
def registrar_recarga(id_cliente, id_base, energia_utilizada, valor):
    """Registra uma recarga no histórico de uso e atualiza o saldo do cliente."""
    conexao = conectar()
    cursor = conexao.cursor()
    
    # Atualizar o saldo do cliente
    atualizar_saldo_query = "UPDATE clientes SET saldo = saldo - %s WHERE id_cliente = %s"
    cursor.execute(atualizar_saldo_query, (valor, id_cliente))
    conexao.commit()
    
    # Registrar a recarga no histórico de uso
    registrar_uso_query = """
        INSERT INTO historico_uso (id_cliente, id_base, data_uso, energia_utilizada, custo)
        VALUES (%s, %s, CURDATE(), %s, %s)
    """
    cursor.execute(registrar_uso_query, (id_cliente, id_base, energia_utilizada, valor))
    conexao.commit()
    
    print(f"Recarga registrada com sucesso! ID do histórico: {cursor.lastrowid}")
    cursor.close()
    conexao.close()

# Listar todos os clientes com seus saldos
def listar_clientes():
    """Lista todos os clientes cadastrados com seus respectivos saldos."""
    conexao = conectar()
    cursor = conexao.cursor()
    query = "SELECT id_cliente, nome, email, telefone, login, saldo FROM clientes"
    cursor.execute(query)
    clientes = cursor.fetchall()
    cursor.close()
    conexao.close()
    return clientes

# Listar todas as recargas registradas
def buscar_ultima_recarga():
    """Busca a última recarga realizada no banco de dados."""
    conexao = conectar()
    cursor = conexao.cursor()
    query = """
        SELECT h.id_uso, c.nome AS cliente, b.localizacao AS base, h.energia_utilizada, h.custo, h.data_uso
        FROM historico_uso h
        INNER JOIN clientes c ON h.id_cliente = c.id_cliente
        INNER JOIN bases_carregamento b ON h.id_base = b.id_base
        ORDER BY h.id_uso DESC LIMIT 1
    """
    cursor.execute(query)
    resultado = cursor.fetchone()
    cursor.close()
    conexao.close()
    if resultado:
        return {
            "id_recarga": resultado[0],
            "cliente": resultado[1],
            "base": resultado[2],
            "energia_utilizada": float(resultado[3]),
            "valor": float(resultado[4]),
            "data": resultado[5].strftime("%Y-%m-%d %H:%M:%S")
        }
    return None

# Listar recargas de um cliente específico
def listar_recargas_cliente(id_cliente):
    """Lista todas as recargas de um cliente específico."""
    conexao = conectar()
    cursor = conexao.cursor()
    query = """
        SELECT h.id_uso, b.localizacao AS base, h.energia_utilizada, h.custo, h.data_uso
        FROM historico_uso h
        INNER JOIN bases_carregamento b ON h.id_base = b.id_base
        WHERE h.id_cliente = %s
    """
    cursor.execute(query, (id_cliente,))
    recargas = cursor.fetchall()
    cursor.close()
    conexao.close()
    return recargas

# Listar todos os históricos de uso
def listar_todos_historicos_uso():
    """Lista o histórico de uso de energia de todos os clientes."""
    conexao = conectar()
    cursor = conexao.cursor()
    query = """
        SELECT h.id_uso, c.nome AS cliente, b.localizacao AS base, h.energia_utilizada, h.custo, h.data_uso
        FROM historico_uso h
        INNER JOIN clientes c ON h.id_cliente = c.id_cliente
        INNER JOIN bases_carregamento b ON h.id_base = b.id_base
    """
    cursor.execute(query)
    historicos = cursor.fetchall()
    cursor.close()
    conexao.close()
    return historicos

# Listar histórico de uso de um cliente específico
def listar_historico_uso(id_cliente):
    """Lista o histórico de uso de energia de um cliente específico."""
    conexao = conectar()
    cursor = conexao.cursor()
    query = """
        SELECT h.id_uso, b.localizacao AS base, h.energia_utilizada, h.custo, h.data_uso
        FROM historico_uso h
        INNER JOIN bases_carregamento b ON h.id_base = b.id_base
        WHERE h.id_cliente = %s
    """
    cursor.execute(query, (id_cliente,))
    historico = cursor.fetchall()
    cursor.close()
    conexao.close()
    return historico

def adicionar_transacao(id_cliente, tipo, valor, id_base=None):
    """
    Insere uma nova transação no banco de dados.
    """
    try:
        conn = conectar()  # Certifique-se de que esta função retorna uma conexão válida
        cursor = conn.cursor()

        # Inserir a transação no banco de dados
        cursor.execute("""
            INSERT INTO transacoes (id_cliente, tipo, valor, id_base, data)
            VALUES (%s, %s, %s, %s, NOW())
        """, (id_cliente, tipo, valor, id_base))

        # Atualizar saldo do cliente
        if tipo == "credito":
            cursor.execute("""
                UPDATE clientes
                SET saldo = saldo + %s
                WHERE id_cliente = %s
            """, (valor, id_cliente))
        elif tipo == "debito":
            cursor.execute("""
                UPDATE clientes
                SET saldo = saldo + %s
                WHERE id_cliente = %s
            """, (valor, id_cliente))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        raise Exception(f"Erro ao adicionar transação: {str(e)}")

def atualizar_saldo_cliente(id_cliente, novo_saldo):
    try:
        conn = conectar()
        cursor = conn.cursor()
        query = "UPDATE cliente SET saldo = %s WHERE id_cliente = %s"
        cursor.execute(query, (novo_saldo, id_cliente))
        conn.commit()
    except Exception as e:
        print("Erro ao atualizar saldo:", e)
    finally:
        cursor.close()
        conn.close()