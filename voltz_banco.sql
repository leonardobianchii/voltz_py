create database Voltz;
use Voltz;

-- Tabela bases_carregamento
CREATE TABLE bases_carregamento (
    id_base INT AUTO_INCREMENT PRIMARY KEY,
    localizacao VARCHAR(255) NOT NULL,
    capacidade_geracao DECIMAL(10, 2) NOT NULL,
    capacidade_armazenamento DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    data_instalacao DATE NOT NULL,
    tipo_conexao VARCHAR(50) NOT NULL
);
 
-- Tabela dados_consumo
CREATE TABLE dados_consumo (
    id_consumo INT AUTO_INCREMENT PRIMARY KEY,
    id_base INT NOT NULL,
    data DATE NOT NULL,
    energia_consumida DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_base) REFERENCES bases_carregamento(id_base)
);
 
-- Tabela dados_geracao
CREATE TABLE dados_geracao (
    id_geracao INT AUTO_INCREMENT PRIMARY KEY,
    id_base INT NOT NULL,
    data DATE NOT NULL,
    energia_gerada DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_base) REFERENCES bases_carregamento(id_base)
);
 
-- Tabela clientes
CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    telefone VARCHAR(20),
    login VARCHAR(50) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    saldo DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    data_cadastro DATE NOT NULL
);
 
-- Tabela historico_uso
CREATE TABLE historico_uso (
    id_uso INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_base INT NOT NULL,
    data_uso DATE NOT NULL,
    energia_utilizada DECIMAL(10, 2) NOT NULL,
    custo DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_base) REFERENCES bases_carregamento(id_base)
);
 
-- Tabela transacoes
CREATE TABLE transacoes (
    id_transacao INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    tipo ENUM('debito', 'credito') NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    data DATE NOT NULL,
    id_base INT,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_base) REFERENCES bases_carregamento(id_base)
);


INSERT INTO bases_carregamento (localizacao, capacidade_geracao, capacidade_armazenamento, status, data_instalacao, tipo_conexao)
VALUES
('São Paulo, SP', 500.00, 1000.00, 'Ativa', '2020-05-10', 'Trifásica'),
('Manaus, AM', 300.00, 800.00, 'Ativa', '2021-08-15', 'Monofásica'),
('Porto Alegre, RS', 450.00, 900.00, 'Ativa', '2019-03-20', 'Trifásica'),
('Rio de Janeiro, RJ', 400.00, 700.00, 'Manutenção', '2022-01-10', 'Bifásica'),
('Brasília, DF', 350.00, 850.00, 'Ativa', '2021-06-05', 'Monofásica'),
('Recife, PE', 500.00, 1100.00, 'Ativa', '2020-11-22', 'Trifásica'),
('Belo Horizonte, MG', 420.00, 950.00, 'Ativa', '2021-03-30', 'Bifásica'),
('Goiânia, GO', 300.00, 600.00, 'Manutenção', '2022-07-18', 'Monofásica'),
('Foz do Iguaçu, PR', 550.00, 1200.00, 'Ativa', '2020-09-12', 'Trifásica'),
('Belém, PA', 320.00, 750.00, 'Inativa', '2018-12-01', 'Bifásica');
