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


empresas = df['NOME DO FORNECEDOR'].unique()
centralidade_empresas = {e: centralidade[e] for e in empresas if e in centralidade}
intermediacao_empresas = {e: intermediacao[e] for e in empresas if e in intermediacao}
proximidade_empresas = {e: proximidade[e] for e in empresas if e in proximidade}


media_centralidade = sum(centralidade_empresas.values()) / len(centralidade_empresas)
media_intermediacao = sum(intermediacao_empresas.values()) / len(intermediacao_empresas)
media_proximidade = sum(proximidade_empresas.values()) / len(proximidade_empresas)


acima_media_centralidade = {e: p for e, p in centralidade_empresas.items() if p > media_centralidade}
acima_media_intermediacao = {e: p for e, p in intermediacao_empresas.items() if p > media_intermediacao}
acima_media_proximidade = {e: p for e, p in proximidade_empresas.items() if p > media_proximidade}

empresas_resultantes_acima = set(acima_media_centralidade.keys()) & set(acima_media_intermediacao.keys()) & set(acima_media_proximidade.keys())

G_filtrado = G.subgraph(set(empresas_resultantes_acima) | set(df['ORGÃO SUPERIOR CONTRATANTE'].unique()))

contratos_por_empresa = {}
for v1, v2 in G.edges():
    fornecedor = v1 if v1 in empresas else v2
    if fornecedor not in contratos_por_empresa:
        contratos_por_empresa[fornecedor] = 0
    contratos_por_empresa[fornecedor] += 1

contratos_ordenados = sorted(contratos_por_empresa.items(), key=lambda x: x[1], reverse=True)
top_10_empresas = [empresa for empresa, _ in contratos_ordenados[:10]]

G_final = G_filtrado.subgraph(set(top_10_empresas) | set(df['ORGÃO SUPERIOR CONTRATANTE'].unique()))

pos = {}
ministérios = [n for n, d in G_final.nodes(data=True) if d['tipo'] == 'orgao']
empresas = [n for n, d in G_final.nodes(data=True) if d['tipo'] == 'empresa']

angles = np.linspace(0, 2 * np.pi, len(ministérios), endpoint=False).tolist()
for angle, ministério in zip(angles, ministérios):
    pos[ministério] = (1.5 * np.cos(angle), 1.5 * np.sin(angle))

angles = np.linspace(0, 2 * np.pi, len(empresas), endpoint=False).tolist()
for angle, empresa in zip(angles, empresas):
    pos[empresa] = (np.cos(angle) * 0.8, np.sin(angle) * 0.8)  # Reduzir o círculo interno para ajustar espaçamento

plt.figure(figsize=(12, 12))
nx.draw(G_final, pos, with_labels=True, node_size=500, node_color='skyblue', edge_color='gray', alpha=0.7, width=1.0, font_size=6, font_weight='bold', connectionstyle='arc3,rad=0.1')

plt.title('Grafo das 10 Empresas com Mais Contratos e Seus Ministérios')
plt.show()
