from crud import *
from app import *
import re
import requests

BASE_URL = "http://127.0.0.1:5000/api"  

def menu_principal():
    while True:
        print("\nBem-vindo à Voltz!")
        print("1. Cadastre-se")
        print("2. Faça login")
        print("3. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastro_cliente()
        elif opcao == "2":
            login_cliente()
        elif opcao == "3":
            print("Obrigado por utilizar o sistema Voltz. Até mais!")
            break
        else:
            print("Opção inválida. Tente novamente.")

def cadastro_cliente():
    print("\nCADASTRO DE CLIENTE")
    nome = input("Nome completo: ")
    email = input("Email (exemplo@dominio.com): ")
    while not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        print("Email inválido. Tente novamente.")
        email = input("Email (exemplo@dominio.com): ")

    telefone = input("Telefone (formato: (xx)xxxxx-xxxx): ")
    while not re.match(r"\(\d{2}\)\d{4,5}-\d{4}", telefone):
        print("Telefone inválido. Tente novamente.")
        telefone = input("Telefone (formato: (xx)xxxxx-xxxx): ")

    login = input("Login (mínimo 5 caracteres): ")
    while len(login) < 5:
        print("O login deve ter pelo menos 5 caracteres.")
        login = input("Login: ")

    senha = input("Senha (mínimo 6 caracteres): ")
    while len(senha) < 6:
        print("A senha deve ter pelo menos 6 caracteres.")
        senha = input("Senha: ")

    saldo = float(input("Saldo inicial (R$): "))

    payload = {
        "nome": nome,
        "email": email,
        "telefone": telefone,
        "login": login,
        "senha": senha,
        "saldo": saldo,
    }

    try:
        response = requests.post(f"{BASE_URL}/cadastro", json=payload)
        if response.status_code == 201:
            print("Cadastro realizado com sucesso!")
        else:
            print(f"Erro ao realizar cadastro: {response.json().get('erro')}")
    except Exception as e:
        print(f"Erro ao conectar com o servidor: {e}")

def login_cliente():
    print("\nLOGIN")
    login = input("Digite seu login: ")
    senha = input("Digite sua senha: ")

    payload = {"login": login, "senha": senha}

    try:
        response = requests.post(f"{BASE_URL}/login", json=payload)
        if response.status_code == 200:
            cliente = response.json()
            print(f"Bem-vindo(a), {cliente['nome']}!")
            menu_cliente(cliente["id_cliente"])
        else:
            print(f"Erro no login: {response.json().get('erro')}")
    except Exception as e:
        print(f"Erro ao conectar com o servidor: {e}")

def menu_cliente(id_cliente):
    while True:
        print("\nMENU DO CLIENTE")
        print("1. Ver saldo")
        print("2. Carregar saldo")
        print("3. Ver histórico de recargas")
        print("4. Ver histórico de uso")
        print("5. Iniciar abastecimento")
        print("6. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            verificar_saldo(id_cliente)
        elif opcao == "2":
            tipo_transacao = input("Tipo de transação ('debito' ou 'credito'): ").lower()
            valor = float(input("Valor da transação (R$): "))
            id_base = input("Digite o ID da base (ou deixe vazio): ")
            id_base = int(id_base) if id_base else None
            registrar_transacao(id_cliente, tipo_transacao, valor, id_base)
            print("Transação registrada com sucesso!")
        elif opcao == "3":
           verificar_historico_transacoes(id_cliente)
        elif opcao == "4":
            historico = listar_historico_uso(id_cliente)
            if historico:
                print("\nHISTÓRICO DE USO:")
                for uso in historico:
                     print(
                f"ID do Uso: {uso[0]} | Base: {uso[1]} | "
                f"Data: {uso[4].strftime('%d/%m/%Y')} | "
                f"Energia Utilizada: {float(uso[2]):.2f} kWh | "
                f"Custo: R$ {float(uso[3]):.2f}"
            )
            else:
                print("Nenhum histórico de uso encontrado.")
        elif opcao == "5":
            iniciar_abastecimento(id_cliente)
        elif opcao == "6":
            break
        else:
            print("Opção inválida. Tente novamente.")


def verificar_saldo(id_cliente):
    try:
        response = requests.get(f"{BASE_URL}/saldo/{id_cliente}")
        if response.status_code == 200:
            saldo = response.json()["saldo"]
            saldo = float(saldo)
            print(f"Seu saldo atual: R$ {saldo:.2f}")
        else:
            print(f"Erro ao buscar saldo: {response.json().get('erro')}")
    except Exception as e:
        print(f"Erro ao conectar com o servidor: {e}")

def iniciar_abastecimento(id_cliente):
    """
    Realiza o abastecimento de energia conforme a quantidade de kWh solicitada pelo cliente.
    """
    print("\nINICIAR ABASTECIMENTO")
    custo_por_kwh = 0.30

    try:
        response = requests.get(f"{BASE_URL}/saldo/{id_cliente}")
        if response.status_code != 200:
            print(f"Erro ao buscar saldo: {response.json().get('erro')}")
            return
        saldo = float(response.json()["saldo"])
    except Exception as e:
        print(f"Erro ao conectar com o servidor para buscar saldo: {e}")
        return

    print(f"Saldo disponível: R$ {saldo:.2f}")

    try:
        energia_desejada = float(input("Digite a quantidade de kWh que deseja recarregar: "))
        custo_abastecimento = energia_desejada * custo_por_kwh

        print(f"O custo para {energia_desejada:.2f} kWh será de R$ {custo_abastecimento:.2f}")

        if saldo < custo_abastecimento:
            print("Saldo insuficiente para realizar o abastecimento.")
            return

        confirmacao = input("Deseja prosseguir com o abastecimento? (s/n): ").lower()
        if confirmacao != 's':
            print("Abastecimento cancelado.")
            return

        id_base = int(input("Digite o ID da base de carregamento: "))

        payload = {
            "id_cliente": id_cliente,
            "id_base": id_base,
            "valor": custo_abastecimento,
            "energia_utilizada": energia_desejada
        }

        response = requests.post(f"{BASE_URL}/abastecimento", json=payload)
        if response.status_code == 200:
            dados = response.json()
            print("\nABASTECIMENTO CONCLUÍDO!")
            print(f"Você utilizou: {float(dados['energia_utilizada']):.2f} kWh")
            print(f"Custo do abastecimento: R$ {float(dados['custo']):.2f}")
            print(f"Saldo restante: R$ {float(dados['saldo_restante']):.2f}")
        else:
            print(f"Erro ao registrar abastecimento: {response.json().get('erro')}")
    except ValueError:
        print("Por favor, insira um valor numérico válido.")
    except Exception as e:
        print(f"Erro ao conectar com o servidor: {e}")
   

def verificar_historico_transacoes(id_cliente):
    try:
        response = requests.get(f"{BASE_URL}/historico_transacoes/{id_cliente}")
        if response.status_code == 200:
            historico = response.json()["historico_transacoes"]
            print("\nHISTÓRICO DE RECARGAS:")
            for transacao in historico:
                print(
                    f"ID: {transacao['id_transacao']}, "
                    f"Tipo: {transacao['tipo']}, "
                    f"Valor: R$ {transacao['valor']:.2f}, "
                    f"Data: {transacao['data']}, "
                    f"ID Base: {transacao['id_base']}"
                )
        else:
            print(f"Erro ao buscar histórico: {response.json().get('mensagem')}")
    except Exception as e:
        print(f"Erro ao conectar com o servidor: {e}")


if __name__ == "__main__":
    menu_principal()
