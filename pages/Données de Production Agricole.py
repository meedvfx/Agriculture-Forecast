import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Config Streamlit
st.set_page_config(page_title="Analyse Production Agricole", layout="centered", page_icon="data:image/svg+xml,%3csvg stroke-width='1.75' xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3e%3cdefs%3e%3cstyle%3e.cls-4lkznqm1cnq5lcsl5h990v-1%7bfill:none%3bstroke:%23FC0F0F%3bstroke-miterlimit:10%3b%3b%7d%3c/style%3e%3c/defs%3e%3cg id='roll_brush' data-name='roll brush'%3e%3cpath class='cls-4lkznqm1cnq5lcsl5h990v-1' d='M22.51 4.36c0 .87-1.38 1.63-3.58 2.16a30.79 30.79 0 0 1-7 .72 30.89 30.89 0 0 1-7-.72C2.79 6 1.41 5.23 1.41 4.36c0-1.59 4.73-2.87 10.59-2.87s10.51 1.28 10.51 2.87Z'/%3e%3cpath class='cls-4lkznqm1cnq5lcsl5h990v-1' d='M22.51 4.36V12c0 .86-1.38 1.63-3.58 2.15a30.23 30.23 0 0 1-7 .72 30.32 30.32 0 0 1-7-.72C2.79 13.67 1.41 12.9 1.41 12V4.36C1.41 5.23 2.79 6 5 6.52a30.89 30.89 0 0 0 7 .72 30.79 30.79 0 0 0 7-.72c2.13-.52 3.51-1.29 3.51-2.16Z'/%3e%3cpath class='cls-4lkznqm1cnq5lcsl5h990v-1' d='M22.51 12v7.67c0 .86-1.38 1.63-3.58 2.16a30.79 30.79 0 0 1-7 .72 30.89 30.89 0 0 1-7-.72c-2.19-.53-3.57-1.3-3.57-2.16V12c0 .86 1.38 1.63 3.57 2.15a30.32 30.32 0 0 0 7 .72 30.23 30.23 0 0 0 7-.72c2.2-.48 3.58-1.25 3.58-2.15Z'/%3e%3cline class='cls-4lkznqm1cnq5lcsl5h990v-1' x1='11' y1='11.08' x2='12.92' y2='11.08'/%3e%3cline class='cls-4lkznqm1cnq5lcsl5h990v-1' x1='14.83' y1='11.08' x2='16.75' y2='11.08'/%3e%3cline class='cls-4lkznqm1cnq5lcsl5h990v-1' x1='7.16' y1='11.08' x2='9.08' y2='11.08'/%3e%3cline class='cls-4lkznqm1cnq5lcsl5h990v-1' x1='11' y1='18.75' x2='12.92' y2='18.75'/%3e%3cline class='cls-4lkznqm1cnq5lcsl5h990v-1' x1='14.83' y1='18.75' x2='16.75' y2='18.75'/%3e%3cline class='cls-4lkznqm1cnq5lcsl5h990v-1' x1='7.16' y1='18.75' x2='9.08' y2='18.75'/%3e%3c/g%3e%3c/svg%3e")
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
df = load_data("data/dataagr.csv")  # Remplace par ton chemin réel

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
st.dataframe(df.head(), hide_index=None)

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
