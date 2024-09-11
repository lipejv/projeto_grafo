import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from utils import formata_numero


PASTA_RAIZ = Path(__file__).parent
BASE_DE_DADOS = 'contratos.csv'
CAMINHO_CONTRATOS = PASTA_RAIZ / 'data' / BASE_DE_DADOS


df = pd.read_csv(CAMINHO_CONTRATOS, sep=';').dropna(axis=1, how='all')


df.drop(columns=['NÚMERO DO CONTRATO', 'SITUAÇÃO',
                 'GRUPO DE OBJETO DE CONTRATAÇÃO',
                 'DATA PUBLICAÇÃO DOU', 'DATA ASSINATURA CONTRATO',
                 'ÓRGÃO / ENTIDADE VINCULADA CONTRATANTE',
                 'FORMA DE CONTRATAÇÃO'], inplace=True)


G = nx.Graph()


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
        G.add_node(nome_empresa, tipo='empresa', dado=cnpj_cpf_empresa)

    if orgao_contratante not in G:
        G.add_node(orgao_contratante, tipo='orgao')

    G.add_edge(orgao_contratante, nome_empresa, weight=valor_contrato)


centralidade = nx.degree_centrality(G)
intermediacao = nx.betweenness_centrality(G)
proximidade = nx.closeness_centrality(G)


contratos_por_empresa = {}
for v1, v2 in G.edges():
    fornecedor = v1 if v1 in df['NOME DO FORNECEDOR'].unique() else v2
    if fornecedor not in contratos_por_empresa:
        contratos_por_empresa[fornecedor] = 0
    contratos_por_empresa[fornecedor] += 1

contratos_ordenados = sorted(contratos_por_empresa.items(), key=lambda x: x[1], reverse=True)
top_10_empresas = [empresa for empresa, _ in contratos_ordenados[:10]]

centralidade_top10 = {e: centralidade[e] for e in top_10_empresas if e in centralidade}
intermediacao_top10 = {e: intermediacao[e] for e in top_10_empresas if e in intermediacao}
proximidade_top10 = {e: proximidade[e] for e in top_10_empresas if e in proximidade}

def plot_metricas(metricas, titulo):
    empresas = list(metricas.keys())
    valores = list(metricas.values())
    
    plt.figure(figsize=(10, 6))
    x_pos = np.arange(len(empresas))
    
    plt.bar(x_pos, valores)
    plt.xticks(x_pos, empresas, rotation=45, ha='right', fontsize=10)
    plt.ylabel(titulo)
    plt.title(f'{titulo} das 10 Empresas com Mais Contratos')
    plt.tight_layout()
    plt.show()

plot_metricas(centralidade_top10, 'Centralidade')
plot_metricas(intermediacao_top10, 'Intermediação')
plot_metricas(proximidade_top10, 'Proximidade')
