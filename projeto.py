import pandas as pd 
from datasets import load_dataset
from transformers import pipeline

# 1. Ingestão escalável
# Em vez do download manual, usei a biblioteca "datasets" para streaming
print("A carregar dados de reviews (IMDb)...")
# Usei um dataset de 10k
reviews_ds = load_dataset("stanfordnlp/imdb", split='train', streaming=True)
reviews_sample = list(reviews_ds.take(100)) # 'take' permite lidar com Big Data por partes
df_reviews = pd.DataFrame(reviews_sample)

# 2. Carregamento de dados estrturados 
# Carregar o CSV do Kaggle
print("A carregar dados do Kaggle...")
df_comportamento = pd.read_csv('customer_segmentation_mixed.csv')

df_comportamento = pd.read_csv('customer_segmentation_mixed.csv')
print("Colunas encontradas no CSV:", df_comportamento.columns.tolist())

# 3. Pipeline de IA (Análise de Sentimentos)
print("A aplicar modelo de IA (NLP)")
# Usei um modelo leve para ser rápido e escalável
sentiment_model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Função para aplicar o modelo ao texto
def analisar_sentimento(texto):
    # Truncar para 512 caracteres para evitar erros de limite do modelo
    resultado = sentiment_model(texto[:512]) [0]
    return resultado['label']

df_reviews['sentimento_predito'] = df_reviews['text'].apply(analisar_sentimento)
 
# 4. Integração de fontes heterogéneas
print("A integrar datasets...")

# Criei uma coluna 'customer_id' baseada na posição (0, 1, 2...) em ambos os DataFrames
# Isso permite ligar o Cliente 1 do CSV à Review 1 da Amazon
df_comportamento = df_comportamento.reset_index().rename(columns={'index': 'customer_id'})
df_reviews['customer_id'] = range(len(df_reviews))

# Uni tudo num único repositório
df_final = pd.merge(df_comportamento, df_reviews, on='customer_id')

print("Integração concluída com sucesso!")
# Mostrar as primeiras linhas para confirmar que a idade e o sentimento estão na mesma tabela
print(df_final[['customer_id', 'Age', 'sentimento_predito']].head())

import sqlite3

# 5. Persistência (Data Warehouse)
print("A guardar dados no Data Warehouse...")
conn = sqlite3.connect('retail_warehouse.db')

# Guardar o df_final na tabela "perfil_clientes"
df_final.to_sql('perfil_clientes', conn, if_exists='replace', index=False)
conn.close()
print("Dados guardados no ficheiro: retail_warehouse.db")

# 6. Suporte à decisão (KPIs)
print("\n--- RELATÓRIO DE INSIGHTS ---")

# KPI1: Idade média por sentimento
idade_sentimento = df_final.groupby('sentimento_predito') ['Age'].mean()
print(f"Idade Média por sentimento:\n{idade_sentimento}")

# KPI2: Distribuição de sentimento po género
dist_genero = pd.crosstab(df_final['Gender'], df_final['sentimento_predito'])
print(f"\nDistribuição por género:\n{dist_genero}")

import matplotlib.pyplot as plt

# Criar um gráfico de barras de satisfação por género
dist_genero.plot(kind='bar', stacked=True, color=['#ff9999','#66b3ff'])
plt.title('Distribuição de sentimentos por género')
plt.xlabel('Género')
plt.ylabel('Número de clientes')
plt.legend(title='Sentimentos')
plt.show()

