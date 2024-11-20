from flask import Flask, request, jsonify
from crud import *
import re
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Variáveis globais para armazenar o último usuário cadastrado e logado
ultima_recarga_realizada = None
ultimo_usuario_cadastrado = None
ultimo_usuario_logado = None

# Endpoint para ver o último usuário cadastrado
@app.route('/api/cadastro', methods=['GET', 'POST'])
def cadastro():
    global ultimo_usuario_cadastrado

    if request.method == 'GET':
        # Retorna o último usuário cadastrado
        if ultimo_usuario_cadastrado:
            return jsonify({"ultimo_usuario_cadastrado": ultimo_usuario_cadastrado}), 200
        return jsonify({"mensagem": "Nenhum usuário cadastrado ainda."}), 404

    try:
        # Processa o cadastro (POST)
        dados = request.json
        nome = dados['nome']
        email = dados['email']
        telefone = dados['telefone']
        login = dados['login']
        senha = dados['senha']
        saldo = dados.get('saldo', 0.0)

        # Validações
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"erro": "Email inválido"}), 400
        if len(login) < 5 or len(senha) < 6:
            return jsonify({"erro": "Login ou senha não atendem os requisitos"}), 400

        inserir_cliente(nome, email, telefone, login, senha, saldo)

        # Atualiza o último usuário cadastrado
        ultimo_usuario_cadastrado = {
            "nome": nome,
            "email": email,
            "telefone": telefone,
            "login": login,
            "saldo": saldo
        }

        return jsonify({"mensagem": "Cadastro realizado com sucesso!"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Endpoint para ver o último usuário que fez login
@app.route('/api/login', methods=['GET', 'POST'])
def login():
    global ultimo_usuario_logado

    if request.method == 'GET':
        # Retorna o último usuário logado
        if ultimo_usuario_logado:
            return jsonify({"ultimo_usuario_logado": ultimo_usuario_logado}), 200
        return jsonify({"mensagem": "Nenhum usuário logado ainda."}), 404

    try:
        # Processa o login (POST)
        dados = request.json
        login = dados['login']
        senha = dados['senha']
        cliente = buscar_cliente_por_login(login, senha)

        if cliente:
            # Atualiza o último usuário logado
            ultimo_usuario_logado = {
                "id_cliente": cliente[0],
                "nome": cliente[1],
                "email": cliente[2],
                "telefone": cliente[3],
                "saldo": cliente[6]
            }
            return jsonify(ultimo_usuario_logado), 200
        else:
            return jsonify({"erro": "Login ou senha inválidos"}), 401
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/saldo/<int:id_cliente>', methods=['GET'])
def verificar_saldo(id_cliente):
    try:
        saldo = buscar_saldo_por_cliente(id_cliente)  # Retorna o saldo
        if saldo is not None:
            return jsonify({"saldo": float(saldo)}), 200  # Retorna saldo como JSON
        return jsonify({"erro": "Cliente não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/historico_transacoes/<int:id_cliente>', methods=['GET'])
def historico_transacoes(id_cliente):
    """Retorna o histórico de transações de recarga de um cliente específico."""
    try:
        historico = listar_transacoes_por_cliente(id_cliente)  # Consulta o banco de dados
        if historico:
            historico_formatado = [
                {
                    "id_transacao": transacao[0],
                    "tipo": transacao[2],
                    "valor": float(transacao[3]),
                    "data": transacao[4].strftime("%Y-%m-%d %H:%M:%S"),
                    "id_base": transacao[5] if len(transacao) > 5 else None
                } for transacao in historico
            ]
            return jsonify({"historico_transacoes": historico_formatado}), 200
        return jsonify({"mensagem": "Nenhuma transação encontrada."}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@app.route('/api/historico_transacoes/<int:id_cliente>', methods=['POST'])
def criar_transacao(id_cliente):
    try:
        dados = request.json
        tipo = dados.get("tipo")
        valor = dados.get("valor")
        id_base = dados.get("id_base")

        # Verificar campos obrigatórios
        if not tipo or valor is None:
            return jsonify({"erro": "Campos obrigatórios ausentes."}), 400

        # Buscar saldo atual do cliente
        saldo_atual = buscar_saldo_por_cliente(id_cliente)
        if saldo_atual is None:
            return jsonify({"erro": "Cliente não encontrado."}), 404

        # Atualizar saldo com base no tipo de transação
        novo_saldo = saldo_atual + valor 
      
        # Registrar a transação
        adicionar_transacao(id_cliente, tipo, valor, id_base)

        # Atualizar o saldo no banco de dados
        atualizar_saldo_cliente(id_cliente, novo_saldo)

        # Retornar a nova transação e saldo atualizado
        nova_transacao = {
            "id_cliente": id_cliente,
            "tipo": tipo,
            "valor": valor,
            "id_base": id_base,
            "data": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "saldo_atualizado": novo_saldo
        }
        return jsonify(nova_transacao), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    
@app.route('/api/abastecimento', methods=['POST'])
def abastecimento():
    try:
        # Dados recebidos do cliente
        dados = request.json
        id_cliente = dados['id_cliente']
        id_base = dados['id_base']
        energia_utilizada = float(dados['energia_utilizada'])
        custo = energia_utilizada * 0.30  # R$ 0.30 por kWh

        # Buscar saldo do cliente
        saldo = buscar_saldo_por_cliente(id_cliente)
        if saldo is None:
            return jsonify({"erro": "Cliente não encontrado."}), 404
        saldo = float(saldo)

        # Verificar se o saldo é suficiente
        if saldo < custo:
            return jsonify({"erro": "Saldo insuficiente para realizar o abastecimento."}), 400

        # Registrar recarga no banco de dados
        registrar_recarga(id_cliente, id_base, energia_utilizada, custo)

        return jsonify({
            "mensagem": "Abastecimento realizado com sucesso!",
            "energia_utilizada": energia_utilizada,
            "custo": custo,
            "saldo_restante": saldo - custo
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# Endpoint para listar o histórico de abastecimentos de um cliente
@app.route('/api/historico_abastecimento/<int:id_cliente>', methods=['GET'])
def historico_abastecimento(id_cliente):
    try:
        # Buscar histórico no banco de dados
        historico = listar_historico_uso(id_cliente)
        if historico:
            historico_formatado = [
                {
                    "id_uso": uso[0],
                    "id_base": uso[1],
                    "energia_utilizada": float(uso[2]),
                    "custo": float(uso[3]),
                    "data_uso": uso[4].strftime("%Y-%m-%d %H:%M:%S")
                }
                for uso in historico
            ]
            return jsonify({"historico_abastecimento": historico_formatado}), 200
        return jsonify({"mensagem": "Nenhum histórico de abastecimento encontrado."}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)