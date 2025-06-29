import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Config Streamlit
st.set_page_config(page_title="🌾 Analyse Production Agricole Maroc", layout="centered")
st.title("🌍 Analyse de la Production Agricole au Maroc (2010–2022)")
st.markdown("""
📊 **Sources des données**  
- [Data.gov.ma](https://data.gov.ma/data/fr/dataset/production-vegetale-2010-2022)  
- [Ministère de l’Agriculture](https://www.agriculture.gov.ma/)

🔍 **Ce jeu de données contient les quantités produites (en tonnes) de différentes cultures agricoles entre 2010 et 2022, réparties par région.**
""")

# Upload ou chargement local
df = pd.read_csv("data/dataarg.csv")  # ou st.file_uploader(...)

# Nettoyage simple
df = df.dropna()
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Affichage des infos de base
st.subheader("📌 Aperçu des données")
st.dataframe(df.head())

# Sélections dynamiques
produit_sel = st.selectbox("🌾 Sélectionnez un produit :", df['produit'].unique())
region_sel = st.selectbox("📍 Sélectionnez une région :", df['region'].unique())

# Filtrage
df_filtre = df[(df['produit'] == produit_sel) & (df['region'] == region_sel)]

# 📈 Évolution par Année (Matplotlib)
st.subheader("📈 Évolution de la production par année")
fig, ax = plt.subplots()
sns.lineplot(data=df_filtre, x="annee", y="quantite_produite", marker="o", ax=ax)
ax.set_title(f"Évolution de la production de {produit_sel} en {region_sel}")
ax.set_ylabel("Quantité (Tonnes)")
ax.set_xlabel("Année")
st.pyplot(fig)

# 📦 Distribution de la production (Seaborn)
st.subheader("📊 Distribution des productions agricoles")
fig2, ax2 = plt.subplots()
sns.histplot(data=df, x="quantite_produite", kde=True, bins=30, ax=ax2)
ax2.set_title("Distribution générale de la production (toutes cultures)")
st.pyplot(fig2)

# 🏆 Top 10 produits les plus produits
st.subheader("🏆 Top 10 des produits les plus produits")
top10 = df.groupby("produit")["quantite_produite"].sum().sort_values(ascending=False).head(10).reset_index()
fig3 = px.bar(top10, x="quantite_produite", y="produit", orientation="h", color="quantite_produite",
              title="Top 10 des cultures les plus produites")
st.plotly_chart(fig3)

# ⚖️ Comparaison entre deux régions
st.subheader("⚖️ Comparaison entre deux régions")
col1, col2 = st.columns(2)
with col1:
    r1 = st.selectbox("Région 1", df['region'].unique(), key="r1")
with col2:
    r2 = st.selectbox("Région 2", df['region'].unique(), key="r2")

df_comp = df[df['produit'] == produit_sel]
r1_data = df_comp[df_comp['region'] == r1].groupby("annee")["quantite_produite"].sum().reset_index()
r2_data = df_comp[df_comp['region'] == r2].groupby("annee")["quantite_produite"].sum().reset_index()

fig4 = go.Figure()
fig4.add_scatter(x=r1_data["annee"], y=r1_data["quantite_produite"], mode="lines+markers", name=r1)
fig4.add_scatter(x=r2_data["annee"], y=r2_data["quantite_produite"], mode="lines+markers", name=r2)
fig4.update_layout(title=f"Comparaison de la production de {produit_sel} entre {r1} et {r2}",
                   xaxis_title="Année", yaxis_title="Quantité (tonnes)")
st.plotly_chart(fig4)
