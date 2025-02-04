# -*- coding: utf-8 -*-
"""Submission-Collaborative-filtering-Diwa-Prasetyo-Proyek-2.ipynb


# Submission - Diwa Prasetyo

## Data Preprocessing

### Import Library
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity

"""### Mengimport dataset"""

data_url = 'https://github.com/DiwaPrasetyo02/submission-collaborative-filtering/raw/main/Online%20Retail.xlsx'
retail_data = pd.read_excel(data_url)

"""### Melihat info dataset"""

print(retail_data.shape)
print(retail_data.info())

"""### Melakukan Pembersihan data"""

cleaned_data = retail_data[retail_data['Quantity'] > 0]
cleaned_data = cleaned_data.dropna(subset=['CustomerID'])
cleaned_data.drop_duplicates(inplace=True)
cleaned_data.reset_index(drop=True, inplace=True)
cleaned_data.head()

"""### Melakukan Penyesuaian kolom"""

cleaned_data['InvoiceDate'] = pd.to_datetime(cleaned_data['InvoiceDate'])
cleaned_data['MonthYear'] = cleaned_data['InvoiceDate'].dt.to_period('M')

cleaned_data['TotalPrice'] = cleaned_data['Quantity'] * cleaned_data['UnitPrice']


numerical_features = cleaned_data[['Quantity', 'UnitPrice', 'TotalPrice']]

"""### Melakukan perubahan tipe data dan melihat rentang waktu transaksi"""

retail_data['InvoiceDate'] = pd.to_datetime(retail_data['InvoiceDate'])

start_date = retail_data['InvoiceDate'].min()
end_date = retail_data['InvoiceDate'].max()

start_date, end_date

"""### Visualisasi Jumlah Transaksi Tiap Negara
Grafik batang yang menunjukkan jumlah transaksi untuk setiap negara. Ini memberikan wawasan tentang negara mana yang memiliki jumlah transaksi terbanyak.
"""

plt.figure(figsize=(12, 6))
transactions_per_country = cleaned_data['Country'].value_counts()
sns.barplot(x=transactions_per_country.index, y=transactions_per_country.values, palette="viridis")
plt.title('Jumlah Transaksi per Negara')
plt.xlabel('Negara')
plt.ylabel('Jumlah Transaksi')
plt.xticks(rotation=90)
plt.show()

"""### Visualisasi Produk terlaris
Visualisasi ini memberikan wawasan tentang 10 produk mana yang paling populer di antara pelanggan. Ini bisa membantu dalam mengelola persediaan dan merencanakan strategi pemasaran untuk produk-produk yang paling laris.
"""

plt.figure(figsize=(12, 6))
top_products = cleaned_data['Description'].value_counts().head(10)
sns.barplot(x=top_products.values, y=top_products.index, palette="viridis")
plt.title('10 Produk Terlaris')
plt.xlabel('Jumlah Terjual')
plt.ylabel('Deskripsi Produk')
plt.show()

"""### Visualisasi Hubungan antara Jumlah Item dan Harga Satuan
hubungan antara jumlah item yang dibeli dan harga satuan. Sumbu x dan y menggunakan skala logaritmik untuk menangani rentang nilai yang luas. Ini dapat membantu mengidentifikasi pola atau anomali dalam data pembelian.
"""

plt.figure(figsize=(10, 6))
sns.scatterplot(data=cleaned_data, x='Quantity', y='UnitPrice', alpha=0.5)
plt.title('Hubungan antara Jumlah Item dan Harga Satuan')
plt.xlabel('Jumlah Item')
plt.ylabel('Harga Satuan')
plt.yscale('log')
plt.xscale('log')
plt.show()

"""### Visualisasi Jumlah Transaksi per Hari dalam Seminggu
Visualisasi ini membantu dalam memahami pola transaksi harian. Misalnya, apakah ada hari tertentu dalam seminggu di mana transaksi lebih banyak terjadi? Ini bisa membantu dalam pengambilan keputusan terkait promosi atau pengaturan stok.
"""

