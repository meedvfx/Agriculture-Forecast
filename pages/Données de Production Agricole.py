import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Config Streamlit
st.set_page_config(page_title="🌾 Analyse Production Agricole", layout="centered")
st.title("🌍 Analyse de la Production Agricole au Maroc (2010–2022)")

# 📊 Source des données
st.markdown("""
📊 **Sources des données :**  
- [Data.gov.ma](https://data.gov.ma/data/fr/dataset/production-vegetale-2010-2022)  
- [Ministère de l’Agriculture](https://www.agriculture.gov.ma/)

🔍 **Données sur la production agricole (en tonnes) de cultures végétales au Maroc.**
""")

@st.cache_data  
def load_data(url):
    df = pd.read_csv(url)
    return df
# 📁 Chargement du dataset
df = load_data("data/dataarg.csv")  # Remplace par ton chemin réel

# 🧹 Prétraitement
df.columns = df.columns.str.strip().str.lower()
df['year'] = pd.to_datetime(df['year']).dt.year

# Renommer les colonnes pour simplifier
df = df.rename(columns={
    'filière': 'filiere',
    'production_tonnes': 'production'
})

# Affichage
st.subheader("📌 Aperçu des données")
st.dataframe(df.head())

# 🎯 Sélections utilisateur
produit_sel = st.selectbox("🌾 Sélectionnez un produit :", df['produit'].unique())
df_produit = df[df['produit'] == produit_sel]

# 📈 Évolution du produit sélectionné (matplotlib + seaborn)
st.subheader(f"📈 Évolution annuelle de la production : {produit_sel}")
fig, ax = plt.subplots()
sns.lineplot(data=df_produit, x='year', y='production', marker='o', ax=ax)
ax.set_xlabel("Année")
ax.set_ylabel("Production (Tonnes)")
ax.set_title(f"Production annuelle de {produit_sel}")
st.pyplot(fig)

# 📦 Distribution globale des productions (seaborn)
st.subheader("📊 Distribution des quantités produites (tous produits)")
fig2, ax2 = plt.subplots()
sns.histplot(df['production'], bins=30, kde=True, ax=ax2)
ax2.set_title("Distribution des productions (en tonnes)")
st.pyplot(fig2)

# 🏆 Top 10 produits les plus produits
st.subheader("🏆 Top 10 des produits les plus produits")
top10 = df.groupby("produit")['production'].sum().sort_values(ascending=False).head(10).reset_index()
fig3 = px.bar(top10, x='production', y='produit', orientation='h', color='production',
              title="Top 10 des produits agricoles par volume total")
st.plotly_chart(fig3)

# 📊 Évolution des 5 produits les plus importants
st.subheader("📈 Évolution de la production des principaux produits")
top5 = df.groupby("produit")['production'].sum().sort_values(ascending=False).head(5).index
df_top5 = df[df['produit'].isin(top5)]
fig4 = px.line(df_top5, x='year', y='production', color='produit',
               title="Évolution des 5 produits les plus importants")
st.plotly_chart(fig4)
