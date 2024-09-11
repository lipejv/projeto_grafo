"""
Módulo principal.
"""

from pathlib import Path
import pandas as pd
import networkx as nx
from utils import formata_numero

PASTA_RAIZ = Path(__file__).parent
BASE_DE_DADOS = 'contratos.csv'
CAMINHO_CONTRATOS = PASTA_RAIZ / 'data' / BASE_DE_DADOS

df = pd.read_csv(CAMINHO_CONTRATOS, sep=';').dropna(axis=1, how='all')

# Removendo colunas que não irão ser úteis.
df.drop(columns=['NÚMERO DO CONTRATO', 'SITUAÇÃO',
                 'GRUPO DE OBJETO DE CONTRATAÇÃO',
                 'DATA PUBLICAÇÃO DOU', 'DATA ASSINATURA CONTRATO',
                 'ÓRGÃO / ENTIDADE VINCULADA CONTRATANTE',
                 'FORMA DE CONTRATAÇÃO'], inplace=True)

G = nx.MultiGraph()

# Criação do grafo.
for indice, linha in df.iterrows():
    orgao_contratante: str = linha['ORGÃO SUPERIOR CONTRATANTE']
    nome_empresa: str = linha['NOME DO FORNECEDOR']
    cnpj_cpf_empresa: str = linha['CPF / CNPJ DO FORNECEDOR']
    valor_contrato_str: str = linha['VALOR CONTRATADO']

    valor_contrato_str = formata_numero(valor_contrato_str)

    try:
        valor_contrato = float(valor_contrato_str)
    except ValueError:
        continue

    if valor_contrato < 0 or nome_empresa == 'Sigiloso':
        continue

    if nome_empresa not in G:
        G.add_node(nome_empresa, dado=cnpj_cpf_empresa)

    G.add_edge(orgao_contratante, nome_empresa, weight=valor_contrato)

# Criando arquivo para usar no Gephi.
nx.write_gexf(G, "grafo.gexf")

empresas = df['NOME DO FORNECEDOR'].unique()

# Calculando a centralidade, intermediação e proximidade de todos os vértices.
centralidade: dict = nx.degree_centrality(G)
intermediacao: dict = nx.betweenness_centrality(G)
proximidade: dict = nx.closeness_centrality(G)

# Pegando apenas as centralidades, intermediações e proximidades das empresas.
centralidade_empresas = {e: centralidade[e]
                         for e in empresas if e in centralidade}

intermediacao_empresas = {e: intermediacao[e]
                          for e in empresas if e in intermediacao}

proximidade_empresas = {e: proximidade[e]
                        for e in empresas if e in proximidade}

print("quantidade de empresas: ", len(empresas))

# Calculando as médias.
media_centralidade = sum(centralidade_empresas.values()
                         ) / len(centralidade_empresas)

media_intermediacao = sum(intermediacao_empresas.values()
                          ) / len(intermediacao_empresas)

media_proximidade = sum(proximidade_empresas.values()
                        ) / len(proximidade_empresas)

# Vendo as empresas que estão acima da média.
acima_media_centralidade = {e: p for e, p in centralidade_empresas.items()
                            if p > media_centralidade}

acima_media_intermediacao = {e: p for e, p in intermediacao_empresas.items()
                             if p > media_intermediacao}

acima_media_proximidade = {e: p for e, p in proximidade_empresas.items()
                           if p > media_proximidade}

print('quantidade empresas acima da media em centralidade: ',
      len(acima_media_centralidade))

print('quantidade empresas acima da media em intermediacao: ',
      len(acima_media_intermediacao))

print('quantidade empresas acima da media em proximidade: ',
      len(acima_media_proximidade))

# Intersecção das empresas que estão acima da média em centralidade, intermedia
# ção e proximidade.
empresas_resultantes_acima = set(acima_media_centralidade.keys()) & set(
    acima_media_intermediacao.keys()) & set(acima_media_proximidade.keys())

print('Quantidade empresas na intersecção: ',
      len((empresas_resultantes_acima)))

contratos_por_empresa = {}
for v1, v2 in G.edges():
    fornecedor = v1 if v1 in empresas else v2

    if fornecedor not in contratos_por_empresa:
        contratos_por_empresa[fornecedor] = 0
    contratos_por_empresa[fornecedor] += 1

# Ordenar pelo número de contratos, do maior para o menor
contratos_ordenados = sorted(
    contratos_por_empresa.items(), key=lambda x: x[1], reverse=True)

# Exibir resultados
print("\nEmpresas com mais contratos:")
for fornecedor, quantidade in contratos_ordenados:
    print(
        f"  - Fornecedor: {fornecedor}, Quantidade de contratos: {quantidade}")