plt.figure(figsize=(12, 6))
cleaned_data['DayOfWeek'] = cleaned_data['InvoiceDate'].dt.day_name()
transactions_per_day = cleaned_data['DayOfWeek'].value_counts().reindex(
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
)
sns.barplot(x=transactions_per_day.index, y=transactions_per_day.values, palette="viridis")
plt.title('Jumlah Transaksi per Hari dalam Seminggu')
plt.xlabel('Hari dalam Seminggu')
plt.ylabel('Jumlah Transaksi')
plt.show()

"""### Visualisasi Heatmap Korelasi
Heatmap ini menunjukkan korelasi antara fitur-fitur numerik dalam dataset. Angka-angka dalam setiap sel menunjukkan nilai korelasi Pearson antara dua fitur. Warna pada heatmap menunjukkan kekuatan dan arah hubungan; merah tua menunjukkan korelasi positif yang kuat, biru tua menunjukkan korelasi negatif yang kuat, dan warna yang lebih terang menunjukkan korelasi yang lemah.
"""

# Compute the correlation matrix
correlation_matrix = numerical_features.corr()

# Plot the heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Heatmap Korelasi Fitur Numerik')
plt.show()

"""### Visualisasi Tren Pendapatan tiap Bulan
Membantu mengidentifikasi tren musiman dan fluktuasi pendapatan dari waktu ke waktu. Misalnya, apakah ada bulan-bulan tertentu dengan pendapatan yang lebih tinggi atau lebih rendah secara konsisten.
"""

# Calculate monthly revenue
monthly_revenue = cleaned_data.groupby('MonthYear')['TotalPrice'].sum()

# Plot the line chart
plt.figure(figsize=(12, 6))
monthly_revenue.plot(kind='line', marker='o', color='b')
plt.title('Tren Pendapatan per Bulan')
plt.xlabel('Bulan-Tahun')
plt.ylabel('Total Pendapatan')
plt.grid(True)
plt.show()

"""## Modeling

### Customer-Item Matrix
Membuat matriks yang disebut Customer-Item Matrix dari data yang sudah dibersihkan (cleaned_data)
"""

# Customer-Item Matrix
customer_item_df = cleaned_data.pivot_table(
    index='CustomerID',
    columns='StockCode',
    values='Quantity',
    aggfunc='sum'
)

customer_item_df = customer_item_df.applymap(lambda x: 1 if x > 0 else 0)

"""### Matriks similaritas antar pengguna
Menghitung matriks similaritas antar pengguna (user-user similarity) berdasarkan matriks Customer-Item yang telah dibuat sebelumnya (customer_item_df).

"""

# Modeling: User-User Similarity
user_similarity_matrix = pd.DataFrame(cosine_similarity(customer_item_df))
user_similarity_matrix.columns = customer_item_df.index
user_similarity_matrix['CustomerID'] = customer_item_df.index
user_similarity_matrix = user_similarity_matrix.set_index('CustomerID')

"""### Contoh menemukan preferensi pengguna yang mirip

Menemukan pengguna-pengguna yang mirip dengan pengguna dengan CustomerID 12350.0, berdasarkan matriks similaritas pengguna yang telah dihitung sebelumnya (user_similarity_matrix).


"""

# Example of finding similar users
similar_users = user_similarity_matrix.loc[12350.0].sort_values(ascending=False)
print(similar_users.head())

"""### Mengidentifikasi item-item yang dibeli oleh dua pengguna tertentu
Mengidentifikasi item-item yang dibeli oleh dua pengguna tertentu, yaitu pengguna dengan CustomerID 12350.0 dan 17935.0, dari matriks Customer-Item
`(customer_item_df)`.
"""

# Items bought by a specific user
items_bought_by_user_A = set(customer_item_df.loc[12350.0].iloc[customer_item_df.loc[12350.0].to_numpy().nonzero()].index)
items_bought_by_user_B = set(customer_item_df.loc[17935.0].iloc[customer_item_df.loc[17935.0].to_numpy().nonzero()].index)

"""### Merekomendasikan item-item yang dibeli oleh pengguna dengan CustomerID 12350.0

"""

