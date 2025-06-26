# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 15:41:11 2025

@author: meedz
"""

##########################

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


##Variables#####################

image = 'C:/Users/meedz/Desktop/Stage/site/data/logo.jpg'


@st.cache_data  
def load_data(url):
    df = pd.read_csv(url)
    return df

###################################################

st.set_page_config(page_title="Description des Données", layout="centered", page_icon="data:image/svg+xml,%3csvg stroke-width='1.75' xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3e%3cdefs%3e%3cstyle%3e.cls-4lkznqm1cnq5lcsl5h990v-1%7bfill:none%3bstroke:%23FC0F0F%3bstroke-miterlimit:10%3b%3b%7d%3c/style%3e%3c/defs%3e%3cg id='roll_brush' data-name='roll brush'%3e%3cpath class='cls-4lkznqm1cnq5lcsl5h990v-1' d='M22.51 4.36c0 .87-1.38 1.63-3.58 2.16a30.79 30.79 0 0 1-7 .72 30.89 30.89 0 0 1-7-.72C2.79 6 1.41 5.23 1.41 4.36c0-1.59 4.73-2.87 10.59-2.87s10.51 1.28 10.51 2.87Z'/%3e%3cpath class='cls-4lkznqm1cnq5lcsl5h990v-1' d='M22.51 4.36V12c0 .86-1.38 1.63-3.58 2.15a30.23 30.23 0 0 1-7 .72 30.32 30.32 0 0 1-7-.72C2.79 13.67 1.41 12.9 1.41 12V4.36C1.41 5.23 2.79 6 5 6.52a30.89 30.89 0 0 0 7 .72 30.79 30.79 0 0 0 7-.72c2.13-.52 3.51-1.29 3.51-2.16Z'/%3e%3cpath class='cls-4lkznqm1cnq5lcsl5h990v-1' d='M22.51 12v7.67c0 .86-1.38 1.63-3.58 2.16a30.79 30.79 0 0 1-7 .72 30.89 30.89 0 0 1-7-.72c-2.19-.53-3.57-1.3-3.57-2.16V12c0 .86 1.38 1.63 3.57 2.15a30.32 30.32 0 0 0 7 .72 30.23 30.23 0 0 0 7-.72c2.2-.48 3.58-1.25 3.58-2.15Z'/%3e%3cline class='cls-4lkznqm1cnq5lcsl5h990v-1' x1='11' y1='11.08' x2='12.92' y2='11.08'/%3e%3cline class='cls-4lkznqm1cnq5lcsl5h990v-1' x1='14.83' y1='11.08' x2='16.75' y2='11.08'/%3e%3cline class='cls-4lkznqm1cnq5lcsl5h990v-1' x1='7.16' y1='11.08' x2='9.08' y2='11.08'/%3e%3cline class='cls-4lkznqm1cnq5lcsl5h990v-1' x1='11' y1='18.75' x2='12.92' y2='18.75'/%3e%3cline class='cls-4lkznqm1cnq5lcsl5h990v-1' x1='14.83' y1='18.75' x2='16.75' y2='18.75'/%3e%3cline class='cls-4lkznqm1cnq5lcsl5h990v-1' x1='7.16' y1='18.75' x2='9.08' y2='18.75'/%3e%3c/g%3e%3c/svg%3e")




# Titre de l'application
st.title("🌍 Analyse des Prix des Produits & Services au Maroc (2017-2024)")

# Chargement des données
df = load_data("C:/Users/meedz/Desktop/Stage/site/data/dataset.csv")

st.divider()

st.markdown("### 📊 Source des Données :")
col1, col2 = st.columns(2)
with col1:
    st.markdown("- [Data.gov.ma](https://data.gov.ma/data/fr/dataset/data_7_5) (Open Data Maroc)")
with col2:
    st.markdown("- [Haut-Commissariat au Plan (HCP)](https://www.hcp.ma/) (Données officielles)")

st.divider()



st.markdown('# 🔍 Description du Dataset')
st.markdown("Ce dataset contient l'**évolution des prix** des produits et services dans **plusieurs villes marocaines** entre **2017 et 2024**.")



st.markdown('# 🏙️ Villes Couvertes')


villes_data = {
    "Grandes Villes": ["🏙️ Casablanca", "🏛️ Rabat", "🌆 Marrakech", "🏖️ Agadir"],
    "Villes Moyennes": ["🕌 Fès", "🏰 Meknès", "⚓ Tanger", "🏘️ Kénitra"],
    "Villes du Sud": ["🏜️ Laâyoune", "🏝️ Dakhla", "🏞️ Guelmim", "🏔️ Errachidia"]
}

st.dataframe(data = villes_data, hide_index = None)


st.markdown('# 📈 Structure des Données')


structure_data = {
    "Colonne": ["📍 Ville", "🛒 Produits", "📅 Date", "💰 Prix"],
    "Description": ["Nom de la ville", "Catégorie", "Mois/Année", "Indice (base 100)"],
    "Exemple": ['"Casablanca"', '"PAIN ET CEREALES"', '"2018-01-01"', '102.5']
}

st.dataframe(data = structure_data, hide_index = None)


st.markdown('# 📌 Catégories Principales')

categories_data = {
    "🍎 Alimentation": ["Pain & Céréales", "Viande & Poisson", "Fruits & Légumes"],
    "🏠 Logement": ["Loyers", "Électricité", "Eau/Gaz"],
    "🚗 Transport": ["Carburants", "Transports", "Réparations"],
    "🏥 Santé": ["Médicaments", "Hôpitaux", "Dentistes"],
    "🎓 Éducation": ["Primaire", "Secondaire", "Supérieur"]
}

st.dataframe(data = categories_data, hide_index = None)

st.divider()

st.markdown('# 📊 Visualisation ')




st.header("📦 Distribution des prix")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df['Prix'], bins=30, kde=True, ax=ax)
ax.set_title('Distribution des Prix')
st.pyplot(fig)


st.divider()
 

st.header("🏙️ Prix moyens par ville")
plt.figure(figsize=(12, 6))
price_by_city = df.groupby('Villes')['Prix'].mean().sort_values(ascending=False)
sns.barplot(x=price_by_city.index, y=price_by_city.values)
plt.xticks(rotation=45)
plt.title('Prix Moyens par Ville')
plt.ylabel('Prix Moyen')
st.pyplot(plt)

st.divider()


st.header("💰 Top 10 des produits les plus chers")
top_expensive = df.groupby('Produits')['Prix'].mean().nlargest(10)
plt.figure(figsize=(12, 6))
sns.barplot(x=top_expensive.values, y=top_expensive.index)
plt.title('Top 10 des Produits les Plus Chers')
plt.xlabel('Prix Moyen')
st.pyplot(plt)

st.divider()


st.header("⚖️ Comparaison des prix entre deux villes")
df['Année'] = pd.to_datetime(df['Date']).dt.year

city1 = st.selectbox('Ville 1', df['Villes'].unique())
city2 = st.selectbox('Ville 2', df['Villes'].unique(), index=1 if 'Marrakech' in df['Villes'].unique() else 0)
if city1 and city2:
    df_filtered = df[df['Villes'].isin([city1, city2])]
    
    # Création du graphique d'évolution par année
    plt.figure(figsize=(12, 6))
    
    # Utilisation de lineplot pour les tendances temporelles
    sns.lineplot(data=df_filtered, x='Année', y='Prix', hue='Villes',
                 style='Villes', markers=True, dashes=False,
                 palette=['#1f77b4', '#ff7f0e'])  # Couleurs bleu et orange
    
    # Améliorations du graphique
    plt.title(f'Évolution des Prix entre {city1} et {city2} par Année')
    plt.xlabel('Année')
    plt.ylabel('Prix')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    years = sorted(df_filtered['Année'].unique())
    plt.xticks(years)
    
    st.pyplot(plt)



st.title("📈 Évolution du Prix par Année")



df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['year'] = df['Date'].dt.year

# ----------------- Sélection Produit -----------------
produits_disponibles = df['Produits'].unique().tolist()

produit_choisi = st.selectbox("Sélectionnez un produit :", produits_disponibles)

# ----------------- Filtrage et Affichage -----------------
df_filtre = df[df['Produits'] == produit_choisi]

if df_filtre.empty:
    st.warning("Aucune donnée pour ce produit.")
else:
    prix_par_annee = df_filtre.groupby('year')['Prix'].mean().reset_index()

    fig, ax = plt.subplots()
    sns.lineplot(data=prix_par_annee, x='year', y='Prix', marker='o', ax=ax)
    ax.set_title(f"Évolution du prix de {produit_choisi} par année")
    ax.set_xlabel("Année")
    ax.set_ylabel("Prix moyen (MAD)")
    ax.grid(True)

    st.pyplot(fig)
























