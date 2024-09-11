
Aqui irá conter informações e detalhes sobre o código e o objetivo do projeto.

# Base de Dados

A base de dados é um csv que possui os dados dos contratos federais feitos pelos ministérios.

Feito o download no portal da transparência.

# Objetivos

## Objetivo geral

Gerar um grafo em cima da base de dados e, com o grafo, usar algoritmos para encontrar possíveis esquemas de lavagem de dinheiro entre os orgãos superiores contratantes e as empresas/fornecedores de serviços ou produtos.

## Objetivo específico

Usar algoritmos específicos para verificar casos suspeitos de contratos nas relações entre os vértices (contratantes e fornecedores) e pesos das arestas. Assim, podendo ou não, indicar alguma possível fraude em contratos do governo federal.

# Estrutura do Grafo

## Vértices

- Orgãos superiores contratantes (nome);
- Empresas/fornecedores (nome da empresa ou pessoa), atributo: CPF ou CNPJ.

## Arestas

Indica um contrato entre uma empresa e um orgão.

## Pesos das arestas

Valor do contrato em reais.

# Código