# Items to recommend
recommended_items_for_B = items_bought_by_user_A - items_bought_by_user_B
print(cleaned_data.loc[cleaned_data['StockCode'].isin(recommended_items_for_B), ['StockCode', 'Description']].drop_duplicates().set_index('StockCode'))

"""### Menghitung matriks similaritas antar item (item-item similarity) berdasarkan matriks Customer-Item (customer_item_df)

"""

# Modeling: Item-Item Similarity
item_similarity_matrix = pd.DataFrame(cosine_similarity(customer_item_df.T))
item_similarity_matrix.columns = customer_item_df.T.index
item_similarity_matrix['StockCode'] = customer_item_df.T.index
item_similarity_matrix = item_similarity_matrix.set_index('StockCode')

"""### Menambahkan konstanta relevansi antar produk
Menambahkan nilai relevansi antar produk untuk memahami relevansi antar produk guna memberikan rekomendasi yang lebih tepat.

"""

# Relevansi Produk
def calculate_relevance(item_similarity, stock_code):
    similar_items = item_similarity.loc[stock_code].sort_values(ascending=False)
    relevance_constant = similar_items / similar_items.max()
    return relevance_constant

# Contoh menghitung relevansi produk dengan StockCode 23166
relevance_constants = calculate_relevance(item_similarity_matrix, 23166)
print(relevance_constants.head(10))

"""### Mencari 10 item paling mirip dengan item yang memiliki StockCode 23166 berdasarkan matriks similaritas item-item (item_similarity_matrix)

"""

# Finding top 10 similar items excluding 23166
top_similar_items = item_similarity_matrix.loc[23166].sort_values(ascending=False).iloc[1:11].index
print(cleaned_data.loc[cleaned_data['StockCode'].isin(top_similar_items), ['StockCode', 'Description']].drop_duplicates().set_index('StockCode').loc[top_similar_items])

"""### Menghitung nilai precision dan recall
Menghitung nilai precision dan recalldari sistem rekomendasi berbasis kolaboratif, dengan menggunakan matriks similaritas antar pengguna (user_similarity) dan matriks similaritas antar item (item_similarity).

"""

# Evaluation
def precision_recall_at_k(user_similarity, item_similarity, user_id, k=10):
    similar_users = user_similarity.loc[user_id].sort_values(ascending=False).iloc[1:k+1].index
    recommended_items = set()
    for similar_user in similar_users:
        recommended_items.update(customer_item_df.loc[similar_user].iloc[customer_item_df.loc[similar_user].to_numpy().nonzero()].index)

    bought_items = set(customer_item_df.loc[user_id].iloc[customer_item_df.loc[user_id].to_numpy().nonzero()].index)
    relevant_items = recommended_items & bought_items

    precision = len(relevant_items) / len(recommended_items) if recommended_items else 0
    recall = len(relevant_items) / len(bought_items) if bought_items else 0

    return precision, recall

# Evaluation with relevance
def precision_recall_with_relevance(user_similarity, item_similarity, user_id, k=10):
    similar_users = user_similarity.loc[user_id].sort_values(ascending=False).iloc[1:k+1].index
    recommended_items = set()
    for similar_user in similar_users:
        recommended_items.update(customer_item_df.loc[similar_user].iloc[customer_item_df.loc[similar_user].to_numpy().nonzero()].index)

    bought_items = set(customer_item_df.loc[user_id].iloc[customer_item_df.loc[user_id].to_numpy().nonzero()].index)
    relevant_items = recommended_items & bought_items

    relevance_scores = {item: item_similarity.loc[item].max() for item in relevant_items}
    precision = len(relevant_items) / len(recommended_items) if recommended_items else 0
    recall = len(relevant_items) / len(bought_items) if bought_items else 0

    return precision, recall, relevance_scores

user_id_example = 12350.0
precision, recall = precision_recall_at_k(user_similarity_matrix, item_similarity_matrix, user_id_example)
print(f'Precision: {precision:.2f}, Recall: {recall:.2f}')

# Evaluation including relevance
precision, recall, relevance_scores = precision_recall_with_relevance(user_similarity_matrix, item_similarity_matrix, user_id_example)
print('Relevance Scores:', relevance_scores)
